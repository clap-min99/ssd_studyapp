## 이번 레슨의 목표

연산 선택표를 정의하고 공유 덧셈기와 출력 MUX로 ALU의 데이터 흐름을 추적합니다.

## 앞에서 배운 내용

2장의 MUX와 4장의 case를 이용하면 여러 연산 결과 중 하나를 고를 수 있습니다.

## 계산 경로와 선택 경로를 나눈다

산술 논리 장치(arithmetic/logic unit, ALU)는 같은 입력에 여러 연산을 제공하는 블록입니다. 여기서는 4비트 입력·출력과 2비트 op를 사용합니다.

| op | 기능 |
| --- | --- |
| 00 | A+B의 하위 4비트 |
| 01 | A−B의 하위 4비트 |
| 10 | 비트 AND |
| 11 | 비트 OR |

```systemverilog
module ch5_alu4(input logic [3:0] a, b, input logic [1:0] op,
                output logic [3:0] result);
  logic [3:0] bx, sum;
  logic carry;
  assign bx = b ^ {4{op[0]}};
  assign {carry,sum} = {1'b0,a}+{1'b0,bx}+{4'b0000,op[0]};
  always_comb begin
    case (op)
      2'b00, 2'b01: result = sum;
      2'b10: result = a & b;
      2'b11: result = a | b;
      default: result = '0;
    endcase
  end
endmodule
```

op[0]=1이면 B를 반전하고 1을 더하므로 산술 경로는 뺄셈을 계산합니다. op=11에서도 이 경로는 뺄셈을 계산할 수 있지만 출력 MUX가 OR를 선택하므로 sum은 출력에 쓰이지 않습니다. 논리 연산에는 반전한 bx가 아니라 원래 b를 사용합니다.

조합 경로들은 동시에 존재하며 case의 네 분기가 네 클록에 실행되는 것은 아닙니다. 실제 합성에서는 목표 기술과 제약에 따라 공유·최적화가 달라질 수 있습니다. 이 모듈은 결과만 내며 다음 레슨에서 결과의 특성을 알리는 플래그를 정의합니다.

<svg viewBox="0 0 450 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-7-study-t c5-7-study-d">
<title id="c5-7-study-t">공유산술과 병렬 논리 경로를 고르는 ALU</title>
<desc id="c5-7-study-d">A·B는 산술·AND·OR 경로의 입력입니다. 산술 경로는 op[0]으로 덧셈/뺄셈을 선택하고 출력 MUX는 op[1:0]으로 세 후보 중 기능을 고릅니다. 4비트 데이터 경로 기능도입니다.</desc>
<rect x="120" y="30" width="125" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="57.5" font-size="15" text-anchor="middle" fill="var(--ink)">ADD / SUB</text><rect x="120" y="105" width="125" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="132.5" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><rect x="120" y="180" width="125" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="207.5" font-size="15" text-anchor="middle" fill="var(--ink)">OR</text><rect x="330" y="65" width="75" height="140" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="367.5" y="140.0" font-size="15" text-anchor="middle" fill="var(--ink)">MUX</text><path d="M20 125 H65 V52 H120 M65 125 H120 M65 125 V202 H120 M245 52 H290 V90 H330 M245 128 H330 M245 202 H290 V180 H330 M405 135 H435 M368 240 V205" fill="none" stroke="var(--ink)" stroke-width="2"/><circle cx="65" cy="125" r="3" fill="var(--ink)"/><text x="30" y="110" font-size="14" text-anchor="middle" fill="var(--ink)">A·B</text><text x="368" y="260" font-size="14" text-anchor="middle" fill="var(--ink)">op[1:0]</text><text x="182" y="20" font-size="13" text-anchor="middle" fill="var(--ink)">op[0]</text><text x="425" y="115" font-size="12" text-anchor="middle" fill="var(--ink)">result</text>
</svg>
<p class="diagram-caption">그림 5-7. A·B는 산술·AND·OR 경로의 입력입니다. 산술 경로는 op[0]으로 덧셈/뺄셈을 선택하고 출력 MUX는 op[1:0]으로 세 후보 중 기능을 고릅니다. 4비트 데이터 경로 기능도입니다.</p>

## 연산 하나를 입력부터 출력 선택까지 따라가기

ALU 코드를 읽을 때는 먼저 op의 의미를 표에 고정한 뒤 각 경로를 따라갑니다. op=01에서는 op[0]=1이라 B를 반전하고 carry-in에 1을 넣습니다. 따라서 sum 경로는 A−B이고 출력 case가 그 sum을 선택합니다. op=10에서는 B를 반전하지 않은 산술 경로가 있어도 출력은 원래 A·B의 AND입니다.

공유되는 것은 덧셈/뺄셈의 가산기이며 논리 AND·OR는 별도 후보를 만듭니다. op=11일 때 내부 산술 결과가 뺄셈이어도 선택되지 않으므로 출력에는 영향이 없습니다. 반대로 논리 경로에 bx를 사용하면 뒤에서 op를 올바르게 골라도 이미 잘못된 함수를 선택하게 됩니다.

조합 ALU의 입력과 op가 바뀌면 출력이 전파 지연 뒤 안정됩니다. 어떤 연산이 가장 느린지에 따라 임계 경로가 달라질 수 있습니다. 연산 결과를 프로세서 상태로 저장하는 레지스터는 이 모듈 밖에 있으므로 ‘ALU가 계산했다’와 ‘결과가 저장됐다’를 구별합니다.

## 따라 풀기

A=0110₂,B=0011₂입니다. op=00이면 6+3=9로 1001, op=01이면 6−3=3으로 0011, op=10이면 0010, op=11이면 0111입니다. unsigned 덧셈은 맞지만 signed에서 6+3=9는 4비트 범위를 넘습니다. 동일한 패턴과 다른 수 해석을 다시 확인합니다.

### 조건을 바꾸어 한 번 더 풀기

A=1001,B=0110에 대해 모든 op를 추적합니다.

| op | bx | 산술 sum | 출력이 고른 경로 | result |
| --- | --- | --- | --- | --- |
| 00 | 0110 | 1111 | 덧셈 | 1111 |
| 01 | 1001 | 0011 | 뺄셈 | 0011 |
| 10 | 0110 | 1111 | A AND B | 0000 |
| 11 | 1001 | 0011 | A OR B | 1111 |

뺄셈의 확장 합은 10011이며 표의 sum은 하위 4비트입니다. op=11에서 sum과 result가 다른 것이 오류가 아니라 선택 회로의 정상 동작입니다.

### 실습: 모든 4비트 입력과 연산 코드 검사하기

아래 테스트벤치는 16×16×4=1024개 조합을 열거합니다. 기대 산술값은 넓은 정수로 먼저 구한 뒤 하위 네 비트만 비교합니다. 논리 연산은 명세표의 AND·OR와 대조합니다. 4장 레슨18의 내보내기 도구를 사용하면 이 코드도 `lessons.sv`에 포함되며 최상위를 `tb_ch5_alu4`로 선택합니다.

```systemverilog
module tb_ch5_alu4;
  timeunit 1ns;
  timeprecision 1ps;
  logic [3:0] a, b, result;
  logic [1:0] op;
  integer expected;
  ch5_alu4 dut(.a(a), .b(b), .op(op), .result(result));
  initial begin
    for (int av=0; av<16; av=av+1)
      for (int bv=0; bv<16; bv=bv+1)
        for (int fn=0; fn<4; fn=fn+1) begin
          a=av[3:0]; b=bv[3:0]; op=fn[1:0];
          case (fn)
            0: expected=av+bv;
            1: expected=av-bv;
            2: expected=av & bv;
            default: expected=av | bv;
          endcase
          #1;
          if (result !== expected[3:0])
            $fatal(1, "a=%0d b=%0d op=%0d got=%b want=%b",
                   av, bv, fn, result, expected[3:0]);
        end
    $display("PASS: 1024 ALU vectors");
    $finish;
  end
endmodule
```

기대 완료 로그는 `PASS: 1024 ALU vectors`입니다. 본문 ALU는 플래그를 출력하지 않으므로 이 검사는 carry·signed overflow를 검사하지 않습니다. 그 질문은 다음 레슨의 독립 플래그 계산과 연결하세요. 실습 사본에서 OR 경로를 `a | bx`로 바꾸면 앞 적용 문제의 반례가 실제 실패로 나타나는지 확인할 수 있습니다.

## 헷갈리기 쉬운 점

조합 ALU 자체에는 저장이 없습니다. op가 X일 때의 default는 시뮬레이션의 완전 할당을 위한 것이며 실제 회로에 X 판별기가 생기는 것은 아닙니다.

## 직접 확인하기

1. op=11의 OR에 bx를 쓰면 왜 틀리나요?
2. ALU 결과를 다음 주기까지 유지하려면?
3. A=0101,B=1010,op=10이면?

<details>
<summary>정답과 해설 보기</summary>
<p>1. A OR B 대신 A OR NOT B를 계산하기 때문입니다.</p>
<p>2. 출력에 레지스터를 둡니다.</p>
<p>3. 0000입니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

op=11일 때만 틀리고 다른 연산은 맞는 ALU가 있습니다. OR 경로가 `a | bx`로 작성됐다고 가정하고 이를 드러내는 A·B를 고르세요. 내부 bx와 기대/실제 출력을 모두 구하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>A=0000,B=0011을 고르면 op[0]=1이라 bx=1100입니다. 기대 A OR B는 0011이지만 잘못된 A OR bx는 1100입니다.</p>
<p>A=1111 같은 입력은 두 OR 결과가 모두 1111이어서 오류를 숨깁니다. 잘못 반전된 비트가 최종 출력에서 가려지지 않는 값을 골라야 합니다.</p>
</details>

## 다음으로 이어가기

다음에는 영·부호·캐리·오버플로를 함께 읽습니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.4, 인쇄 pp. 247–248 / PDF pp. 268–269. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
