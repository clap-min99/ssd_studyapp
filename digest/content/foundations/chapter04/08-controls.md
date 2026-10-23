## 이번 레슨의 목표

동기·비동기 리셋의 코드를 비교하고 reset > enable > 유지 순서로 레지스터를 추적합니다.

## 앞에서 배운 내용

3장 레슨 4의 동기식 리셋은 클록 에지에서만 반영되고 비동기 리셋의 활성화는 클록을 기다리지 않았습니다.

## if의 위치와 사건 목록이 의미를 정한다

아래 두 모듈은 별개 이름으로 비교합니다. reset은 active-high이고 en=1일 때만 새 데이터를 저장합니다.

```systemverilog
module reg_sync(input logic clk, reset, en,
                input logic [2:0] d,
                output logic [2:0] q);
  always_ff @(posedge clk)
    if (reset) q <= '0;
    else if (en) q <= d;
endmodule

module reg_async(input logic clk, reset, en,
                 input logic [2:0] d,
                 output logic [2:0] q);
  always_ff @(posedge clk or posedge reset)
    if (reset) q <= '0;
    else if (en) q <= d;
endmodule
```

첫 코드는 clk 상승 때만 실행되어 그때 reset을 검사합니다. 둘째는 reset 상승도 사건이므로 클록이 멈춰 있어도 초기화가 활성화됩니다. 두 코드 모두 reset=1이면 en이나 d보다 초기화가 우선합니다. reset=0,en=0에서 할당하지 않는 것은 플립플롭의 유지 동작입니다. 이를 조합논리의 할당 누락과 혼동하지 않습니다.

active-low 비동기 리셋이라면 `negedge reset_n`과 `if (!reset_n)`을 함께 맞춥니다. 극성과 사건을 서로 바꿔 쓰면 의도한 소자가 되지 않습니다. enable을 쓰려는 목적만으로 `clk & en`을 새 클록으로 만들어서는 안 됩니다. 일반 데이터 선택/저장 허용 기술과 실제 클록 게이팅 설계는 구별합니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-8-t c4-8-d">
<title id="c4-8-t">리셋과 Enable: 사건 조건과 우선순위</title>
<desc id="c4-8-d">상승 에지에서의 공통 우선순위를 비교한 개념도입니다. 비동기 버전은 reset 활성화 때에도 첫 조건이 적용됩니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">reset=1</text><text x="75" y="91">q_next=000</text><text x="223" y="63">reset=0·en=1</text><text x="223" y="91">q_next=d</text><text x="371" y="63">reset=0·en=0</text><text x="371" y="91">q_next=q</text></g>
</svg>
<p class="diagram-caption">그림 4-8. 상승 에지에서의 공통 우선순위를 비교한 개념도입니다. 비동기 버전은 reset 활성화 때에도 첫 조건이 적용됩니다.</p>

## 따라 풀기

초기 q=101, d=011, en=0이고 클록 상승이 10ns입니다. reset이 7ns에 1이 되면 비동기 버전은 그 사건의 갱신 후 000, 동기 버전은 10ns까지 101입니다. 10ns에는 둘 다 000입니다. 12ns에 reset=0, en=1, d=110이 되고 다음 상승이 20ns라면 20ns 갱신 후 둘 다 110입니다. reset 해제 자체가 d를 복사하는 사건은 아닙니다.

## 헷갈리기 쉬운 점

비동기 리셋의 해제에는 실제 회로의 recovery/removal 등 시간 조건이 있습니다. 이 RTL 예제는 해제 안전성을 증명하는 회로가 아닙니다. reset=0,en=0에서 else q<=q를 적지 않아도 유지입니다. 반면 reset을 en 안에 넣으면 en=0일 때 리셋되지 않는 다른 우선순위가 됩니다.

## 직접 확인하기

1. reset=en=1이면 어떤 값이 저장되나요?
2. 동기 리셋 펄스가 두 상승 에지 사이에서 끝나면 반드시 잡히나요?
3. active-low 비동기 리셋의 사건 조건은 무엇인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 000입니다. reset 분기가 먼저입니다.</p>
<p>2. 아닙니다. 상승 에지에서 reset이 1이어야 이 코드가 반영합니다.</p>
<p>3. negedge reset_n입니다. 본문에서도 !reset_n으로 활성 상태를 검사합니다.</p>
</details>

## 다음으로 이어가기

다음에는 한 always_ff 안의 여러 레지스터가 같은 에지에서 무엇을 읽는지 확인합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.4.2–4.4.3, 인쇄 pp. 192–194 / PDF pp. 213–215. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
