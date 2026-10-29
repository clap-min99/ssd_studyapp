## 이번 레슨의 목표

N·Z·C·V를 계산하고 signed·unsigned 비교와 SLT 버스 확장을 구별합니다.

## 앞에서 배운 내용

앞 레슨 ALU는 결과 비트만 만들었습니다. 이제 결과가 0인지, 산술 범위를 넘었는지도 봅니다.

## 연산 종류에 맞는 플래그를 정의한다

N은 result의 최상위 비트, Z는 모든 result 비트가 0일 때 1입니다. N은 패턴의 부호 비트이며 overflow가 있는 수학적 결과의 실제 부호를 보장하지 않습니다. 이 장에서는 C·V를 덧셈/뺄셈에서만 유효하게 두고 AND·OR에서는 0으로 정의합니다.

산술 결과 S에 대해 덧셈 V=¬(A_msb⊕B_msb)·(A_msb⊕S_msb), 뺄셈 V=(A_msb⊕B_msb)·(A_msb⊕S_msb)입니다. sub로 통합하면 `V=(A_msb⊕S_msb)·¬(A_msb⊕B_msb⊕sub)`입니다. C는 확장 덧셈의 최상위 캐리입니다.

아래 표는 반드시 A−B를 수행한 뒤의 플래그를 사용합니다. +는 OR입니다.

| 관계 | signed | unsigned |
| --- | --- | --- |
| A=B / A≠B | Z / ¬Z | Z / ¬Z |
| A<B | N⊕V | ¬C |
| A≤B | Z+(N⊕V) | Z+¬C |
| A≥B | ¬(N⊕V) | C |
| A>B | ¬Z·¬(N⊕V) | ¬Z·C |

SLT(set less than)는 참이면 결과 버스의 숫자 1, 거짓이면 0입니다. 4비트 signed SLT는 `{3'b000, less}`이며 less=N⊕V입니다. SLTU는 unsigned less=¬C를 사용합니다. 단순히 S의 부호 비트만 0 확장하면 overflow에서 틀립니다. 모든 프로세서가 이 플래그를 명령어 상태로 노출한다는 뜻은 아닙니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-8-t c5-8-d">
<title id="c5-8-t">ALU 플래그와 SLT: 비교 결과를 올바르게 만들기</title>
<desc id="c5-8-d">결과 특성·산술 특성·비교값 확장을 구별한 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">결과 특성</text><text x="75" y="87">N=MSB·Z=영</text><text x="223" y="59">산술 특성</text><text x="223" y="87">C=캐리·V=범위 초과</text><text x="371" y="59">SLT 출력</text><text x="371" y="87">000 뒤에 less 연결</text></g>
</svg>
<p class="diagram-caption">그림 5-8. 결과 특성·산술 특성·비교값 확장을 구별한 개념도입니다.</p>

## 플래그는 같은 합에 대한 서로 다른 질문이다

N은 ‘저장 폭 안의 결과 MSB가 1인가’, Z는 ‘그 결과가 전부 0인가’, C는 ‘확장 덧셈에서 한 비트가 더 나왔는가’, V는 ‘signed 수학적 답이 표현 범위를 벗어났는가’입니다. 하나의 정답/오답 표시를 네 가지로 나눈 것이 아닙니다. 질문이 다르므로 C=1,V=0과 C=0,V=1이 모두 가능합니다.

덧셈에서 서로 다른 부호끼리는 서로 상쇄되므로 signed 범위를 넘지 않습니다. 같은 부호끼리 더했는데 결과 부호가 달라지면 넘쳤습니다. 뺄셈에서는 B의 실제 부호 반전 효과를 고려해 입력 부호가 다를 때 넘칠 수 있습니다. 이 두 설명을 각각의 V 식에 대응시키세요.

SLT는 플래그를 프로그램이 사용할 수 있는 데이터 값으로 바꾼 결과입니다. less=1이면 결과는 모든 비트가 1인 마스크가 아니라 숫자 1입니다. 8비트라면 00000001입니다. 결과를 만드는 순간 어떤 연산에서 얻은 N·V인지도 분명해야 하므로 A−B 경로와 비교 선택을 함께 설계합니다.

## 따라 풀기

A=0110,B=1110의 뺄셈입니다. 6−(−2)=8은 signed 범위 밖입니다. 비트 계산은 0110+0001+1=01000이므로 S=1000,C=0,N=1,Z=0입니다. 입력 부호가 다르고 결과 부호가 A와 달라 V=1입니다. signed less=N⊕V=0으로 6<−2는 거짓입니다. unsigned에서는 6<14가 참이라 ¬C=1입니다. 각각 SLT 결과는 0000,0001입니다.

### 조건을 바꾸어 한 번 더 풀기

서로 다른 두 덧셈을 대조합니다.

| 4비트 덧셈 | 전체 합 | N | Z | C | V |
| --- | --- | --- | --- | --- | --- |
| 1111+0001 | 10000 | 0 | 1 | 1 | 0 |
| 0111+0001 | 01000 | 1 | 0 | 0 | 1 |

첫 행은 unsigned 15+1이 넘쳤지만 signed −1+1=0은 정상입니다. 둘째는 unsigned 7+1=8은 정상이나 signed +8이 범위 밖입니다. ‘carry가 없으니 overflow도 없다’는 생각을 이 두 행으로 반박할 수 있습니다.

## 헷갈리기 쉬운 점

N⊕V를 덧셈 뒤에 계산해 A<B라고 읽지 않습니다. 비교 표는 뺄셈 결과에 적용합니다. carry와 borrow의 극성도 먼저 정해야 합니다.

## 직접 확인하기

1. 0111+0001의 N,Z,C,V는?
2. 1111+0001의 C와 V는?
3. less=1일 때 8비트 SLT는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 1,0,0,1입니다. signed 7+1은 범위를 넘습니다.</p>
<p>2. C=1,V=0입니다. signed −1+1=0은 범위 안입니다.</p>
<p>3. 00000001입니다. 모든 비트를 1로 채우지 않습니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

signed 4비트 A=1001,B=0010에 대해 A−B의 N,Z,C,V와 SLT를 구하세요. 이어 unsigned 비교에서는 less가 어떻게 달라지는지 설명하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>1001+1101+1=10111이라 S=0111,C=1,N=0,Z=0입니다. signed −7−2=−9가 범위를 넘으므로 V=1입니다. signed less=N XOR V=1이고 SLT=0001입니다.</p>
<p>unsigned 9&lt;2는 거짓이므로 less=NOT C=0입니다. 같은 출력 비트와 플래그를 사용해도 수 해석에 따라 비교식이 다릅니다.</p>
</details>

## 다음으로 이어가기

다음에는 비트를 이동하는 조합 시프터를 만듭니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.4, 인쇄 pp. 248–251 / PDF pp. 269–272. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
