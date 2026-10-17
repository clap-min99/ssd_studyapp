## 이번 레슨의 목표

**선택 심화**입니다. CMOS 인버터와 두 입력 NAND·NOR의 연결을 추적하고, 전송 게이트와 pseudo-nMOS의 목적·한계를 설명할 수 있으면 됩니다.

## 앞에서 배운 내용

nMOS는 게이트가 HIGH일 때, pMOS는 LOW일 때 켜지는 논리 스위치 모델을 배웠습니다. 이제 출력 Y를 전원 또는 GND에 연결합니다. 분석은 유효한 입력이 안정된 뒤의 상태를 기준으로 합니다.

## NOT은 위아래 스위치를 반대로 켠다

CMOS는 상보적인 nMOS와 pMOS를 함께 사용합니다. 인버터에서는 위의 pMOS가 Y를 V_DD로 끌어올리는 **풀업(pull-up)**, 아래의 nMOS가 Y를 GND로 끌어내리는 **풀다운(pull-down)** 입니다. 두 게이트에는 같은 입력 A를 넣습니다.

<svg viewBox="0 0 440 285" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="cmos-title cmos-desc">
<title id="cmos-title">CMOS 인버터의 스위치 기능도</title>
<desc id="cmos-desc">위에는 VDD에서 Y로 이어지는 pMOS, 아래에는 Y에서 GND로 이어지는 nMOS가 있습니다. A가 0이면 위 스위치만 켜져 Y는 1, A가 1이면 아래 스위치만 켜져 Y는 0입니다. 직사각형은 정식 소자 기호가 아니라 기능을 표시한 것입니다.</desc>
<g fill="none" stroke="var(--ink)" stroke-width="2"><path d="M195 25 H245 M220 25 V50 M220 100 V135 H365 M220 135 V170 M220 220 V250 M195 250 H245 M202 258 H238 M211 266 H229 M45 135 H105 V75 H150 M105 135 V195 H150"/></g>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="150" y="50" width="140" height="50" rx="5"/><rect x="150" y="170" width="140" height="50" rx="5"/><circle cx="220" cy="135" r="4"/></g>
<g fill="var(--ink)" font-family="sans-serif" font-size="14" text-anchor="middle"><text x="220" y="17">V_DD</text><text x="220" y="72">pMOS</text><text x="220" y="90">A=0일 때 ON</text><text x="220" y="192">nMOS</text><text x="220" y="210">A=1일 때 ON</text><text x="30" y="140">A</text><text x="384" y="140">Y</text><text x="278" y="257">GND</text></g>
</svg>
<p class="diagram-caption">그림 1-10. 연결 경로를 나타낸 기능도입니다. 직사각형은 정식 MOS 회로 기호를 대신한 표시입니다.</p>

| A | 위 pMOS | 아래 nMOS | Y |
| --- | --- | --- | --- |
| 0 | ON | OFF | 1 |
| 1 | OFF | ON | 0 |

유효한 입력이 안정되면 한쪽 네트워크만 켜지므로 이상적인 모델에서는 전원에서 GND로 이어지는 직통 경로가 없습니다. 실제 누설과 전환 중 전류는 다음 레슨에서 구분합니다.

## NAND와 NOR는 직렬·병렬을 바꾼다

직렬 스위치는 **모두 켜져야** 경로가 연결되고, 병렬은 **하나만 켜져도** 연결됩니다.

| 구현 | GND 쪽 nMOS | V_DD 쪽 pMOS | 출력이 0인 조건 |
| --- | --- | --- | --- |
| NAND | A·B 두 개를 직렬 | A·B 두 개를 병렬 | A와 B가 모두 1 |
| NOR | A·B 두 개를 병렬 | A·B 두 개를 직렬 | A 또는 B가 1 |

예를 들어 NAND에서 A=1, B=0이면 풀다운의 B 스위치가 꺼져 GND 경로가 끊어집니다. 위쪽 B pMOS는 켜지므로 Y는 V_DD에 연결되어 1입니다. A=B=1일 때만 두 nMOS가 모두 켜지고 두 pMOS가 모두 꺼져 출력 0이 됩니다.

정적인 상보 CMOS에서는 풀다운의 직렬 구조에 풀업의 병렬 구조를 대응시키고, 병렬에 직렬을 대응시켜 **전도 조건이 상보적**이 되게 합니다. 둘 다 켜지면 전원·GND 사이 전류가 흐르고, 둘 다 꺼지면 출력이 떠 있는(floating) 상태가 됩니다. 안정된 입력에서 이 두 상황을 피해야 합니다.

## 따라 풀기

두 입력 AND를 정적 상보 CMOS로 만든다고 합시다.

1. 먼저 두 입력 NAND를 만듭니다. nMOS 두 개와 pMOS 두 개로 총 4개입니다.
2. 출력에 NOT을 붙여 다시 반전합니다. nMOS·pMOS 각 하나, 총 2개입니다.
3. 결과는 `¬(¬(A·B)) = A·B`이고, 단순한 구현은 **총 6개**의 트랜지스터입니다.

이 수는 이 구현 방식의 개수입니다. 모든 공정·라이브러리·논리 방식에서 AND가 무조건 6개라는 일반 법칙은 아닙니다. 세 입력 NAND는 직렬 nMOS 3개와 병렬 pMOS 3개로 6개입니다.

## 신호를 통과시키는 전송 게이트

nMOS 단독은 LOW를 잘 통과시키지만 HIGH는 문턱전압의 영향으로 충분히 높게 전달하지 못할 수 있습니다. pMOS는 반대로 HIGH에 유리하고 LOW에 약합니다. 두 소자를 **병렬**로 연결하고 nMOS 게이트에 EN, pMOS 게이트에 ¬EN을 넣은 것이 전송 게이트(transmission gate)입니다.

EN=1이면 둘 다 켜져 두 단자를 연결하고, EN=0이면 둘 다 꺼져 분리합니다. 신호를 반전하는 게이트가 아니라 양방향 스위치입니다. 데이터가 0인지 1인지와, 스위치를 켜는 제어 EN을 구분합니다.

## 왜 pseudo-nMOS라는 다른 방식도 있을까

여러 pMOS를 직렬로 놓는 대신 **항상 켜진 약한 pMOS 하나**를 풀업으로 쓰고, nMOS 풀다운을 강하게 만드는 방식이 pseudo-nMOS입니다. 풀다운이 꺼지면 위쪽이 Y를 올리고, 풀다운이 켜지면 약한 풀업을 이겨 Y를 낮춥니다. 많은 입력을 가진 NOR 등의 특정 회로에서 장점이 있지만 소자 크기와 강도의 비율을 설계해야 합니다.

LOW일 때도 위아래 경로가 모두 켜져 **정적 전류가 흐른다**는 대가가 있습니다. 앞서 설명한 정적 상보 CMOS의 규칙을 이 다른 논리 방식에 그대로 적용하면 안 됩니다.

## 헷갈리기 쉬운 점

NAND 논리 게이트와 NAND 플래시 저장장치는 같은 대상이 아닙니다. 또한 전송 게이트의 OFF는 출력 0을 의미하지 않습니다. 연결이 끊기면 그 노드의 전압은 다른 회로나 남아 있는 전하에 달려 있어, 별도 구동 없이 유효한 논리값을 보장할 수 없습니다.

## 직접 확인하기

1. NOR에서 A=1, B=0일 때 GND 경로와 V_DD 경로는 각각 연결되나요? Y는 무엇인가요?
2. 세 입력 NAND의 nMOS와 pMOS는 각각 어떻게 연결하나요?
3. 전송 게이트 EN=0일 때 신호 두 단자는 어떤 상태인가요? pseudo-nMOS가 LOW일 때의 전력상 단점도 설명해보세요.

<details>
<summary>정답과 해설 보기</summary>
<p>1. 병렬 nMOS 중 A가 켜져 <strong>GND 경로는 연결</strong>됩니다. 직렬 pMOS 중 A가 꺼져 <strong>V_DD 경로는 차단</strong>됩니다. Y는 <strong>0</strong>입니다.</p>
<p>2. <strong>nMOS 3개 직렬, pMOS 3개 병렬</strong>입니다. 세 입력이 모두 1일 때만 아래 경로가 연결됩니다.</p>
<p>3. 두 소자가 모두 꺼져 <strong>두 단자는 분리</strong>됩니다. 출력 0이라는 뜻은 아닙니다. pseudo-nMOS는 LOW에서 약한 풀업과 풀다운 사이에 <strong>지속적인 전류</strong>가 흘러 정적 전력을 소비합니다.</p>
</details>

## 다음으로 이어가기

논리 기능이 같아도 구현에 따라 전력과 속도가 달라집니다. 다음에는 정전용량 충전과 정적 전류를 구분해 전력을 계산합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §1.7.5–1.7.8, 인쇄 pp. 29–32 / PDF pp. 52–55. 원문의 선택 심화 범위입니다. 경로 추적 예제·기능도·문제를 새로 구성했습니다.
