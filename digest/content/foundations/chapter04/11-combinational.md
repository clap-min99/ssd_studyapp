## 이번 레슨의 목표

blocking 할당으로 중간 값을 계산하고 case의 기본값과 if의 우선순위를 설명합니다.

## 앞에서 배운 내용

레슨 10에서 조합논리의 모든 경로를 채워야 함을 배웠습니다. 긴 진리표나 우선순위 조건은 식 한 줄보다 절차 블록이 읽기 좋습니다.

## 블록 안의 계산 순서와 회로의 병렬성을 함께 본다

간단한 식에는 assign을 사용하고, 여러 조건과 중간 계산에는 always_comb를 사용합니다. 아래 status_led는 2비트 상태 코드를 3비트 LED 패턴으로 바꿉니다. LED는 active-high, 순서는 [2:0]입니다.

```systemverilog
module status_led(input logic [1:0] code,
                  output logic [2:0] led);
  always_comb begin
    case (code)
      2'b00: led = 3'b001;
      2'b01: led = 3'b010;
      2'b10: led = 3'b100;
      default: led = 3'b000;
    endcase
  end
endmodule
```

`case`는 입력과 항목을 비교해 맞는 분기를 고릅니다. 11과 X·Z가 들어간 패턴은 위의 정확한 case 항목과 맞지 않으므로 default로 갑니다. 실제 회로에서 X를 판별하는 소자가 합성된다는 뜻은 아닙니다. 기본값을 먼저 할당하고 일부 분기에서 덮어쓰는 방식도 가능합니다. 모든 출력이 모든 경로에서 정의되어야 합니다.

우선순위 회로는 `if (req[2]) grant=3'b100; else if (req[1]) grant=3'b010; else if (req[0]) grant=3'b001; else grant=3'b000;`으로 쓸 수 있습니다. req[2]가 가장 높습니다. 이는 always_comb 안에 넣는 문장이며 독립 if 세 개와는 덮어쓰기 순서가 다릅니다.

조합 블록의 중간 신호는 blocking `=`로 의존 순서에 맞춰 계산합니다. 예를 들어 `t = a ^ b; y = t & en;`이면 같은 평가에서 새 t를 읽습니다. 문장 순서를 바꾸면 y가 이전 t를 볼 수 있습니다. always_comb에서 쓴 변수가 스스로 변했다고 블록이 반복 평가되어 문제를 고쳐준다고 가정하지 않습니다. 각 조합 블록은 입력에서 출력 방향으로 읽히게 작성합니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-11-t c4-11-d">
<title id="c4-11-t">Always_comb·Case·If: 모든 입력에 출력 정하기</title>
<desc id="c4-11-d">상태 코드별 LED 출력을 묶어 나타낸 진리표 개념도입니다. 저장 소자는 없습니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">code=00</text><text x="75" y="91">led=001</text><text x="223" y="63">code=01</text><text x="223" y="91">led=010</text><text x="371" y="63">code=10 / 11</text><text x="371" y="91">led=100 / 000</text></g>
</svg>
<p class="diagram-caption">그림 4-11. 상태 코드별 LED 출력을 묶어 나타낸 진리표 개념도입니다. 저장 소자는 없습니다.</p>

## 따라 풀기

code=01이면 두 번째 case 항목과 일치해 led=010입니다. code를 11로 바꾸면 default에서 000을 받습니다. default를 없애면 11일 때 새 값이 없어 직전 010을 유지하는 잘못된 저장 동작이 생길 수 있습니다. 별도 우선순위 예제의 req=011에서는 req[2]=0,req[1]=1이므로 grant=010이며 req[0]도 1이라는 사실은 낮은 우선순위라 무시됩니다.

## 헷갈리기 쉬운 점

case가 항상 ROM이라는 뜻은 아닙니다. 도구와 대상 기술에 따라 게이트·MUX·LUT 등으로 구현할 수 있습니다. always_comb에서는 신호 변경에 대한 자동 감지를 활용하고, 예전 always @(a,b) 코드에서는 감지 목록 누락도 점검합니다. nonblocking으로 중간 값을 계산하며 재평가에 기대는 방식은 피합니다.

## 직접 확인하기

1. status_led에서 code=10,11일 때 출력은 각각 무엇인가요?
2. req=101이면 우선순위 출력은 무엇인가요?
3. t=a^b; y=t&en;을 역순으로 쓰면 왜 위험한가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 100,000입니다. 둘 다 값이 정해져 있습니다.</p>
<p>2. 100입니다. req[2]가 req[0]보다 높습니다.</p>
<p>3. blocking 문장은 순서대로 보이므로 y가 이번 평가에서 아직 갱신하지 않은 t를 사용할 수 있습니다.</p>
</details>

## 다음으로 이어가기

다음에는 와일드카드로 입력 조건을 묶을 때 지켜야 할 경계를 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.5–4.5.2, 4.5.4, 인쇄 pp. 197–206 / PDF pp. 218–227. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
