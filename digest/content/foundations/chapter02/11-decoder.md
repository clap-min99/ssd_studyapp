## 이번 레슨의 목표

2:4 디코더의 각 출력을 최소항으로 쓰고, 디코더와 OR로 논리 함수를 구현할 수 있으면 됩니다.

## 앞에서 배운 내용

MUX는 입력 번호로 데이터를 고릅니다. 디코더(decoder)는 입력 번호에 해당하는 출력선을 활성화합니다. 여기서는 **별도 enable이 없고 출력이 active-high**인 n:2ⁿ 디코더를 다룹니다.

## 이진 코드에서 one-hot으로

두 입력 A1·A0의 값 00·01·10·11에 대해 각각 Q0·Q1·Q2·Q3 중 하나만 1입니다. 정확히 한 비트만 1인 표현을 **one-hot**이라고 합니다. 입력이 안정된 정상 동작을 말하며, 전환 중 글리치는 뒤에서 다룹니다.

| A1A0 | Q3Q2Q1Q0 |
| --- | --- |
| 00 | 0001 |
| 01 | 0010 |
| 10 | 0100 |
| 11 | 1000 |

출력식을 쓰면 `Q0=¬A1·¬A0`, `Q1=¬A1·A0`, `Q2=A1·¬A0`, `Q3=A1·A0`입니다. 즉 각각이 입력의 **최소항 하나**입니다. 보수 입력을 공유하는 인버터 두 개와 AND 네 개로 기본 구조를 만들 수 있습니다.

<svg viewBox="0 0 440 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c2-dec-title c2-dec-desc">
<title id="c2-dec-title">디코더 출력 1과 2를 OR하여 XOR 구현하기</title>
<desc id="c2-dec-desc">A1과 A0를 2대4 디코더에 넣습니다. 출력 Q1과 Q2를 OR하여 F로 만듭니다. Q0와 Q3는 이 출력 함수에 쓰지 않습니다. 입력 01 또는 10에서만 F가 1입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="90" y="25" width="135" height="165" rx="5"/><rect x="315" y="80" width="65" height="65" rx="5"/></g><g fill="none" stroke="var(--ink)" stroke-width="2"><path d="M30 70 H90 M30 145 H90 M225 48 H275 M225 88 H280 V96 H315 M225 128 H280 V130 H315 M225 168 H275 M380 112 H415"/></g><g fill="var(--ink)" font-family="sans-serif" font-size="14" text-anchor="middle"><text x="16" y="76">A1</text><text x="16" y="151">A0</text><text x="157" y="98">2:4</text><text x="157" y="122">디코더</text><text x="251" y="40">Q0</text><text x="251" y="80">Q1</text><text x="251" y="120">Q2</text><text x="251" y="188">Q3</text><text x="347" y="118">OR</text><text x="425" y="118">F</text></g>
</svg>
<p class="diagram-caption">그림 2-11. 출력 두 개를 직접 묶지 않고 OR 블록으로 합칩니다.</p>

## 따라 풀기

입력 두 비트가 서로 다를 때 F=1이라고 합시다. SOP는 `F=¬A1·A0+A1·¬A0`이므로 디코더의 **Q1과 Q2를 OR**하면 됩니다. 입력 10에서 Q2만 1이므로 F=1, 11에서는 Q3만 1이므로 F=0입니다.

여러 함수가 같은 입력을 사용한다면 디코더 출력들을 공유하고 각 함수의 OR만 따로 둘 수도 있습니다. 예를 들어 같은 입력에서 ‘둘 다 1’ 출력 H는 Q3를 그대로 사용합니다. 이는 최소항을 만들고 필요한 것들을 모으는 SOP 구조이며, 5장의 ROM 개념과 연결됩니다.

## 헷갈리기 쉬운 점

디코더와 우선순위 회로는 다릅니다. 이 디코더는 **이진 번호**를 입력받아 정확히 한 출력을 켭니다. 앞의 우선순위 회로는 **동시 요청들**을 받아 가장 높은 요청 하나를 승인하고, 요청이 없으면 전부 끕니다. 실제 부품이 active-low나 enable을 사용한다면 표를 그 규격에 맞춰 바꿔야 합니다.

## 직접 확인하기

1. 3:8 디코더 입력이 101이면 어느 출력이 1인가요?
2. 2:4 디코더로 두 입력 XNOR를 구현하려면 어느 출력들을 OR하나요?
3. 디코더의 Q1과 Q2를 전선 하나로 직접 묶으면 OR와 같나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 이진수 101은 5이므로 <strong>Q5</strong>만 1입니다. 출력 벡터를 Q7부터 쓰면 00100000입니다.</p>
<p>2. 입력 00과 11에서 켜져야 하므로 <strong>Q0와 Q3</strong>를 OR합니다.</p>
<p>3. 아닙니다. 일반 출력 두 개를 묶는 것은 <strong>출력 충돌</strong>을 만들 수 있습니다. 실제 OR 회로가 필요합니다.</p>
</details>

## 다음으로 이어가기

여러 방법으로 같은 기능을 구현했습니다. 다음에는 입력이 바뀐 뒤 언제까지 출력을 기다려야 하는지, 선택선과 데이터 도착 시간이 회로 선택에 어떤 영향을 주는지 계산합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §2.8.2, 인쇄 pp. 84–86 / PDF pp. 106–108. XOR 적용·기능도·문제를 새로 구성했습니다.
