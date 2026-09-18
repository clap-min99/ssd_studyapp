import time

from django.core.management.base import BaseCommand

from digest.models import Article, Tag
from fetcher.gemini_parser import tag_article


class Command(BaseCommand):
    help = "태그가 비어있는 기존 기사에 Gemini로 태그를 채운다 (1회성 백필)."

    def handle(self, *args, **kwargs):
        articles = Article.objects.filter(tags__isnull=True)
        total = articles.count()
        self.stdout.write(f"{total}건 처리 시작")

        for i, a in enumerate(articles, 1):
            slugs = tag_article(a.title, a.summary, a.category)
            if slugs:
                a.tags.set(Tag.objects.filter(slug__in=slugs))
            self.stdout.write(f"[{i}/{total}] {a.title[:40]} -> {slugs}")
            time.sleep(1)  # 분당 요청 한도 여유 두기