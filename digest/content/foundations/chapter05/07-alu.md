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

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-7-t c5-7-d">
<title id="c5-7-t">ALU: 산술·논리 연산을 고르는 회로</title>
<desc id="c5-7-d">공유 산술 경로와 병렬 논리 경로가 출력 선택기로 모이는 기능 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">산술 경로</text><text x="75" y="87">A + 선택한 B + C</text><text x="223" y="59">논리 경로</text><text x="223" y="87">A AND B·A OR B</text><text x="371" y="59">출력 MUX</text><text x="371" y="87">op로 하나 선택</text></g>
</svg>
<p class="diagram-caption">그림 5-7. 공유 산술 경로와 병렬 논리 경로가 출력 선택기로 모이는 기능 개념도입니다.</p>

## 따라 풀기

A=0110₂,B=0011₂입니다. op=00이면 6+3=9로 1001, op=01이면 6−3=3으로 0011, op=10이면 0010, op=11이면 0111입니다. unsigned 덧셈은 맞지만 signed에서 6+3=9는 4비트 범위를 넘습니다. 동일한 패턴과 다른 수 해석을 다시 확인합니다.

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

## 다음으로 이어가기

다음에는 영·부호·캐리·오버플로를 함께 읽습니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.4, 인쇄 pp. 247–248 / PDF pp. 268–269. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
