## 이번 레슨의 목표

같은 입력열을 두 FSM에 적용하고 에지 직전 Mealy 출력과 에지 직후 Moore 출력을 구별합니다.

## 앞에서 배운 내용

3장 레슨 9의 10 검출기를 코드로 옮깁니다. x는 각 상승 에지 전에 안정되는 동기 입력이며 리셋 뒤부터 읽은 연속 두 비트가 10인지 봅니다.

## 출력을 언제 읽는지도 명세다

Moore 상태는 WAIT(직전 1 없음), ONE(직전 1), HIT(방금 10 검출)입니다. ONE에서 x=0이면 HIT, HIT에서는 x=1이면 ONE 아니면 WAIT로 갑니다.

```systemverilog
module detect10_moore(input logic clk, reset, x,
                      output logic hit);
  typedef enum logic [1:0] {WAIT, ONE, HIT} state_t;
  state_t state, ns;
  always_ff @(posedge clk)
    if (reset) state <= WAIT;
    else state <= ns;
  always_comb begin
    ns = WAIT;
    case (state)
      WAIT: if (x) ns = ONE; else ns = WAIT;
      ONE:  if (x) ns = ONE; else ns = HIT;
      HIT:  if (x) ns = ONE; else ns = WAIT;
      default: ns = WAIT;
    endcase
  end
  assign hit = (state == HIT);
endmodule

module detect10_mealy(input logic clk, reset, x,
                      output logic hit);
  logic prev_one;
  always_ff @(posedge clk)
    if (reset) prev_one <= 1'b0;
    else prev_one <= x;
  assign hit = prev_one & ~x;
endmodule
```

Mealy의 prev_one은 직전 샘플이 1이었는지 나타냅니다. 현재 x가 0으로 바뀌면 에지를 기다리지 않고 hit가 켜질 수 있습니다. 두 구현은 검출 의미는 같지만 출력 파형은 같지 않습니다. 리셋은 동기식이므로 첫 리셋 에지 전에 출력을 유효하다고 가정하지 않습니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-14-t c4-14-d">
<title id="c4-14-t">Moore와 Mealy 코드: 10 검출의 관측 시점</title>
<desc id="c4-14-d">10을 완성하는 두 번째 입력 0 주위의 출력 관측 순서입니다. Mealy는 에지 직전, Moore는 에지의 갱신 후를 비교합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">직전 샘플=1</text><text x="75" y="91">ONE / prev_one=1</text><text x="223" y="63">이번 x=0</text><text x="223" y="91">직전 Mealy hit=1</text><text x="371" y="63">에지 갱신 후</text><text x="371" y="91">Moore HIT·hit=1</text></g>
</svg>
<p class="diagram-caption">그림 4-14. 10을 완성하는 두 번째 입력 0 주위의 출력 관측 순서입니다. Mealy는 에지 직전, Moore는 에지의 갱신 후를 비교합니다.</p>

## 같은 검출 사건을 두 관찰 창으로 읽기

10 검출의 의미는 ‘이번 에지에서 읽는 x가 0이고 직전 샘플이 1’입니다. Mealy는 직전 샘플을 저장한 prev_one과 현재 입력 x로 조건을 만들므로 x가 준비된 에지 이전부터 hit가 켜질 수 있습니다. Moore는 그 에지에서 HIT 상태에 들어간 뒤 hit를 켭니다.

따라서 비교 기준은 에지 직전 Mealy와 갱신 후 Moore입니다. 둘의 파형을 같은 순간에만 비교해 불일치라고 판단하면 안 됩니다. 출력이 다음 단계 레지스터의 enable로 쓰인다면 그 레지스터가 어느 에지에서 어느 값을 읽는지까지 검토해야 합니다.

입력 x가 에지 사이에 흔들리면 Mealy hit도 따라 바뀔 수 있습니다. 이 회로는 입력이 에지 전에 안정되는 동기 신호라는 전제를 가집니다. Moore는 상태에만 의존해 입력의 직접 경로가 없지만, 실제 다중 상태 비트의 전환과 출력 디코드 지연까지 없는 것은 아닙니다. 기능 시점과 물리 글리치를 구별합니다.

## 따라 풀기

리셋 후 입력 1,1,0,0을 네 에지에 넣습니다.

| 에지 | x | 직전 prev_one | 직전 Mealy hit | 직후 Moore 상태 | 직후 Moore hit |
| --- | --- | --- | --- | --- | --- |
| E1 | 1 | 0 | 0 | ONE | 0 |
| E2 | 1 | 1 | 0 | ONE | 0 |
| E3 | 0 | 1 | 1 | HIT | 1 |
| E4 | 0 | 0 | 0 | WAIT | 0 |

E3의 갱신 후 Mealy prev_one은 0이 되어 hit는 꺼집니다. Moore hit는 HIT에 머무는 다음 주기 동안 켜집니다. 두 출력을 모두 에지 직후에만 비교하면 같은 파형이어야 한다고 잘못 판단할 수 있습니다.

### 조건을 바꾸어 한 번 더 풀기

리셋 후 1,0,1,0을 입력하면 검출 사건은 두 번째와 네 번째 에지입니다.

| 에지 | x | 직전 prev_one | 직전 Mealy | 직후 Moore | 직후 Mealy |
| --- | --- | --- | --- | --- | --- |
| E1 | 1 | 0 | 0 | 0 | 0 |
| E2 | 0 | 1 | 1 | 1 | 0 |
| E3 | 1 | 0 | 0 | 0 | 0 |
| E4 | 0 | 1 | 1 | 1 | 0 |

에지 직후 x는 표의 값을 그대로 유지한다고 가정했습니다. Mealy의 prev_one이 이번 x로 갱신되면서 직전 검출 조건은 사라지고, Moore는 HIT 상태로 그 결과를 한 주기 유지합니다.

## 헷갈리기 쉬운 점

Mealy 출력은 조합 경로로 입력 변화에 반응하므로 글리치와 외부 샘플 시점을 검토해야 합니다. Moore도 여러 상태 비트가 바뀌는 실제 출력 디코드에서 무조건 글리치가 없다고 보장하지 않습니다. 비동기 입력을 직접 넣어도 된다는 뜻이 아닙니다.

## 직접 확인하기

1. 입력 1,0,1,0에서 Moore hit가 켜지는 에지는 언제인가요?
2. Mealy에서 prev_one=1,x=0인 에지 직후 hit는 왜 꺼질 수 있나요?
3. Moore와 Mealy 출력이 같은 사건을 검출하면 파형도 반드시 같나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 두 번째와 네 번째 에지 갱신 후입니다.</p>
<p>2. 그 에지에서 prev_one이 현재 x=0으로 갱신되어 조합식이 0이 되기 때문입니다.</p>
<p>3. 아닙니다. 출력의 입력 의존성과 관측 시점이 다릅니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

10을 검출할 때 두 구현의 출력을 모두 상승 에지 직후에만 읽었더니 Mealy가 항상 0입니다. 검출기가 잘못되었다고 결론내리기 전에 테스트의 관찰 시점을 어떻게 바꿔야 하나요?

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>x를 이전 하강 에지에 준비한 뒤 다음 상승 에지 직전에 Mealy 조건을 기록하고, 상승 에지의 nonblocking 갱신이 반영된 뒤 Moore 출력을 기록합니다. 각 기록이 어떤 입력 쌍에 대한 것인지 함께 적습니다.</p>
<p>Mealy 출력을 다음 에지 이후에도 유지해야 한다는 요구라면 출력 등록 등 회로 계약을 바꿔야 합니다. 관찰 시점 오류와 출력 유지 요구를 분리해야 합니다.</p>
</details>

## 다음으로 이어가기

다음 두 레슨의 자료형·매개변수는 선택 심화입니다. 핵심 흐름만 공부한다면 레슨 18 테스트벤치로 이어가도 됩니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.6, 인쇄 pp. 209–211 / PDF pp. 230–232. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
