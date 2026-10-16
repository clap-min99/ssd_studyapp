from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from digest.models import DailyDigest, ReviewPreferences, ReviewRecord, ReviewSession, Tag, Term


class ReviewSessionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="learner")
        self.other = get_user_model().objects.create_user(username="other")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.today = timezone.localdate()
        self.tag = Tag.objects.create(slug="nand", name="NAND", category="ssd")
        self.auto = Tag.objects.create(slug="can", name="CAN", category="automotive")
        self.digest = DailyDigest.objects.create(date=self.today, subject="today", raw_text="")
        self.terms = []
        for i in range(12):
            term = Term.objects.create(term=f"Term {i:02}", meaning=f"Meaning {i}", first_seen_digest=self.digest)
            term.tags.add(self.tag if i < 10 else self.auto)
            self.terms.append(term)
        for i in range(5):
            ReviewRecord.objects.create(user=self.user, term=self.terms[i],
                next_review_date=self.today - timedelta(days=5-i))

    def start(self, **settings):
        response = self.client.post("/api/review/session/", {"daily_goal": 10, **settings}, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def answer(self, session, term_id, **extra):
        return self.client.post(f"/api/review/{term_id}/answer/", {
            "familiarity": "mastered", "session_id": session["id"], **extra,
        }, format="json")

    def test_overdue_first_and_only_three_new_terms(self):
        data = self.start()
        cards = data["session"]["terms"]
        self.assertEqual([card["id"] for card in cards[:5]], [term.pk for term in self.terms[:5]])
        self.assertEqual(len(cards), 8)
        self.assertEqual(sum(card["is_new"] for card in cards), 3)
        self.assertTrue(all(len(card["options"]) == len(set(card["options"])) for card in cards))
        self.assertTrue(all(card["meaning"] in card["options"] for card in cards))

    def test_resume_and_duplicate_answer_do_not_double_count(self):
        session = self.start(daily_goal=5)["session"]
        pk = session["terms"][0]["id"]
        self.assertEqual(self.answer(session, pk).status_code, 200)
        record = ReviewRecord.objects.get(user=self.user, term_id=pk)
        interval = record.interval_days
        self.assertEqual(self.answer(session, pk).status_code, 200)
        record.refresh_from_db()
        self.assertEqual(record.interval_days, interval)
        data = self.client.get("/api/review/session/").data
        self.assertEqual(data["completed_today"], 1)
        self.assertEqual(data["session"]["completed_ids"], [pk])
        self.assertEqual(data["daily_goal"], 5)

    def test_daily_limit_and_extra_five_respect_new_cap(self):
        session = self.start(daily_goal=5)["session"]
        for card in session["terms"]:
            self.assertEqual(self.answer(session, card["id"]).status_code, 200)
        data = self.start(daily_goal=5)
        self.assertEqual(data["session"]["terms"], [])
        data = self.start(daily_goal=5, extra=True)
        self.assertEqual(len(data["session"]["terms"]), 3)
        for card in data["session"]["terms"]:
            self.answer(data["session"], card["id"])
        data = self.start(extra=True)
        self.assertEqual(data["new_today"], 3)
        self.assertEqual(data["session"]["terms"], [])

    def test_topic_category_and_date_filters(self):
        data = self.start(category="automotive", tag="can", date=str(self.today))
        self.assertEqual({card["id"] for card in data["session"]["terms"]}, {term.pk for term in self.terms[10:]})
        data = self.start(date=str(self.today - timedelta(days=1)))
        self.assertEqual(data["session"]["terms"], [])
        # Repeated appearances also count, not only the first-seen date.
        past = DailyDigest.objects.create(date=self.today - timedelta(days=1), subject="past", raw_text="")
        self.terms[0].appeared_in.add(past)
        data = self.start(date=str(past.date))
        self.assertEqual([card["id"] for card in data["session"]["terms"]], [self.terms[0].pk])

    def test_weak_mode_includes_future_weak_records_and_no_new(self):
        record = ReviewRecord.objects.get(user=self.user, term=self.terms[0])
        record.familiarity = "mastered"
        record.save()
        ReviewRecord.objects.create(user=self.user, term=self.terms[7], familiarity="familiar", next_review_date=self.today + timedelta(days=2))
        data = self.start(weak_only=True)
        ids = {card["id"] for card in data["session"]["terms"]}
        self.assertNotIn(self.terms[0].pk, ids)
        self.assertIn(self.terms[7].pk, ids)
        self.assertEqual(len(ids), 5)
        self.assertFalse(any(card["is_new"] for card in data["session"]["terms"]))

    def test_account_isolation_and_invalid_queue_answers(self):
        session = self.start()["session"]
        self.client.force_authenticate(self.other)
        self.assertIsNone(self.client.get("/api/review/session/").data["session"])
        self.assertEqual(self.answer(session, session["terms"][0]["id"]).status_code, 404)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.answer(session, self.terms[-1].pk).status_code, 400)
        ReviewSession.objects.filter(pk=session["id"]).update(date=self.today - timedelta(days=1))
        self.assertEqual(self.answer(session, session["terms"][0]["id"]).status_code, 400)

    def test_superseded_session_cannot_submit(self):
        old = self.start()["session"]
        self.start(category="automotive")
        self.assertEqual(self.answer(old, old["terms"][0]["id"]).status_code, 400)

    def test_input_validation_and_authentication(self):
        for data in ({"daily_goal": 100}, {"tag": "missing"}, {"date": "bad"}, {"mode": "bad"}):
            with self.subTest(data=data):
                self.assertEqual(self.client.post("/api/review/session/", data, format="json").status_code, 400)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/review/session/").status_code, 401)
        self.assertEqual(self.client.post("/api/review/session/", {}).status_code, 401)

    def test_empty_meanings_excluded_and_decoys_prefer_topic(self):
        self.terms[11].meaning = "  "
        self.terms[11].save()
        data = self.start(category="automotive", mode="choice")
        self.assertEqual(len(data["session"]["terms"]), 1)
        data = self.start(tag="nand", mode="choice")
        for card in data["session"]["terms"]:
            self.assertTrue(all(value.startswith("Meaning ") for value in card["options"]))
            self.assertNotIn("Meaning 10", card["options"])

    def test_written_review_does_not_build_decoys(self):
        data = self.start(mode="written")
        for card in data["session"]["terms"]:
            self.assertEqual(card["options"], [card["meaning"]])

    def test_choice_deduplicates_meanings_before_limiting_candidates(self):
        Term.objects.all().delete()
        Term.objects.bulk_create([
            Term(term=f"A{i:03}", meaning=" same " if i % 2 else "same")
            for i in range(100)
        ] + [Term(term=f"Z{i}", meaning=f"other {i}") for i in range(3)])
        self.tag.terms.add(*Term.objects.all())
        for tagged in (True, False):
            with self.subTest(tagged=tagged):
                if not tagged:
                    self.tag.terms.clear()
                data = self.start(mode="choice", tag=self.tag.slug if tagged else "")
                self.assertTrue(data["session"]["terms"])
                for card in data["session"]["terms"]:
                    self.assertEqual(set(card["options"]), {"same", "other 0", "other 1", "other 2"})
                    self.assertEqual(len(card["options"]), 4)

    def test_preferences_and_sessions_are_deleted_with_account(self):
        self.start()
        user_id = self.user.pk
        self.user.delete()
        self.assertFalse(ReviewSession.objects.filter(user_id=user_id).exists())
        self.assertFalse(ReviewPreferences.objects.filter(user_id=user_id).exists())
