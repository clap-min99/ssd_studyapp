## 이번 레슨의 목표

두 단계 레지스터의 에지별 값을 추적하고 blocking으로 바꾸면 달라지는 이유를 설명합니다.

## 앞에서 배운 내용

3장의 파이프라인은 단계 경계마다 레지스터를 두었습니다. 새 입력이 같은 에지에 모든 단계를 통과하지 않도록 기술해야 합니다.

## 오른쪽은 갱신 전 값으로 평가한다

```systemverilog
module delay2(input logic clk, reset, d,
              output logic q);
  logic stage1;
  always_ff @(posedge clk) begin
    if (reset) begin
      stage1 <= 1'b0;
      q <= 1'b0;
    end else begin
      stage1 <= d;
      q <= stage1;
    end
  end
endmodule
```

한 always_ff 안에 여러 문장을 넣으므로 `begin/end`로 묶습니다. 상승 에지에서 stage1의 새 값은 직전 d, q의 새 값은 직전 stage1입니다. 첫 문장에서 stage1의 갱신을 예약했어도 둘째 문장의 오른쪽에는 아직 이전 stage1이 있습니다. 이것이 두 플립플롭을 직렬 연결한 동작과 맞습니다.

반대로 `stage1 = d; q = stage1;`처럼 blocking 할당을 쓰면 같은 블록 안에서 첫 갱신이 즉시 보이므로 q도 곧바로 d를 읽습니다. 단계 하나를 잃는 모델이 되거나 시뮬레이션과 의도한 구조가 달라집니다. 순서를 뒤집는 요령 대신 저장 소자는 nonblocking으로 통일합니다.

같은 직렬 구조는 1비트 동기화기의 기능 모델에도 쓰이지만, 위 delay2는 동기 입력의 지연 예제입니다. 아날로그 준안정성, 물리 배치, 동기화기 속성 설정을 검증하지 않았으며 다중 비트 CDC나 짧은 펄스를 해결한다는 뜻도 아닙니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-9-t c4-9-d">
<title id="c4-9-t">여러 레지스터와 Nonblocking: 이전 값 함께 읽기</title>
<desc id="c4-9-d">리셋 후 첫 입력 1이 두 레지스터를 통과하는 에지 관계입니다. E1에서는 q가 이전 stage1=0을 받습니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">입력 d</text><text x="75" y="91">E1 직전 1</text><text x="223" y="63">stage1</text><text x="223" y="91">E1 후 1</text><text x="371" y="63">출력 q</text><text x="371" y="91">E2 후 1</text></g>
</svg>
<p class="diagram-caption">그림 4-9a. 리셋 후 첫 입력 1이 두 레지스터를 통과하는 에지 관계입니다. E1에서는 q가 이전 stage1=0을 받습니다.</p>

<svg viewBox="0 0 450 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-9b-t c4-9b-d">
<title id="c4-9b-t">두 플립플롭의 직렬 연결</title>
<desc id="c4-9b-d">d가 첫 플립플롭의 D로 들어가고 그 Q인 stage1이 둘째 플립플롭의 D에 연결됩니다. 두 클록 핀은 같은 clk에 연결됩니다. reset 연결은 생략했습니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"><rect x="80" y="25" width="90" height="90"/><rect x="265" y="25" width="90" height="90"/></g>
<g stroke="var(--ink)" stroke-width="2" fill="none"><path d="M30 55 H80 M170 55 H265 M355 55 H420 M125 150 V115 M310 150 V115 M40 150 H310 M115 115 L125 103 L135 115 M300 115 L310 103 L320 115"/></g>
<g fill="var(--ink)" font-size="15"><text x="10" y="59">d</text><text x="90" y="59">D</text><text x="145" y="59">Q</text><text x="192" y="43">stage1</text><text x="275" y="59">D</text><text x="330" y="59">Q</text><text x="425" y="59">q</text><text x="13" y="155">clk</text><text x="115" y="90">FF1</text><text x="300" y="90">FF2</text></g>
</svg>
<p class="diagram-caption">그림 4-9b. 코드의 두 저장 신호를 플립플롭 두 개로 그린 기능 회로입니다. reset 배선은 생략했습니다. 동일 에지에서 FF2가 읽는 것은 갱신 전 stage1입니다.</p>

## 따라 풀기

리셋 후 stage1=q=0입니다. reset=0으로 두고 에지 직전 d를 1,0,1 순서로 넣습니다.

| 에지 | 직전 d | 직전 stage1 | 직후 stage1 | 직후 q |
| --- | --- | --- | --- | --- |
| E1 | 1 | 0 | 1 | 0 |
| E2 | 0 | 1 | 0 | 1 |
| E3 | 1 | 0 | 1 | 0 |

각 행의 직후 stage1이 다음 행의 직전 stage1입니다. q는 현재 행의 새 stage1이 아니라 직전 열을 복사합니다. 이 표가 두 저장 단계의 검산 기준입니다.

## 헷갈리기 쉬운 점

nonblocking은 한 클록을 기다린 뒤 할당한다는 뜻이 아닙니다. 현재 에지의 시뮬레이션 갱신 단계에서 반영합니다. 두 줄을 서로 다른 always_ff로 분리해도 같은 클록과 nonblocking을 사용하고 단일 구동을 지키면 같은 동작을 기술할 수 있습니다.

## 직접 확인하기

1. E4 직전 d=0이면 위 표 다음의 stage1,q는 무엇인가요?
2. 두 nonblocking 문장의 나열 순서를 바꾸면 기능이 바뀌나요?
3. 이 코드를 돌려 동기화기의 MTBF를 측정할 수 있나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. stage1=0,q=1입니다. E3 후 stage1=1을 q가 받습니다.</p>
<p>2. 이 예제에서는 바뀌지 않습니다. 서로 다른 왼쪽 신호에 직전 값을 예약합니다.</p>
<p>3. 아닙니다. 일반 RTL 모델은 준안정성의 아날로그 해소 확률을 표현하지 않습니다.</p>
</details>

## 다음으로 이어가기

다음에는 에지가 아니라 레벨에 반응하는 래치를 구별합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.4.4, 4.5.4, 인쇄 pp. 195, 203–207 / PDF pp. 216, 224–228. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
