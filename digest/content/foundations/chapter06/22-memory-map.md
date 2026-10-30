## 이번 레슨의 목표

[선택 심화] 메모리 맵의 배치 선택과 어셈블러 지시어의 공간·정렬 효과를 계산합니다.

## 앞에서 배운 내용

레슨21의 코드는 임의의 교육용 주소에 놓았습니다. 실제 프로그램은 코드·데이터·스택의 배치를 정해야 합니다.

## 메모리 맵은 ISA만으로 결정되지 않는다

메모리 맵(memory map)은 주소별 용도를 정한 배치입니다. 예를 들어 코드 .text, 읽기 전용 상수 .rodata, 초기값 있는 전역 .data,0으로 초기화할 .bss,동적 할당 heap,함수 임시 공간 stack이 있습니다. 운영체제가 있는 환경과 bare-metal의 배치·초기화 책임은 다릅니다. 책의 구체 주소를 모든 RISC-V 시스템의 고정 주소로 외우지 않습니다.

gp는 전역 데이터 접근을 돕는 기준 주소, sp는 스택 기준 주소입니다. heap을 위로,stack을 아래로 자라게 그린 것은 한 배치 모델입니다. 주소 공간4GiB가 곧 설치된 RAM4GiB나 할당 가능한 공간4GiB는 아닙니다.

## 지시어는 CPU 명령어가 아니다

`.text`·`.data`·`.bss`·`.section .rodata`는 섹션을 고릅니다. `.word`는32비트 값,`.byte`는8비트 값,`.string`은 여기의 GNU식 표기에서 널 종료 문자열,`.space N`은 N바이트 공간을 만듭니다. `.equ N,3`은 심볼 상수,`.globl name`은 다른 파일에 공개할 이름을 표시합니다.

```asm
.data
mark: .byte 0x7A
.balign 4
values: .word 6, 11
msg: .string "GO"
.bss
.balign 4
result: .space 4
```

`.balign 4`는 다음 위치를4바이트 경계로 맞춥니다. 책의 RISC-V 도구에서는 `.align 2`도2²=4바이트 정렬입니다. 다른 아키텍처 도구와 혼동을 줄이려면 바이트 수가 명시적인 `.balign`을 씁니다. .bss의0 초기화는 로더 또는 시작 코드가 수행합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-22-t c6-22-d">
<title id="c6-22-t">교육용 .data 베이스0x800에서 정렬 패딩과 데이터를 구별한다.</title>
<desc id="c6-22-d">0x800: mark 1바이트 / 0x801–0x803: 정렬 여유3바이트 / 0x804·0x808: values 두 워드 / 0x80C–0x80E: G·O·널</desc>
<rect x="75" y="18" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="41" text-anchor="middle" font-size="14" fill="var(--ink)">0x800: mark 1바이트</text>
<rect x="75" y="56" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="79" text-anchor="middle" font-size="14" fill="var(--ink)">0x801–0x803: 정렬 여유3바이트</text>
<rect x="75" y="94" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="117" text-anchor="middle" font-size="14" fill="var(--ink)">0x804·0x808: values 두 워드</text>
<rect x="75" y="132" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="155" text-anchor="middle" font-size="14" fill="var(--ink)">0x80C–0x80E: G·O·널</text>
</svg>
<p class="diagram-caption">그림 6-22. 교육용 .data 베이스0x800에서 정렬 패딩과 데이터를 구별한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

.data가0x800에 배치되었다고 가정합니다. mark 뒤 다음 주소는0x801입니다.4바이트 정렬은0x804이므로3바이트 건너뜁니다. 두 워드는0x804–0x80B의8바이트, 문자열은 G·O·널의3바이트여서 msg=0x80C이고 다음 위치0x80F입니다. .data 점유는15바이트입니다.

result가 든 .bss는 별도 섹션이므로 .data 뒤 주소0x80F부터 반드시 이어진다고 단정할 수 없습니다. 링커가 .bss를0x900에 정하면 result=0x900이고 시작 코드가4바이트를0으로 초기화합니다.

## 헷갈리기 쉬운 점

.word가 선언된다고 자동으로 모든 도구에서 원하는 정렬을 보장한다고 가정하지 않습니다. 소스에 명시하고 최종 배치를 확인합니다. 스택과 heap이 충돌하지 않도록 하는 책임도 실제 실행 환경에 있으며 하드웨어가 무조건 막아 주지는 않습니다.

## 직접 확인하기

1. .string의"GO"가2바이트가 아닌 이유는?
2. 현재 위치0x1006에서 .balign 4 뒤 위치는?
3. .equ COUNT,8은 레지스터에8을 적재하나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 끝의0 바이트를 포함해3바이트입니다.</p>
<p>2. 0x1008이며2바이트 여유가 필요합니다.</p>
<p>3. 아닙니다. 어셈블러가 사용하는 심볼 상수를 정의합니다. CPU 실행 명령어가 아닙니다.</p>
</details>

## 다음으로 이어가기

섹션과 심볼을 실제 실행 파일로 만드는 도구들의 역할을 나눠 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.5.1–6.5.2, 인쇄 pp. 344–348 / PDF pp. 365–369. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
