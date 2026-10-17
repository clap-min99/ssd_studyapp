from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from digest.models import Lesson, Tag


LESSONS = [
    (1, "01-roadmap.md", "큰 회로를 이해하는 법: 추상화와 설계 원칙"),
    (2, "02-digital.md", "디지털 추상화: 연속적인 세상에서 0과 1 고르기"),
    (3, "03-bits.md", "비트와 이진수: 0과 1로 수를 표현하기"),
    (4, "04-hex.md", "바이트와 16진수: 긴 비트열 읽기"),
    (5, "05-addition.md", "이진수 덧셈: 캐리와 고정된 비트 폭"),
    (6, "06-signed.md", "2의 보수와 오버플로: 같은 비트, 다른 해석"),
    (7, "07-gates.md", "논리 게이트: 진리표·논리식·회로 연결하기"),
    (8, "08-levels.md", "논리 전압과 잡음 여유: 0과 1의 물리적 조건"),
    (9, "09-transistors.md", "[선택 심화] 반도체와 MOS 스위치"),
    (10, "10-cmos.md", "[선택 심화] CMOS로 NOT·NAND·NOR 만들기"),
    (11, "11-power.md", "[선택 심화] 전력: 비트가 바뀔 때 드는 비용"),
    (12, "12-review.md", "1장 종합: 표현에서 회로까지 설명하기"),
]


COMBINATIONAL_LESSONS = [
    (1, "01-specification.md", "조합논리의 약속: 기능과 시간, 연결 규칙"),
    (2, "02-canonical.md", "진리표를 식으로: SOP와 POS 표준형"),
    (3, "03-algebra.md", "불 대수: 같은 함수를 더 간단하게 쓰기"),
    (4, "04-schematic.md", "논리식을 회로로: 중간 신호와 우선순위 회로"),
    (5, "05-multilevel.md", "다단 논리와 버블 푸싱: 구현의 선택"),
    (6, "06-unknown.md", "X와 Z: 모르는 값과 구동하지 않는 상태"),
    (7, "07-kmap.md", "카르노 맵: 이웃한 1들을 묶어 변수 지우기"),
    (8, "08-display.md", "4변수 카르노 맵: 표시 회로 설계하기"),
    (9, "09-dontcare.md", "Don't care: 생략해도 되는 조건을 정확히 정하기"),
    (10, "10-mux.md", "멀티플렉서: 데이터를 고르고 함수를 구현하기"),
    (11, "11-decoder.md", "디코더: 비트 코드를 one-hot으로 바꾸기"),
    (12, "12-timing.md", "전파·오염 지연: 가장 느린 경로와 빠른 경로"),
    (13, "13-glitch.md", "글리치: 논리적으로 맞아도 잠깐 틀릴 수 있다"),
    (14, "14-review.md", "2장 종합: 명세에서 구현·검증까지"),
]

CHAPTERS = [
    ("binary-representation", "디지털 설계의 출발점",
     "H&H RISC-V판 1장: 추상화 → 수의 표현 → 논리 게이트 → 전압·CMOS·전력. 그림과 예제, 확인 문제로 기초를 쌓습니다.",
     "", LESSONS),
    ("combinational-logic", "조합논리 설계",
     "H&H RISC-V판 2장: 진리표와 논리식 → 불 대수·카르노 맵 → MUX·디코더 → 지연과 글리치. 원하는 동작을 회로로 구현합니다.",
     "chapter02", COMBINATIONAL_LESSONS),
]


class Command(BaseCommand):
    help = "Harris & Harris RISC-V판 1–2장에 대응하는 기초 챕터와 레슨을 생성·갱신한다."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        content_dir = Path(__file__).resolve().parents[2] / "content" / "foundations"
        previous = None
        for chapter_order, (slug, name, description, directory, lessons) in enumerate(CHAPTERS, 1):
            chapter, _ = Tag.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "category": "foundations",
                          "order": chapter_order, "prerequisite": previous},
            )
            # 기존 시범 레슨의 URL을 유지하며 책 순서에 맞춰 빈자리를 만든다.
            if chapter_order == 1 and chapter.lessons.filter(order=1, title=LESSONS[2][2]).exists():
                for old_order, new_order in [(3, 6), (2, 4), (1, 3)]:
                    chapter.lessons.filter(order=old_order).update(order=new_order)
            for order, filename, title in lessons:
                Lesson.objects.update_or_create(
                    chapter=chapter, order=order,
                    defaults={"title": title, "body": (content_dir / directory / filename).read_text(encoding="utf-8")},
                )
            previous = chapter
        count = sum(len(chapter[4]) for chapter in CHAPTERS)
        self.stdout.write(self.style.SUCCESS(f"컴퓨터 구조 기초: {len(CHAPTERS)}개 챕터, {count}개 레슨 저장 완료"))
