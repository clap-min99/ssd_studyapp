## 이번 레슨의 목표

선택 심화입니다. ROM 점 표기와 소자 유무를 구별하고 pseudo-nMOS·동적 배열의 조건을 설명합니다.

## 앞에서 배운 내용

1장의 선택 심화에서는 약한 pull-up과 pull-down의 경쟁을 봤습니다. 이를 많은 행·열의 규칙적인 배열에 적용합니다.

## 논리 표의 1과 접지로 끌어내리는 소자는 반대일 수 있다

pseudo-nMOS 출력은 약한 pMOS가 위로 당기고, 활성화된 nMOS 경로가 있으면 아래로 내려갑니다. ROM의 한 열에서 선택된 행에 pull-down 소자가 있으면 출력은 0, 없으면 1입니다. 따라서 ‘점은 출력 1’이라는 ROM 논리 표에서는 점이 없는 위치에 pull-down을 배치하는 구현이 가능합니다. 점이 언제나 트랜지스터 존재를 뜻하지 않습니다.

PLA의 AND 평면도 반전을 이용해 곱항을 만들 수 있습니다. t=A·¬B라면 출력 t를 0으로 만드는 조건은 ¬A+B입니다. 따라서 ¬A 또는 B가 활성일 때 pull-down하는 NOR 형태를 쓰면 `t=¬(¬A+B)=A·¬B`가 됩니다. OR 평면에서 항들이 raw 노드를 당겨 0을 만들면 마지막 인버터를 거쳐 OR 결과로 바꿉니다. 중간 반전을 생략하면 완전히 다른 함수가 됩니다.

동적 배열은 precharge와 evaluate 구간으로 동작을 나누어 충전·방전합니다. 저장 노드가 입력을 언제든 정적 복원하는 회로와 다르므로 클록 위상·누설·유지 시간·입력 조건이 필요합니다. 동적 회로를 모든 순간의 이상적 조합 게이트처럼 연결해서 해석하지 않습니다.

이 레슨은 소자 수를 줄이는 구조 원리를 다루는 선택 심화입니다. 실제 전압·소자 치수·감지 회로·타이밍 설계는 포함하지 않으며 기능도와 트랜지스터 도면의 추상화 수준을 구별합니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-25-t c5-25-d">
<title id="c5-25-t">[선택 심화] 배열 구현: Pull-down과 논리 반전</title>
<desc id="c5-25-d">ROM의 한 행이 선택된 경우 소자 유무와 출력의 관계를 나타낸 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">pull-down 있음</text><text x="75" y="87">선택 시 출력 0</text><text x="223" y="59">pull-down 없음</text><text x="223" y="87">약한 pull-up → 1</text><text x="371" y="59">논리 점 표기</text><text x="371" y="87">어떤 의미인지 확인</text></g>
</svg>
<p class="diagram-caption">그림 5-25. ROM의 한 행이 선택된 경우 소자 유무와 출력의 관계를 나타낸 개념도입니다.</p>

## 따라 풀기

2주소 비트 ROM의 한 출력 표를 주소 00,01,10,11 순서로 1,0,1,0이라 정합니다. 00·10 행에는 pull-down이 없고 01·11 행에는 있습니다. 주소 10이면 선택된 접지 경로가 없어 출력은 1입니다. PLA의 t=A·¬B에 A=1,B=0을 넣으면 pull-down 조건 ¬A+B=0이라 t=1, A=1,B=1이면 조건 1이라 t=0으로 원래 곱항과 일치합니다.

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

## 다음으로 이어가기

마지막에는 산술·저장·메모리를 작은 시스템으로 함께 검증합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.6.3, 인쇄 pp. 282–283 / PDF pp. 303–304. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
