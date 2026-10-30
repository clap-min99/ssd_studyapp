## 이번 레슨의 목표

[선택 심화] 동기 예외와 비동기 인터럽트를 구별하고 처리기의 복귀 정책을 설명합니다.

## 앞에서 배운 내용

레슨12의 함수 호출은 프로그램이 명시적으로 수행했습니다. 예외 처리에서는 예정하지 않은 사건도 현재 실행을 바꿀 수 있습니다.

## 호출과 비슷하지만 저장 규칙이 다르다

동기 예외(exception)는 불법 명령어 등 현재 명령어와 관련된 사건이고, 인터럽트(interrupt)는 타이머·외부 장치 같은 비동기 사건입니다. 두 종류의 처리기로 제어가 넘어가는 동작을 trap이라고 부릅니다. ecall은 실행 환경에 서비스를 요청하는 동기 예외입니다. 시스템 호출 번호·인자·종료 규칙은 OS별 ABI이며 RV32I 하나만으로 정해지지 않습니다.

여기서는 M-mode에서 직접 처리하고 중첩 trap은 다루지 않는 개념 모델입니다. M/S/U는 각각 machine/supervisor/user 권한이며 모든 시스템에 S·U가 있는 것은 아닙니다. 세부 권한 제어는 별도 명세입니다.

| CSR | 역할 |
| --- | --- |
| mtvec | 처리기 베이스와 전달 모드 |
| mcause | 인터럽트 여부와 원인 코드 |
| mepc | 복귀에 사용할 예외·중단 위치 |
| mscratch | 처리기가 활용하는 임시 저장용 CSR |

하드웨어는 mepc·mcause·관련 상태를 기록하고 처리기로 보냅니다. 일반 레지스터 전부를 메모리에 자동 저장하지 않습니다. 처리기는 사용할 레지스터를 보존하고 원인을 처리한 뒤 복원해야 합니다. mscratch 자체가 자동 스택인 것은 아니며 소프트웨어가 포인터 등을 넣어 활용합니다. MRET은 PC뿐 아니라 trap 관련 권한·인터럽트 상태도 복구합니다.

## 재실행·건너뛰기·종료는 서로 다른 정책

문제가 해결되어 원래 명령어를 재시도하려면 mepc를 그대로 둡니다. 정상32비트 명령어를 의도적으로 건너뛰는 정책이라면4를 더할 수 있지만 모든 예외·인터럽트에서 더하면 안 됩니다. C 확장의16비트 명령어는 길이도 다릅니다. 인터럽트 복귀에서 한 명령어를 건너뛰면 프로그램 의미가 깨질 수 있습니다.

direct 모드는 베이스로, vectored 모드의 인터럽트는 BASE+4×원인 코드로 갑니다. 동기 예외는 vectored에서도 베이스입니다. 책의 벡터 간격 설명과 구별하여 공식 특권 명세의4바이트 슬롯 규칙을 사용합니다. CSR 접근 명령어는 현대 분류의 Zicsr이며, MRET은 특권 명령어로 기본 정수 산술과 구별합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-25-t c6-25-d">
<title id="c6-25-t">트랩 처리에서는 복귀 위치와 일반 레지스터 보존을 함께 관리한다.</title>
<desc id="c6-25-d">사건 발생|mepc·mcause 기록 / 처리기|레지스터 저장·처리 / 복원 후 MRET|정책에 따른 PC</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">사건 발생</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">mepc·mcause 기록</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">처리기</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">레지스터 저장·처리</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">복원 후 MRET</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">정책에 따른 PC</text>
</svg>
<p class="diagram-caption">그림 6-25. 트랩 처리에서는 복귀 위치와 일반 레지스터 보존을 함께 관리한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

mepc=0x504에서 길이4인 ecall을 실행했다고 가정합니다. 요청 처리를 완료하고 그 명령어를 건너뛰어 복귀하려면 mepc=0x508로 바꿉니다. 같은0x504에서 발생한 복구 가능한 접근 문제를 해결해 재시도한다면0x504를 유지합니다. 두 정책을 섞으면 재호출 반복 또는 명령어 누락이 됩니다.

별도로 mtvec의 BASE=0x800,MODE=vectored,인터럽트 원인 코드7이면 시작 주소는0x800+4×7=0x81C입니다. 동기 원인 코드7은 같은 숫자여도 인터럽트가 아니므로 베이스0x800으로 갑니다.

## 헷갈리기 쉬운 점

불법 명령어를 무조건 무시하는 예제 정책을 실제 시스템의 일반 규칙으로 사용하지 않습니다. mcause의 최상위 비트와 원인 코드를 함께 해석합니다. 처리기 전체 코드·인터럽트 허용 설정·중첩·장치 승인 절차는 이 레슨 범위 밖입니다.

## 직접 확인하기

1. MRET 대신 ret를 쓰면 같은가요?
2. 인터럽트가 끝날 때 항상 mepc에4를 더하나요?
3. BASE=0x1000에서 vectored 인터럽트 원인11의 주소는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 아닙니다. ret는 ra 기반 JALR이고 MRET은 mepc와 trap 관련 상태를 사용합니다.</p>
<p>2. 아닙니다. 복귀할 정상 실행 위치를 건너뛸 수 있습니다.</p>
<p>3. 0x102C입니다. 4×11=44=0x2C를 더합니다.</p>
</details>

## 다음으로 이어가기

다음에는 같은 비트 패턴을 다르게 비교하는 signed·unsigned 명령어를 모아 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.6.2, 인쇄 pp. 356–359 / PDF pp. 377–380. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 책과 구별한 trap 용어·벡터 전달·CSR 분류는 공식 [Machine-Level ISA](https://docs.riscv.org/reference/isa/priv/machine.html)와 [Zicsr](https://docs.riscv.org/reference/isa/unpriv/zicsr.html)을 참고합니다.
