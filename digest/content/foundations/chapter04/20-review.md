## 이번 레슨의 목표

리셋·유지·갱신 명세를 HDL과 독립 기대값에 연결하고 기능 검사와 물리 타이밍 검사의 범위를 구별합니다.

## 앞에서 배운 내용

조합논리는 assign 또는 완전 할당 always_comb, 저장 소자는 always_ff와 nonblocking으로 기술했습니다. 이제 둘을 합쳐 검사합니다.

## 누적 홀짝 제어기의 명세를 고정한다

3장 종합의 1비트 제어기에 enable을 추가합니다. active-high 동기 리셋이 최우선이고, reset=0일 때 en=1인 에지에서 x를 누적합니다. Q_next=Q⊕x이며 en=0이면 유지합니다. 출력 odd=Q입니다. x·en·reset은 상승 에지 전에 준비합니다.

```systemverilog
module parity_control(input logic clk, reset, en, x,
                      output logic odd);
  logic next_odd;
  assign next_odd = odd ^ x;
  always_ff @(posedge clk)
    if (reset) odd <= 1'b0;
    else if (en) odd <= next_odd;
endmodule
```

회로는 XOR 조합 경로와 1비트 저장 소자, 리셋·유지 선택입니다. 아래 자체 테스트는 입력의 매 에지 이력을 별도 기대값으로 누적합니다. 첫 벡터는 reset=en=x=1로 리셋 우선순위를, 둘째는 en=0,x=1로 유지 동작을 검사합니다.

```systemverilog
module tb_parity_control;
  timeunit 1ns;
  timeprecision 1ps;
  logic clk, reset, en, x, odd;
  logic expected;
  logic [2:0] stimulus [0:5];
  parity_control dut(.clk(clk), .reset(reset), .en(en), .x(x), .odd(odd));
  initial begin
    clk = 0;
    forever #5 clk = ~clk;
  end
  initial begin
    stimulus[0]=3'b111; stimulus[1]=3'b001;
    stimulus[2]=3'b011; stimulus[3]=3'b010;
    stimulus[4]=3'b011; stimulus[5]=3'b100;
    reset=1; en=0; x=0; expected=0;
    for (int i=0; i<6; i=i+1) begin
      @(negedge clk);
      {reset,en,x} = stimulus[i];
      @(posedge clk);
      if (reset) expected=0;
      else if (en && x) expected=~expected;
      #1;
      if (odd !== expected) $fatal(1, "Mismatch at edge %0d", i+1);
    end
    $display("PASS: parity control");
    $finish;
  end
endmodule
```

입력은 하강 에지에서 바꾸고 상승 에지에서 기대값을 갱신하며 #1 뒤에 DUT를 관찰합니다. 첫 5ns 상승에서는 미리 켠 reset이 적용되고, 표의 E1은 첫 벡터가 들어간 15ns 상승입니다. 테스트벤치의 expected는 검증용 변수이므로 blocking으로 즉시 계산합니다. DUT의 저장 소자에는 nonblocking을 사용한다는 규칙과 충돌하지 않습니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-20-t c4-20-d">
<title id="c4-20-t">4장 종합: 명세에서 HDL과 자동 검증까지</title>
<desc id="c4-20-d">동일한 명세를 회로와 검사에 연결하는 세 관점입니다. 기대값은 입력 이력에서 따로 계산합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">명세</text><text x="75" y="91">reset &gt; en &gt; 유지</text><text x="223" y="63">DUT</text><text x="223" y="91">XOR·1비트 저장</text><text x="371" y="63">검증</text><text x="371" y="91">자극·기대값·비교</text></g>
</svg>
<p class="diagram-caption">그림 4-20. 동일한 명세를 회로와 검사에 연결하는 세 관점입니다. 기대값은 입력 이력에서 따로 계산합니다.</p>

## 따라 풀기

표의 에지 번호는 벡터 0부터 5까지를 E1부터 E6으로 센 것입니다.

| 에지 | reset | en | x | 직후 기대 odd | 이유 |
| --- | --- | --- | --- | --- | --- |
| E1 | 1 | 1 | 1 | 0 | 리셋 우선 |
| E2 | 0 | 0 | 1 | 0 | 유지 |
| E3 | 0 | 1 | 1 | 1 | 1을 누적 |
| E4 | 0 | 1 | 0 | 1 | 0은 홀짝 유지 |
| E5 | 0 | 1 | 1 | 0 | 두 번째 1 |
| E6 | 1 | 0 | 0 | 0 | 다시 초기화 |

테스트를 실행했을 때 이 기대값과 맞는지를 검사합니다. 추가로 에지 사이 x 변화에 odd가 바뀌지 않는지, 연속 enable 입력과 반복 리셋도 확인할 수 있습니다. 오류 검출력을 확인하려면 별도 사본에서 리셋 우선순위를 뒤집거나 enable을 제거했을 때 실패하는지도 봅니다.

## 헷갈리기 쉬운 점

기능 시뮬레이션 통과만으로 최대 클록 주파수와 hold를 보장하지 않습니다. 합성된 경로와 실제 타이밍 제약은 3장의 setup·hold·스큐 관점으로 별도 확인합니다. 이 장은 SystemVerilog 입문 범위이며 언어 전체, 원문 연습문제 전체, 특정 FPGA 보드 배포 과정은 포함하지 않습니다.

## 직접 확인하기

1. 핵심: odd=1,reset=en=x=1인 에지 직후 값은 무엇인가요? (레슨 8)
2. 핵심: next_odd를 별도 always_ff에서 저장하면 같은 회로인가요? (레슨 7·9)
3. 핵심: en=0일 때 odd에 값을 할당하지 않으면 왜 여기서는 맞나요? (레슨 10)
4. 핵심: 출력이 X일 때 !== 비교는 어떻게 되나요? (레슨 18)
5. 선택: W=1 parity_chain은 무엇으로 단순해지나요? (레슨 17)
6. 핵심: 테스트 통과로 실제 회로의 hold 조건도 확인했나요? (3장 레슨 12)

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0입니다. 리셋이 최우선입니다.</p>
<p>2. 아닙니다. 다음 값을 저장하는 추가 단계가 생겨 에지별 행동이 달라집니다.</p>
<p>3. always_ff가 나타내는 플립플롭의 의도한 유지 동작이기 때문입니다.</p>
<p>4. 기대값이 정상 0 또는 1이면 불일치로 검출합니다.</p>
<p>5. 입력 a[0]을 출력하는 연결입니다.</p>
<p>6. 아닙니다. 실제 clock-to-Q·최단 경로·hold 요구와 스큐를 따로 검사해야 합니다.</p>
</details>

## 다음으로 이어가기

5장 디지털 구성 요소에서는 산술 회로·시프터·메모리 등 재사용 블록을 이 언어로 표현합니다. 다음 챕터의 첫 레슨은 반가산기·전가산기부터 시작합니다. 회로를 먼저 이해하고 코드를 읽으며, 명세에서 독립적인 검사를 만든다는 순서를 이어갑니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.10 및 4.1–4.9 종합, 인쇄 pp. 171–222 / PDF pp. 192–243. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
