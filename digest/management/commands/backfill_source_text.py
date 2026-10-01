import time

from django.core.management.base import BaseCommand
from django.db.models import Q

from digest.models import DailyDigest
from fetcher.gemini_parser import extract_sources


class Command(BaseCommand):
    help = "source_text가 비어있는 기존 기사/학습 콘텐츠에 메일 원문 부분을 채운다 (1회성 백필)."

    def handle(self, *args, **kwargs):
        digests = DailyDigest.objects.filter(
            Q(articles__source_text="") | Q(learning_items__source_text="")
        ).distinct()
        total = digests.count()
        self.stdout.write(f"다이제스트 {total}건 처리 시작")

        for i, d in enumerate(digests, 1):
            items = [*d.articles.filter(source_text=""), *d.learning_items.filter(source_text="")]
            titles = [getattr(it, "title", None) or it.heading for it in items]
            try:
                sources = extract_sources(d.raw_text, titles)
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e):
                    self.stdout.write(self.style.WARNING("Gemini 일일 한도 초과 — 내일 다시 실행하면 남은 것부터 이어서 채운다."))
                    return
                self.stdout.write(self.style.WARNING(f"[{i}/{total}] {d.date} 실패: {str(e)[:200]}"))
                continue

            filled = 0
            for it, src in zip(items, sources):
                if src.strip():
                    it.source_text = src.strip()
                    it.save(update_fields=["source_text"])
                    filled += 1
            self.stdout.write(f"[{i}/{total}] {d.date} -> {filled}/{len(items)}개 채움")
            time.sleep(1)  # 분당 요청 한도 여유 두기
