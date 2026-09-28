import time

from django.core.management.base import BaseCommand
from google.genai.errors import ClientError

from digest.models import Tag, Term
from fetcher.gemini_parser import tag_term

# 무료 티어 분당 5회 한도 — 여유 있게 13초 간격
REQUEST_INTERVAL_SECONDS = 13


class Command(BaseCommand):
    help = "태그가 비어있는 기존 용어에 Gemini로 태그(챕터)를 채운다 (1회성 백필)."

    def handle(self, *args, **kwargs):
        terms = list(Term.objects.filter(tags__isnull=True))
        total = len(terms)
        self.stdout.write(f"{total}건 처리 시작")

        for i, t in enumerate(terms, 1):
            for attempt in range(3):
                try:
                    slugs = tag_term(t.term, t.meaning, t.relevance)
                    break
                except ClientError as e:
                    if e.code == 429 and attempt < 2:
                        self.stdout.write(self.style.WARNING(f"레이트리밋, 60초 대기 후 재시도"))
                        time.sleep(60)
                    else:
                        raise

            if slugs:
                t.tags.set(Tag.objects.filter(slug__in=slugs))
            self.stdout.write(f"[{i}/{total}] {t.term[:40]} -> {slugs}")
            time.sleep(REQUEST_INTERVAL_SECONDS)
