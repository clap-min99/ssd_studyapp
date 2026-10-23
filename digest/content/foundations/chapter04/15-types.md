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

## 따라 풀기

a=sa=1110₂, b=sb=0011₂로 같은 패턴을 넣습니다. unsigned는 14×3=42이므로 결과 00101010₂=0x2A입니다. signed는 −2×3=−6이고 8비트 2의 보수는 256−6=250의 패턴 11111010₂=0xFA입니다. 두 결과의 하위 4비트는 같지만 전체 8비트 결과와 수 해석은 다릅니다.

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

## 다음으로 이어가기

다음 선택 심화에서는 같은 동작을 여러 폭으로 재사용합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.7–4.7.2, 인쇄 pp. 211–215 / PDF pp. 232–236. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
