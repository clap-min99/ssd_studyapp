## 이번 레슨의 목표

AND·OR 배열의 역할을 구별하고 자체 함수를 곱항 연결표로 바꾸며 ROM과 비교합니다.

## 앞에서 배운 내용

2장의 SOP와 다출력 논리가 다시 등장합니다. LUT는 진리표 모든 행을 저장했고 PLA는 필요한 항을 직접 구성합니다.

## AND 평면에서 항을 만들고 OR 평면에서 출력을 고른다

프로그래머블 논리 배열(programmable logic array, PLA)은 입력과 보수 입력을 AND 평면에 공급해 곱항(implicant)을 만듭니다. OR 평면은 출력마다 필요한 곱항을 합칩니다. 입력 M개, 곱항 K개, 출력 P개의 조직을 M×K×P로 나타낼 수 있습니다. 이 세 수를 곱한 값을 실제 저장 비트 용량이라고 읽지는 않습니다.

자체 예제로 F=A·B+¬A·C, G=A·B+C를 만듭니다. t0=A·B,t1=¬A·C,t2=C를 만들면 F=t0+t1,G=t0+t2입니다. 공통 t0는 두 출력이 공유합니다.

| 항 | A | B | C | F에 연결 | G에 연결 |
| --- | --- | --- | --- | --- | --- |
| t0 | 참 | 참 | 사용 안 함 | 예 | 예 |
| t1 | 보수 | 사용 안 함 | 참 | 예 | 아니오 |
| t2 | 사용 안 함 | 사용 안 함 | 참 | 아니오 | 예 |

사용하지 않는 리터럴은 그 입력을 곱항에 제한 조건으로 넣지 않는다는 뜻입니다. 0을 AND에 연결해 항을 없애는 뜻이 아닙니다. 그림의 점은 문맥에 따라 리터럴 연결 또는 항의 출력 연결을 나타내므로 어느 평면인지 확인합니다.

ROM을 논리적으로 보면 AND 평면이 모든 최소항 2ᴹ개를 고정 생성하고 OR 평면을 설정하는 특수한 조직입니다. PLA는 필요한 항 수가 적을 때 더 작을 수 있지만 함수·공정·배선·구현 방식에 따라 결과는 달라집니다. 기본 PLA는 2수준 조합논리이며 저장 소자를 포함한 확장 장치와 구별합니다.

<svg viewBox="0 0 450 265" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-23-study-t c5-23-study-d">
<title id="c5-23-study-t">공통 곱항이 두 OR 출력에 연결되는 PLA</title>
<desc id="c5-23-study-d">입력·보수에서 만든 t0=AB가 F와 G 양쪽 OR에 연결됩니다. t1=NOT A·C는 F에,t2=C는 G에만 연결됩니다. AND 평면의 리터럴 배선은 각 항의 식으로 표시한 기능도입니다.</desc>
<rect x="55" y="35" width="105" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="107.5" y="62.5" font-size="15" text-anchor="middle" fill="var(--ink)">t0 = AB</text><rect x="55" y="115" width="105" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="107.5" y="142.5" font-size="15" text-anchor="middle" fill="var(--ink)">t1 = ¬AC</text><rect x="55" y="195" width="105" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="107.5" y="222.5" font-size="15" text-anchor="middle" fill="var(--ink)">t2 = C</text><rect x="300" y="65" width="75" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="337.5" y="92.5" font-size="15" text-anchor="middle" fill="var(--ink)">OR → F</text><rect x="300" y="185" width="75" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="337.5" y="212.5" font-size="15" text-anchor="middle" fill="var(--ink)">OR → G</text><path d="M160 58 H220 V78 H300 M220 58 H245 V198 H300 M160 138 H260 V98 H300 M160 218 H300" fill="none" stroke="var(--ink)" stroke-width="2"/><circle cx="220" cy="58" r="3" fill="var(--ink)"/>
</svg>
<p class="diagram-caption">그림 5-23. 입력·보수에서 만든 t0=AB가 F와 G 양쪽 OR에 연결됩니다. t1=NOT A·C는 F에,t2=C는 G에만 연결됩니다. AND 평면의 리터럴 배선은 각 항의 식으로 표시한 기능도입니다.</p>

## 곱항 하나를 행 하나로 만들고 공유를 표시하기

SOP의 곱항은 특정 입력 조건을 만족할 때 1입니다. t0=A·B는 C가 무엇이든 A=B=1이면 1이고,t1=¬A·C는 B를 보지 않습니다. PLA의 AND 평면은 이 리터럴 선택을 구현합니다. 사용하지 않는 입력을 0으로 곱하는 것이 아니라 그 조건을 제거한 것입니다.

OR 평면에서는 각 출력이 어떤 t를 포함하는지 표시합니다. F=t0+t1,G=t0+t2이므로 t0의 한 결과가 F와 G 양쪽으로 갈라집니다. 이 공유는 두 함수를 각각 독립 회로로 최소화한 결과와 다른 자원 선택을 줄 수 있습니다. 다출력 회로에서는 출력 하나의 식 길이만 보지 않고 공통 항도 확인합니다.

ROM은 모든 최소항을 만든 다음 원하는 행을 합치는 방식으로 볼 수 있고,PLA는 필요한 더 큰 곱항으로 여러 최소항을 묶을 수 있습니다. t0=A·B는 3입력의 최소항 두 개 A·B·¬C와 A·B·C를 함께 덮습니다. 입력 자유도를 항에서 제거하는 의미가 카르노 맵의 묶음과 연결됩니다.

## 따라 풀기

A=0,B=1,C=1이면 t0=0,t1=1,t2=1이라 F=1,G=1입니다. A=1,B=0,C=1이면 t0=0,t1=0,t2=1이라 F=0,G=1입니다. 같은 3입력·2출력 함수를 ROM으로 저장하면 8×2=16비트 표 내용이 필요합니다. PLA에서는 세 곱항을 썼지만 전체 면적을 단순히 3비트라고 비교할 수는 없습니다.

### 조건을 바꾸어 한 번 더 풀기

입력 ABC를 세 가지 골라 항부터 계산합니다.

| ABC | t0=AB | t1=¬AC | t2=C | F | G |
| --- | --- | --- | --- | --- | --- |
| 110 | 1 | 0 | 0 | 1 | 1 |
| 111 | 1 | 0 | 1 | 1 | 1 |
| 001 | 0 | 1 | 1 | 1 | 1 |

첫 두 행은 C가 달라도 t0가 같다는 것을 보여줍니다. 세 번째는 F와 G가 모두 1이어도 서로 다른 항으로 만들어질 수 있음을 보여줍니다. 최종 출력만 같은 사례를 보고 내부 항을 동일하다고 추측하지 않습니다.

## 헷갈리기 쉬운 점

논리식의 +는 OR입니다. 중간 항을 공유하는 것과 시간 순서로 계산기를 재사용하는 것은 다릅니다. PLA의 입력·항·출력 개수와 메모리의 깊이·폭 표기법을 섞지 않습니다.

## 직접 확인하기

1. t0=A·B를 두 출력이 쓰면 항을 두 번 만들어야 하나요?
2. t1에서 B를 사용하지 않는다는 뜻은?
3. 기본 PLA에 현재 상태가 있나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 논리 PLA에서는 한 항을 OR 평면의 두 출력에 연결해 공유할 수 있습니다.</p>
<p>2. B=0,1 모두 해당 항의 값에 영향을 주지 않는다는 뜻입니다.</p>
<p>3. 조합 함수만 구성하므로 자체적인 플립플롭 상태는 없습니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

H=A·B+D·C,J=A·B+¬D·C의 두 출력을 PLA로 구현합니다. 공유 가능한 항과 나머지 항을 정하고 각 출력의 OR 연결을 적으세요. 이 함수의 입력 수와 사용한 항 수는 각각 얼마인가요?

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>t0=A·B,t1=D·C,t2=¬D·C로 두고 H=t0+t1,J=t0+t2로 연결합니다. 공통 t0를 공유합니다.</p>
<p>입력은 A,B,C,D 네 개이고 이 구성의 항은 세 개,출력은 두 개입니다. 항 수 3을 저장 용량 3비트라고 부르지 않으며 실제 리터럴/출력 연결의 자원은 별도입니다.</p>
</details>

## 다음으로 이어가기

다음에는 LUT·플립플롭·배선을 함께 설정하는 FPGA를 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.6–5.6.1, 인쇄 pp. 272–276 / PDF pp. 293–297. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
