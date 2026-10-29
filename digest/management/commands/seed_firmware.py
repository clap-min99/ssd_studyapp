from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from digest.models import Lesson, Tag


LESSONS = [
    (1, "01-addresses.md", "주소와 포인터: 코드가 하드웨어에 닿기까지"),
    (2, "02-bits.md", "비트와 필드: 다른 설정을 보존하며 바꾸기"),
    (3, "03-registers.md", "레지스터의 약속: volatile과 읽기·쓰기 부작용"),
]


class Command(BaseCommand):
    help = "펌웨어 동작 원리 첫 장의 검토된 Markdown 레슨을 생성·갱신한다."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        content_dir = Path(__file__).resolve().parents[2] / "content" / "firmware" / "chapter01"
        chapter, _ = Tag.objects.update_or_create(
            slug="firmware-memory-registers",
            defaults={
                "name": "C 코드에서 레지스터까지",
                "description": "주소·포인터 → 비트·필드 → 레지스터 접근 규칙. 직접 쓴 코드의 값 변화를 추적하며 펌웨어의 출발점을 정리합니다.",
                "category": "firmware", "order": 1, "prerequisite": None,
            },
        )
        for order, filename, title in LESSONS:
            Lesson.objects.update_or_create(
                chapter=chapter, order=order,
                defaults={"title": title, "body": (content_dir / filename).read_text(encoding="utf-8")},
            )
        self.stdout.write(self.style.SUCCESS(f"펌웨어 동작 원리: 1개 챕터, {len(LESSONS)}개 레슨 저장 완료"))
