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

SEQUENTIAL_LESSONS = [
    (1, "01-state.md", "기억과 상태: 피드백으로 1비트 저장하기"),
    (2, "02-latch.md", "D 래치: 언제 데이터를 통과시킬까"),
    (3, "03-flipflop.md", "D 플립플롭과 레지스터: 에지에서 값 저장하기"),
    (4, "04-controls.md", "Enable과 Reset: 유지·갱신·초기화 구별하기"),
    (5, "05-transistors.md", "전송 게이트로 저장 소자 만들기"),
    (6, "06-synchronous.md", "동기식 설계: 피드백 경로에 레지스터 두기"),
    (7, "07-fsm.md", "FSM 설계: 명세에서 상태표와 회로까지"),
    (8, "08-encoding.md", "상태 인코딩: 이진수와 one-hot 비교하기"),
    (9, "09-moore-mealy.md", "Moore와 Mealy: 출력이 반응하는 시점"),
    (10, "10-factoring.md", "FSM 분해: 작은 상태 머신의 협력"),
    (11, "11-reverse.md", "회로에서 FSM 읽기: 식·표·도달 가능한 상태"),
    (12, "12-timing.md", "Setup과 Hold: 느린 경로와 빠른 경로 검사하기"),
    (13, "13-skew.md", "[선택 심화] 클록 스큐: 같은 클록의 다른 도착 시각"),
    (14, "14-synchronizer.md", "준안정성과 동기화기: 비동기 입력 받아들이기"),
    (15, "15-resolution.md", "[선택 심화] 준안정성 해소 시간의 지수 법칙"),
    (16, "16-parallelism.md", "병렬성과 파이프라인: 지연 시간과 처리량"),
    (17, "17-review.md", "3장 종합: 상태·기능·시간을 함께 검증하기"),
]

HDL_LESSONS = [
    (1, "01-modules.md", "HDL과 모듈: 코드를 회로로 읽기"),
    (2, "02-operators.md", "버스와 연산자: 비트별 연산과 축약 연산"),
    (3, "03-mux.md", "조건 선택과 중간 신호: 식을 연결망으로 보기"),
    (4, "04-bits.md", "상수와 비트 조립: 폭·진법·연결·반복"),
    (5, "05-simulation.md", "X·Z와 지연: 시뮬레이션이 표현하는 것"),
    (6, "06-structure.md", "구조 모델링: 인스턴스와 포트로 회로 연결하기"),
    (7, "07-registers.md", "레지스터 기술: 상승 에지에서 값 저장하기"),
    (8, "08-controls.md", "리셋과 Enable: 사건 조건과 우선순위"),
    (9, "09-pipeline.md", "여러 레지스터와 Nonblocking: 이전 값 함께 읽기"),
    (10, "10-latches.md", "래치와 할당 누락: 의도한 기억과 뜻밖의 기억"),
    (11, "11-combinational.md", "Always_comb·Case·If: 모든 입력에 출력 정하기"),
    (12, "12-casez.md", "Casez와 Don’t care: 자유도와 미지값 구별하기"),
    (13, "13-fsm.md", "FSM 기술: 상태 레지스터·다음 상태·출력"),
    (14, "14-moore-mealy.md", "Moore와 Mealy 코드: 10 검출의 관측 시점"),
    (15, "15-types.md", "[선택 심화] 자료형과 부호: Logic·Net·VHDL 비교"),
    (16, "16-parameters.md", "[선택 심화] 매개변수 모듈: 폭을 정해 재사용하기"),
    (17, "17-generate.md", "[선택 심화] Generate: 반복문으로 회로 구성하기"),
    (18, "18-testbench.md", "테스트벤치: 입력 생성에서 자동 검사까지"),
    (19, "19-vectors.md", "파일 기반 검사: 벡터·클록·종료 조건"),
    (20, "20-review.md", "4장 종합: 명세에서 HDL과 자동 검증까지"),
]

BUILDING_BLOCK_LESSONS = [
    (1, "01-adders.md", "반가산기와 전가산기: 한 자리 덧셈의 입출력"),
    (2, "02-ripple.md", "리플 캐리 덧셈기: 자리올림의 긴 경로"),
    (3, "03-lookahead.md", "캐리 미리보기: Generate와 Propagate"),
    (4, "04-prefix.md", "[선택 심화] 프리픽스 덧셈기: 캐리 조건을 트리로 합치기"),
    (5, "05-subtraction.md", "덧셈·뺄셈 공유: 반전과 Carry-in"),
    (6, "06-comparators.md", "비교기: 비트의 같음과 수의 크기"),
    (7, "07-alu.md", "ALU: 산술·논리 연산을 고르는 회로"),
    (8, "08-flags.md", "ALU 플래그와 SLT: 비교 결과를 올바르게 만들기"),
    (9, "09-shifters.md", "시프터와 회전기: 비트 이동과 수의 해석"),
    (10, "10-multiply.md", "[선택 심화] 곱셈기와 MAC: 부분곱을 더하기"),
    (11, "11-division.md", "[선택 심화] 나눗셈기: 부분 나머지로 몫 정하기"),
    (12, "12-fixed-point.md", "고정소수점: 비트 패턴에 배율 약속하기"),
    (13, "13-floating-point.md", "[선택 심화] 부동소수점 표현: 부호·지수·유효숫자"),
    (14, "14-floating-add.md", "[선택 심화] 부동소수점 덧셈: 정렬·정규화·반올림"),
    (15, "15-counters.md", "카운터와 위상 누산기: 저장값을 반복 갱신하기"),
    (16, "16-shift-registers.md", "시프트 레지스터: 직렬·병렬 데이터 바꾸기"),
    (17, "17-scan.md", "[선택 심화] 스캔 체인: 내부 상태를 넣고 꺼내 검사하기"),
    (18, "18-memory-organization.md", "메모리 배열: 주소·워드·포트의 약속"),
    (19, "19-dram-sram.md", "DRAM과 SRAM: 전하와 피드백으로 비트 저장하기"),
    (20, "20-register-file.md", "레지스터 파일: 두 읽기와 한 쓰기 포트"),
    (21, "21-rom-lut.md", "ROM과 LUT: 저장한 표로 논리 함수 구현하기"),
    (22, "22-memory-hdl.md", "메모리 HDL: 배열과 읽기·쓰기 시점"),
    (23, "23-pla.md", "PLA: 필요한 곱항을 여러 출력이 공유하기"),
    (24, "24-fpga.md", "FPGA: LUT·플립플롭·배선으로 회로 배치하기"),
    (25, "25-array-circuits.md", "[선택 심화] 배열 구현: Pull-down과 논리 반전"),
    (26, "26-review.md", "5장 종합: 계산·저장·배열을 함께 설명하기"),
]

ARCHITECTURE_LESSONS = [
    (1, "01-isa.md", "아키텍처와 ISA: 프로그램이 보는 컴퓨터의 약속"),
    (2, "02-registers.md", "레지스터와 산술: 명령어의 입력과 결과 추적하기"),
    (3, "03-immediates.md", "즉시값과 큰 상수: 부호 확장과 LUI"),
    (4, "04-memory.md", "바이트 주소와 Load·Store: 주소와 값 구별하기"),
    (5, "05-logic-shifts.md", "논리와 시프트 명령어: 비트 필드 꺼내고 바꾸기"),
    (6, "06-multiply.md", "[선택 심화] M 확장: 곱의 상위·하위 비트와 나눗셈"),
    (7, "07-branches.md", "PC와 분기: 다음에 실행할 주소 고르기"),
    (8, "08-conditionals.md", "조건문: If·Else와 여러 갈래 선택 구현하기"),
    (9, "09-loops.md", "반복문: 초기화·조건·본문·갱신 추적하기"),
    (10, "10-arrays.md", "워드 배열: 인덱스를 바이트 주소로 바꾸기"),
    (11, "11-bytes-strings.md", "바이트와 문자열: 부호 확장·종료 문자·경계"),
    (12, "12-calls.md", "함수 호출: 인자·반환값·복귀 주소의 이동"),
    (13, "13-stack.md", "스택과 보존 규칙: 누가 어떤 값을 지킬까"),
    (14, "14-nonleaf.md", "중첩 호출: 돌아갈 주소와 살아 있는 값 보존하기"),
    (15, "15-recursion.md", "재귀 호출: 같은 코드에 서로 다른 스택 프레임"),
    (16, "16-pseudoinstructions.md", "의사명령어: 편한 표기와 실제 명령어 구별하기"),
    (17, "17-r-i-encoding.md", "R·I 형식: 어셈블리를 32비트 기계어로 조립하기"),
    (18, "18-s-b-encoding.md", "S·B 형식: 저장 오프셋과 분기 변위 인코딩"),
    (19, "19-u-j-encoding.md", "U·J 형식: 큰 즉시값과 점프 변위 인코딩"),
    (20, "20-decode-addressing.md", "기계어 읽기: 즉시값 복원과 주소 지정 방식"),
    (21, "21-stored-program.md", "저장 프로그램: 명령어·데이터·아키텍처 상태"),
    (22, "22-memory-map.md", "[선택 심화] 메모리 맵과 지시어: 코드와 데이터 배치"),
    (23, "23-toolchain.md", "[선택 심화] 컴파일·어셈블·링크·로드의 역할"),
    (24, "24-endianness.md", "[선택 심화] 엔디언: 워드의 바이트를 주소에 배치하기"),
    (25, "25-exceptions.md", "[선택 심화] 예외와 인터럽트: 원인·복귀 PC·상태 보존"),
    (26, "26-signed.md", "[선택 심화] Signed·Unsigned 명령어와 넘침 검사"),
    (27, "27-float-compressed.md", "[선택 심화] F·C 확장: 데이터 폭과 명령어 길이"),
    (28, "28-isa-families.md", "ISA의 확장과 비교: RISC-V·MIPS·ARM"),
    (29, "29-x86.md", "[선택 심화] x86 비교: 피연산자·플래그·가변 길이"),
    (30, "30-review.md", "6장 종합: 프로그램을 상태 변화로 설명하기"),
]

CHAPTERS = [
    ("binary-representation", "디지털 설계의 출발점",
     "H&H RISC-V판 1장: 추상화 → 수의 표현 → 논리 게이트 → 전압·CMOS·전력. 그림과 예제, 확인 문제로 기초를 쌓습니다.",
     "chapter01", LESSONS),
    ("combinational-logic", "조합논리 설계",
     "H&H RISC-V판 2장: 진리표와 논리식 → 불 대수·카르노 맵 → MUX·디코더 → 지연과 글리치. 원하는 동작을 회로로 구현합니다.",
     "chapter02", COMBINATIONAL_LESSONS),
    ("sequential-logic", "순차논리 설계",
     "H&H RISC-V판 3장: 래치·플립플롭 → 동기식 회로·FSM → Setup/Hold·동기화 → 파이프라인. 기억하는 회로의 기능과 시간을 함께 설계합니다.",
     "chapter03", SEQUENTIAL_LESSONS),
    ("hardware-description-languages", "하드웨어 기술 언어",
     "H&H RISC-V판 4장: SystemVerilog로 조합논리·레지스터·FSM을 표현하고 테스트벤치로 검증합니다. 자료형·매개변수·Generate는 선택 심화로 다룹니다.",
     "chapter04", HDL_LESSONS),
    ("digital-building-blocks", "디지털 구성 요소",
     "H&H RISC-V판 5장: 덧셈기·ALU·시프터 → 소수 표현 → 카운터·시프트 레지스터 → 메모리·PLA·FPGA. 블록의 폭·부호·시간과 연결을 함께 익힙니다.",
     "chapter05", BUILDING_BLOCK_LESSONS),
    ("risc-v-architecture", "RISC-V 아키텍처",
     "H&H RISC-V판 6장: 레지스터·메모리·어셈블리 → 분기·배열·함수 호출 → 기계어 인코딩과 저장 프로그램. 컴파일·예외·확장·다른 ISA도 연결합니다.",
     "chapter06", ARCHITECTURE_LESSONS),
]


class Command(BaseCommand):
    help = "Harris & Harris RISC-V판 1–6장에 대응하는 기초 챕터와 레슨을 생성·갱신한다."

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
