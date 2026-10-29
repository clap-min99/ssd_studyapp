## 이번 레슨의 목표

선택 심화입니다. 변수 자료형과 net의 역할, 부호 선언의 영향과 VHDL의 타입 차이를 구별합니다.

## 앞에서 배운 내용

레슨 5에서는 공유 버스에 tri를, 나머지 단일 구동 신호에는 logic을 사용했습니다. 자료형 이름과 실제 저장 소자는 같은 분류가 아닙니다.

## 값의 표현과 구동의 해소는 다른 질문이다

기존 Verilog의 `reg`는 절차적 할당 대상에 쓰던 자료형 이름입니다. 이름에 reg가 있어도 조합논리 출력일 수 있습니다. SystemVerilog의 `logic`도 사용 방식에 따라 조합 출력이나 저장값이 됩니다. net인 `wire`와 `tri`는 연결과 여러 구동원의 해소를 나타냅니다. `wire logic`처럼 net 종류와 원소 자료형을 함께 쓸 수도 있습니다. 이 트랙에서는 단일 구동은 logic, 공유 버스 모델은 tri로 의도를 드러냅니다.

같은 세기의 tri 구동원에서 Z와 1은 1, 0과 1은 X가 됩니다. `trireg`는 무구동 시 이전 값을 보존하는 모델, `tri0`·`tri1`은 각각 기본 풀다운·풀업 모델입니다. `triand`와 `trior`는 wired-AND·wired-OR 해소 규칙을 가집니다. 이는 일반 레지스터나 임의의 실제 배선을 대신하는 만능 모델이 아닙니다.

```systemverilog
module multiply4(input logic [3:0] a, b,
                  input logic signed [3:0] sa, sb,
                  output logic [7:0] unsigned_product,
                  output logic signed [7:0] signed_product);
  assign unsigned_product = a * b;
  assign signed_product = sa * sb;
endmodule
```

같은 폭의 packed logic 벡터는 기본적으로 unsigned입니다. `signed`는 2의 보수 해석을 지정하며 곱셈·크기 비교·산술 오른쪽 시프트 등에 영향을 줍니다. 두 피연산자의 폭·부호와 결과 폭을 함께 정합니다. 연결·슬라이스·signed와 unsigned 혼합식은 부호를 바꿀 수 있으므로 원래 선언만 믿고 복잡한 식을 추측하지 않습니다.

VHDL 비교: entity가 인터페이스, architecture가 구현을 담으며 STD_LOGIC과 STD_LOGIC_VECTOR는 IEEE 라이브러리에서 가져옵니다. STD_LOGIC은 U·X·0·1·Z·W·L·H·-의 9상태이고 BOOLEAN과 같은 자료형이 아닙니다. numeric_std의 unsigned·signed 및 변환 함수로 산술 해석을 명시할 수 있습니다. signal의 <=와 process 내부 variable의 :=도 구별합니다. VHDL-2008에서는 process(all)과 out 포트 읽기를 지원하므로 구버전 제한을 그대로 일반화하지 않습니다. 이는 비교 안내이며 VHDL 전체 구현 과정은 아닙니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-15-t c4-15-d">
<title id="c4-15-t">[선택 심화] 자료형과 부호: Logic·Net·VHDL 비교</title>
<desc id="c4-15-d">자료형을 읽을 때 구별할 세 질문을 나란히 나타낸 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">logic / reg</text><text x="75" y="91">이름만으로 FF 아님</text><text x="223" y="63">wire / tri</text><text x="223" y="91">연결·구동 해소</text><text x="371" y="63">signed</text><text x="371" y="91">비트의 수 해석</text></g>
</svg>
<p class="diagram-caption">그림 4-15. 자료형을 읽을 때 구별할 세 질문을 나란히 나타낸 개념도입니다.</p>

## 자료형을 세 질문으로 나누어 판단하기

자료형을 읽을 때는 첫째 ‘어떤 값을 담는가’, 둘째 ‘누가 이 신호를 구동하는가’, 셋째 ‘그 비트를 어떤 수로 해석하는가’를 나누세요. 4상태 logic은 첫 질문에, 여러 구동을 해소하는 tri 같은 net은 둘째 질문에, signed는 셋째 질문에 답합니다. 셋 중 어느 하나도 혼자서 플립플롭을 보장하지 않습니다.

예를 들어 `logic signed [3:0] a`는 4비트 2의 보수 해석을 명시합니다. 하지만 `assign y=~a`에 쓰이면 조합논리이고 always_ff에서 q로 복사하면 저장 데이터입니다. 기존 Verilog의 reg도 그 이름만으로 저장 소자라는 뜻이 아니었습니다.

signed 캐스팅은 같은 폭의 패턴에 수 해석을 붙입니다. 4비트 1110을 signed로 읽으면 −2가 되지만 이를 unsigned 8비트 00001110으로 먼저 확장한 뒤 signed로 읽으면 +14입니다. ‘캐스팅했으니 언제나 음수가 된다’가 아니라 폭과 확장 순서를 함께 봐야 합니다. 혼합식은 두 피연산자의 폭·부호를 명시한 다음 계산합니다.

## 따라 풀기

a=sa=1110₂, b=sb=0011₂로 같은 패턴을 넣습니다. unsigned는 14×3=42이므로 결과 00101010₂=0x2A입니다. signed는 −2×3=−6이고 8비트 2의 보수는 256−6=250의 패턴 11111010₂=0xFA입니다. 두 결과의 하위 4비트는 같지만 전체 8비트 결과와 수 해석은 다릅니다.

### 조건을 바꾸어 한 번 더 풀기

패턴 1110을 8비트로 옮기는 두 방법을 비교합니다.

| 의도 | 8비트 패턴 | 8비트 signed 해석 |
| --- | --- | --- |
| unsigned 14를 보존 | 00001110 | +14 |
| signed −2를 보존 | 11111110 | −2 |

여기에 00000011을 곱하면 각각 +42와 −6입니다. 곱셈 출력의 signed 표시만 바꾸어서는 입력 확장 단계에서 바뀐 의미를 되돌릴 수 없습니다. 연산 전의 비트 폭부터 검산해야 합니다.

## 헷갈리기 쉬운 점

logic이 항상 플립플롭이라는 설명도, wire가 SystemVerilog에서 금지되었다는 설명도 맞지 않습니다. 다중 구동 가능 여부는 net/variable 선언과 포트 규칙까지 확인해야 합니다. VHDL의 U는 초기화하지 않은 상태이며 SystemVerilog의 기본 초기 X와 표기가 다릅니다.

## 직접 확인하기

1. reg라는 이름이면 반드시 저장 소자가 있나요?
2. 1110을 4비트 unsigned와 signed로 읽으면 각각 얼마인가요?
3. VHDL의 BOOLEAN과 STD_LOGIC은 같은 자료형인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 아닙니다. 사건 조건과 모든 할당 경로를 봐야 합니다.</p>
<p>2. 14와 −2입니다.</p>
<p>3. 아닙니다. 비교 결과와 논리 신호 사이에 필요한 변환·조건 표현을 구별합니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

4비트 a=1001을 signed 값으로 보존하며 8비트 b에 넣으려 합니다. 반복 연결식을 적고, 0 확장한 결과와 값을 비교하세요. 연결 결과를 이후 signed 산술에 쓰려면 무엇을 확인해야 하나요?

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>비트 패턴은 {{4{a[3]}},a}로 11111001을 만듭니다. 8비트 2의 보수로 읽으면 −7입니다. 0 확장은 00001001이며 +9입니다.</p>
<p>연결 표현 자체가 자동으로 signed 값을 주는 것은 아니므로 b의 signed 선언이나 적절한 명시 변환을 확인합니다. 올바른 패턴과 올바른 수 해석을 모두 확보해야 합니다.</p>
</details>

## 다음으로 이어가기

다음 선택 심화에서는 같은 동작을 여러 폭으로 재사용합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.7–4.7.2, 인쇄 pp. 211–215 / PDF pp. 232–236. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
