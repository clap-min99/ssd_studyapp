"""Account-scoped daily review queues and resumable progress."""
import random
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Trim
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ReviewPreferences, ReviewRecord, ReviewSession, Tag, Term
from .serializers import DueTermSerializer


class SessionInput(serializers.Serializer):
    daily_goal = serializers.ChoiceField(choices=[5, 10, 20], default=10)
    category = serializers.ChoiceField(choices=["", "ssd", "automotive"], default="")
    tag = serializers.SlugField(required=False, allow_blank=True, default="")
    date = serializers.DateField(required=False, allow_null=True, default=None)
    weak_only = serializers.BooleanField(default=False)
    mode = serializers.ChoiceField(choices=["written", "choice"], default="written")
    extra = serializers.BooleanField(default=False)

    def validate_tag(self, value):
        if value and not Tag.objects.filter(slug=value).exists():
            raise serializers.ValidationError("존재하지 않는 주제입니다.")
        return value


def progress(user):
    sessions = ReviewSession.objects.filter(user=user, date=timezone.localdate())
    completed, learned = set(), set()
    for session in sessions:
        completed.update(session.completed_ids)
        learned.update(set(session.new_term_ids) & set(session.completed_ids))
    return completed, learned


def session_data(user, session=None):
    prefs, _ = ReviewPreferences.objects.get_or_create(user=user)
    completed, learned = progress(user)
    result = {"daily_goal": prefs.daily_goal, "completed_today": len(completed), "new_today": len(learned), "session": None}
    if session:
        terms = Term.objects.filter(pk__in=session.term_ids).prefetch_related("tags")
        by_id = {term.pk: term for term in terms}
        ordered = [by_id[pk] for pk in session.term_ids if pk in by_id]
        cards = DueTermSerializer(ordered, many=True).data
        # 객관식 후보는 문제마다 재조회하지 않고 주제별로 한 번만 가져온다.
        topic_meanings = {}
        fallback = []
        if session.mode == "choice" and ordered:
            meanings = (Term.objects.order_by().annotate(candidate_meaning=Trim("meaning"))
                .exclude(candidate_meaning="").values_list("candidate_meaning", flat=True).distinct())
            slugs = {tag.slug for term in ordered for tag in term.tags.all()}
            for slug in slugs:
                topic_meanings[slug] = list(meanings.filter(tags__slug=slug)[:30])
            fallback = list(meanings[:100])
        for card, term in zip(cards, ordered):
            card["tags"] = [tag.slug for tag in term.tags.all()]
            card["is_new"] = term.pk in session.new_term_ids
            card["meaning"] = term.meaning.strip()
            card["options"] = [card["meaning"]]
            if session.mode != "choice":
                continue
            related = [value for slug in card["tags"] for value in topic_meanings.get(slug, [])]
            preferred = list(dict.fromkeys(value.strip() for value in related if value.strip() and value.strip() != term.meaning.strip()))
            random.shuffle(preferred)
            decoys = preferred[:3]
            if len(decoys) < 3:
                shuffled_fallback = random.sample(fallback, len(fallback))
                for value in shuffled_fallback:
                    value = value.strip()
                    if value and value != term.meaning.strip() and value not in decoys:
                        decoys.append(value)
                    if len(decoys) >= 3:
                        break
            card["meaning"] = term.meaning.strip()
            card["options"] = [card["meaning"], *decoys]
            random.shuffle(card["options"])
        result["session"] = {
            "id": session.pk, "terms": cards, "completed_ids": session.completed_ids,
            "scope": session.scope, "mode": session.mode,
        }
    return result


class ReviewSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = ReviewSession.objects.filter(user=request.user, date=timezone.localdate()).first()
        return Response(session_data(request.user, session))

    def post(self, request):
        serializer = SessionInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        options = serializer.validated_data
        today = timezone.localdate()
        with transaction.atomic():
            # Serialize queue creation and answers for this account.
            get_user_model().objects.select_for_update().get(pk=request.user.pk)
            prefs, _ = ReviewPreferences.objects.get_or_create(user=request.user)
            prefs.daily_goal = options["daily_goal"]
            prefs.save(update_fields=["daily_goal"])
            completed, learned = progress(request.user)
            terms = Term.objects.exclude(meaning="").exclude(pk__in=completed)
            if options["category"]:
                terms = terms.filter(tags__category=options["category"])
            if options["tag"]:
                terms = terms.filter(tags__slug=options["tag"])
            if options["date"]:
                terms = terms.filter(Q(appeared_in__date=options["date"]) | Q(first_seen_digest__date=options["date"]))
            records = {record.term_id: record for record in ReviewRecord.objects.filter(user=request.user)}
            due, new = [], []
            for term in terms.distinct():
                if not term.meaning.strip():
                    continue
                record = records.get(term.pk)
                if record is None:
                    if not options["weak_only"]:
                        new.append(term.pk)
                elif options["weak_only"]:
                    if record.familiarity != "mastered":
                        due.append((record.next_review_date, term.pk))
                elif record.next_review_date <= today:
                    due.append((record.next_review_date, term.pk))
            count = 5 if options["extra"] else max(0, prefs.daily_goal - len(completed))
            selected = [pk for _, pk in sorted(due)][:count]
            selected_new = new[:min(max(0, count - len(selected)), max(0, 3 - len(learned)))]
            scope = {key: (str(value) if key == "date" and value else value)
                     for key, value in options.items() if key in ("category", "tag", "date", "weak_only")}
            session = ReviewSession.objects.create(
                user=request.user, date=today, term_ids=selected + selected_new,
                new_term_ids=selected_new, scope=scope, mode=options["mode"],
            )
        return Response(session_data(request.user, session), status=201)
