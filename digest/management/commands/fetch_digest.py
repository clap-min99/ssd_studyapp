"""
매일 실행할 커맨드.

    python manage.py fetch_digest

하는 일:
    1. Gmail에서 최신 다이제스트 메일을 가져온다.
    2. Gemini로 구조화한다.
    3. DailyDigest / Article / LearningItem / Term 으로 DB에 저장한다.
    4. 같은 날짜가 이미 저장돼 있으면 건너뛴다 (--force로 덮어쓰기 가능).
"""

from __future__ import annotations

from datetime import date as date_cls

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from digest.models import Article, DailyDigest, LearningItem, Term, Tag
from fetcher.gemini_parser import parse_digest_with_gemini
from fetcher.gmail_client import fetch_latest_digest


class Command(BaseCommand):
    help = "Gmail에서 최신 SSD/자동차 SW 다이제스트를 가져와 DB에 저장한다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days-back",
            type=int,
            default=2,
            help="최근 며칠 이내 메일을 검색할지 (기본 2일)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="같은 날짜 데이터가 이미 있어도 덮어쓴다.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="DB에 저장하지 않고 파싱 결과만 출력한다.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Gmail에서 최신 다이제스트 메일 확인 중...")
        digest_mail = fetch_latest_digest(days_back=options["days_back"])

        if digest_mail is None:
            raise CommandError("최근 다이제스트 메일을 찾지 못했습니다.")

        digest_date = date_cls.fromisoformat(digest_mail["date"])

        if not options["force"] and DailyDigest.objects.filter(date=digest_date).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"{digest_date} 다이제스트는 이미 저장되어 있습니다. "
                    "덮어쓰려면 --force 옵션을 사용하세요."
                )
            )
            return

        self.stdout.write(f"메일 발견: {digest_mail['subject']}")
        self.stdout.write("Gemini로 구조화 중...")
        parsed = parse_digest_with_gemini(digest_mail["body"])

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS("--dry-run: DB에 저장하지 않았습니다."))
            self.stdout.write(f"기사 {len(parsed.articles)}건, "
                               f"학습콘텐츠 {len(parsed.learning_items)}건, "
                               f"용어 {len(parsed.terms)}건")
            return

        with transaction.atomic():
            digest_obj, created = DailyDigest.objects.update_or_create(
                date=digest_date,
                defaults={
                    "subject": digest_mail["subject"],
                    "raw_text": digest_mail["body"],
                },
            )

            if not created:
                # --force로 재실행된 경우, 기존 하위 항목을 지우고 새로 채운다.
                digest_obj.articles.all().delete()
                digest_obj.learning_items.all().delete()

            for a in parsed.articles:
                article_obj = Article.objects.create(
                    digest=digest_obj,
                    title=a.title,
                    links=a.links,
                    summary=a.summary,
                    insight=a.insight,
                    category=a.category,
                )
                if a.tags:
                    article_obj.tags.set(Tag.objects.filter(slug__in=a.tags))

            for li in parsed.learning_items:
                li_obj = LearningItem.objects.create(
                    digest=digest_obj,
                    heading=li.heading,
                    body=li.body,
                )
                if li.tags:
                    li_obj.tags.set(Tag.objects.filter(slug__in=li.tags))
                

            new_term_count = 0
            for t in parsed.terms:
                term_obj, term_created = Term.objects.get_or_create(
                    term=t.term,
                    defaults={
                        "meaning": t.meaning or "",
                        "relevance": t.relevance or "",
                        "first_seen_digest": digest_obj,
                    },
                )
                # 재등장이어도 이 다이제스트에 나왔다는 사실은 기록한다 (상세 팝업의 "관련 기사" 목록용)
                term_obj.appeared_in.add(digest_obj)
                if term_created:
                    new_term_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"저장 완료: {digest_date} / 기사 {len(parsed.articles)}건 / "
                f"학습콘텐츠 {len(parsed.learning_items)}건 / "
                f"새 용어 {new_term_count}건 (중복 제외 총 {len(parsed.terms)}건 처리)"
            )
        )