## 이번 레슨의 목표

조건의 반대를 검사해 불필요한 블록을 건너뛰고 두 경로가 합쳐지는 위치를 설명합니다.

## 앞에서 배운 내용

레슨7에서 조건부 분기와 무조건 점프를 배웠습니다. 식의 참·거짓을 제어 흐름으로 옮깁니다.

## Else 블록까지 흘러가지 않게 하기

조건이 `if (a0<a1) result=10; else result=20;`이면 거짓 조건인 a0≥a1을 검사하여 else로 갑니다. 참 블록을 끝낸 뒤에는 else를 건너뛰어야 합니다.

```asm
bge  a0, a1, choose_else
addi t0, zero, 10
jal  zero, choose_done
choose_else:
addi t0, zero, 20
choose_done:
addi a2, t0, 1
```

마지막 명령어는 조건문 밖의 공통 후속 작업입니다. 조건이 어느 쪽이든 실행합니다. 앞의 C 표현은 작은 signed 값만 비교하며 산술 범위 초과가 없는 예입니다.

## 여러 갈래 선택: 선택 심화

switch는 비교와 분기 사슬로 구현할 수도 있습니다. 선택값2·5에 서로 다른 블록, 나머지에 기본 블록을 두는 경우, 상수2와 비교해 맞으면 case2로, 이어5와 비교해 맞으면 case5로, 둘 다 아니면 default로 갑니다. 각 case 뒤의 공통 done 점프가 C의 break 역할을 합니다.

항상 이런 사슬로 컴파일되는 것은 아닙니다. 점프 테이블은 다른 구현 선택입니다. HDL case는 병렬 회로 기술이고 여기의 분기 사슬은 실행 명령어열이라는 차이도 기억합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-8-t c6-8-d">
<title id="c6-8-t">조건을 뒤집어 Else로 보내고 참 경로는 Else를 건너뛴다.</title>
<desc id="c6-8-d">a0≥a1?|거짓이면10 / 참이면20|두 경로 합류 / 공통 +1|a2=11 또는21</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">a0≥a1?</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">거짓이면10</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">참이면20</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">두 경로 합류</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">공통 +1</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">a2=11 또는21</text>
</svg>
<p class="diagram-caption">그림 6-8. 조건을 뒤집어 Else로 보내고 참 경로는 Else를 건너뛴다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

a0=3,a1=8이면 bge는 거짓입니다. t0=10을 실행하고 jal로 choose_done에 가므로 a2=11입니다. a0=8,a1=8이면 bge가 참이라 choose_else로 이동하여 t0=20,a2=21입니다. ‘작거나 같다’가 아니라 ‘작다’ 조건이므로 같을 때 else인 점을 확인합니다.

참 블록 뒤의 jal을 지우면3<8인 경우에도 else의 t0=20을 실행하여 a2=21이 됩니다. 올바른 분기 조건만으로는 충분하지 않고 블록 끝의 합류 경로도 확인해야 합니다.

## 헷갈리기 쉬운 점

어셈블리 들여쓰기는 실행을 묶지 않습니다. 실제 주소·레이블·분기가 경로를 정합니다. bgt 같은 표기는 소스를 뒤집은 blt로 구현하는 의사명령어일 수 있습니다.

## 직접 확인하기

1. 예제에서 a0=9,a1=4면 a2는?
2. else 없는 if도 끝에 무조건 점프가 필요한가요?
3. switch의 break를 빼면 왜 결과가 달라질 수 있나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 21입니다. bge가 참이라 else에서20을 고르고 공통으로1을 더합니다.</p>
<p>2. 보통은 아닙니다. 거짓이면 if 블록만 건너뛰고 참이면 후속 코드로 이어집니다.</p>
<p>3. 다음 case 블록으로 실행이 이어져 이미 정한 결과를 덮을 수 있습니다.</p>
</details>

## 다음으로 이어가기

앞으로 건너뛰는 분기를 뒤로 돌아가는 분기와 연결하면 반복문이 됩니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.4, 인쇄 pp. 313–315 / PDF pp. 334–336. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
