## 이번 레슨의 목표

선택 심화입니다. ROM 점 표기와 소자 유무를 구별하고 pseudo-nMOS·동적 배열의 조건을 설명합니다.

## 앞에서 배운 내용

1장의 선택 심화에서는 약한 pull-up과 pull-down의 경쟁을 봤습니다. 이를 많은 행·열의 규칙적인 배열에 적용합니다.

## 논리 표의 1과 접지로 끌어내리는 소자는 반대일 수 있다

pseudo-nMOS 출력은 약한 pMOS가 위로 당기고, 활성화된 nMOS 경로가 있으면 아래로 내려갑니다. ROM의 한 열에서 선택된 행에 pull-down 소자가 있으면 출력은 0, 없으면 1입니다. 따라서 ‘점은 출력 1’이라는 ROM 논리 표에서는 점이 없는 위치에 pull-down을 배치하는 구현이 가능합니다. 점이 언제나 트랜지스터 존재를 뜻하지 않습니다.

PLA의 AND 평면도 반전을 이용해 곱항을 만들 수 있습니다. t=A·¬B라면 출력 t를 0으로 만드는 조건은 ¬A+B입니다. 따라서 ¬A 또는 B가 활성일 때 pull-down하는 NOR 형태를 쓰면 `t=¬(¬A+B)=A·¬B`가 됩니다. OR 평면에서 항들이 raw 노드를 당겨 0을 만들면 마지막 인버터를 거쳐 OR 결과로 바꿉니다. 중간 반전을 생략하면 완전히 다른 함수가 됩니다.

동적 배열은 precharge와 evaluate 구간으로 동작을 나누어 충전·방전합니다. 저장 노드가 입력을 언제든 정적 복원하는 회로와 다르므로 클록 위상·누설·유지 시간·입력 조건이 필요합니다. 동적 회로를 모든 순간의 이상적 조합 게이트처럼 연결해서 해석하지 않습니다.

이 레슨은 소자 수를 줄이는 구조 원리를 다루는 선택 심화입니다. 실제 전압·소자 치수·감지 회로·타이밍 설계는 포함하지 않으며 기능도와 트랜지스터 도면의 추상화 수준을 구별합니다.

<svg viewBox="0 0 450 285" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-25-study-t c5-25-study-d">
<title id="c5-25-study-t">약한 pull-up과 선택 pull-down의 출력 노드</title>
<desc id="c5-25-study-d">약한 pull-up이 raw 노드를 1로 당기고,선택 pull-down 경로가 켜지면 GND로 내려 0이 됩니다. 출력 F가 OR여야 하는 평면에서는 raw 뒤 인버터가 필요합니다. 소자 기능 블록으로 그렸습니다.</desc>
<text x="175" y="20" font-size="15" text-anchor="middle" fill="var(--ink)">V_DD</text><rect x="125" y="45" width="100" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="175.0" y="70.0" font-size="15" text-anchor="middle" fill="var(--ink)">약한 pull-up</text><rect x="125" y="150" width="100" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="175.0" y="175.0" font-size="15" text-anchor="middle" fill="var(--ink)">pull-down</text><rect x="300" y="100" width="90" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="345.0" y="127.5" font-size="15" text-anchor="middle" fill="var(--ink)">NOT</text><path d="M175 25 V45 M175 85 V150 M175 120 H300 M390 122 H430 M175 190 V225 M160 225 H190 M165 232 H185" fill="none" stroke="var(--ink)" stroke-width="2"/><circle cx="175" cy="120" r="3" fill="var(--ink)"/><text x="245" y="105" font-size="14" text-anchor="middle" fill="var(--ink)">raw</text><text x="420" y="105" font-size="15" text-anchor="middle" fill="var(--ink)">F</text><text x="175" y="260" font-size="15" text-anchor="middle" fill="var(--ink)">GND 경로가 켜지면 raw=0</text>
</svg>
<p class="diagram-caption">그림 5-25. 약한 pull-up이 raw 노드를 1로 당기고,선택 pull-down 경로가 켜지면 GND로 내려 0이 됩니다. 출력 F가 OR여야 하는 평면에서는 raw 뒤 인버터가 필요합니다. 소자 기능 블록으로 그렸습니다.</p>

## 접지 경로와 최종 반전으로 논리값 복원하기

약한 pull-up이 달린 출력 노드에서 실제로 확인할 것은 ‘선택된 입력 조건이 GND로의 경로를 여는가’입니다. 경로가 열리면 raw 노드는 0이고 없으면 1입니다. 논리 표의 점이 1을 뜻하는 ROM에서는 점이 있는 자리와 pull-down 소자를 두는 자리가 반대일 수 있습니다.

PLA의 t=A·¬B를 만든다면 raw 출력이 0이어야 하는 조건은 ¬A 또는 B입니다. 그 두 신호를 parallel pull-down 조건으로 둔 뒤 raw 출력을 읽으면 ¬(¬A+B)=A·¬B입니다. 이 단계의 반전은 드모르간 법칙으로 검산할 수 있습니다. OR 평면에서 raw NOR를 만들었다면 뒤 인버터까지 포함해야 출력 OR가 됩니다.

동적 회로에서는 동일한 논리값 논의 외에 언제 precharge하고 언제 evaluate하는지도 필요합니다. precharge 시각의 raw 1을 곧바로 최종 함수 1로 읽으면 평가 전 결과를 오해합니다. 저장 노드의 유효 시간과 관찰 시점을 지정한 모델이라는 점을 기억합니다.

## 따라 풀기

2주소 비트 ROM의 한 출력 표를 주소 00,01,10,11 순서로 1,0,1,0이라 정합니다. 00·10 행에는 pull-down이 없고 01·11 행에는 있습니다. 주소 10이면 선택된 접지 경로가 없어 출력은 1입니다. PLA의 t=A·¬B에 A=1,B=0을 넣으면 pull-down 조건 ¬A+B=0이라 t=1, A=1,B=1이면 조건 1이라 t=0으로 원래 곱항과 일치합니다.

### 조건을 바꾸어 한 번 더 풀기

t=A·¬B의 네 경우를 pull-down 조건으로 풀어 봅니다.

| A B | pull-down 조건 ¬A+B | raw 노드 t |
| --- | --- | --- |
| 00 | 1 | 0 |
| 01 | 1 | 0 |
| 10 | 0 | 1 |
| 11 | 1 | 0 |

원래 t의 진리표와 일치합니다. 만약 마지막 raw 값을 한 번 더 반전하면 이 함수의 부정이 됩니다. ‘소자를 붙였다’는 말보다 출력까지의 반전 횟수를 적는 습관이 중요합니다.

## 헷갈리기 쉬운 점

pseudo-nMOS의 정적 전류와 동적 회로의 누설·충전 조건은 서로 다른 비용입니다. 점·색깔만 외우지 말고 출력까지의 반전 횟수와 실제 접지 경로를 추적합니다.

## 직접 확인하기

1. ROM에서 선택된 pull-down이 켜지면 출력은?
2. t=A·B를 NOR로 만들 pull-down 조건은?
3. 동적 배열에서 위상을 생략해도 되나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 이 모델에서는 0입니다.</p>
<p>2. ¬A+¬B입니다. 그 부정이 A·B입니다.</p>
<p>3. 아닙니다. 충전과 평가 시점이 동작 조건의 일부입니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

raw 노드가 t0 또는 t1이 1일 때 아래로 당겨지는 배열을 만듭니다. 최종 출력 F=t0+t1을 얻으려면 무엇을 추가해야 하나요? t0=1,t1=0에서 raw와 F를 각각 구하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>raw=NOT(t0 OR t1)이므로 마지막 인버터가 필요합니다. 그러면 F=NOT raw=t0 OR t1입니다.</p>
<p>입력 1,0에서는 접지 경로가 열려 raw=0이고 인버터 뒤 F=1입니다. raw 노드와 최종 출력의 이름을 구별하지 않으면 NOR를 OR로 잘못 읽을 수 있습니다.</p>
</details>

## 다음으로 이어가기

마지막에는 산술·저장·메모리를 작은 시스템으로 함께 검증합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.6.3, 인쇄 pp. 282–283 / PDF pp. 303–304. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
