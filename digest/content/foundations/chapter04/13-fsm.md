## 이번 레슨의 목표

열거형으로 상태를 정의하고 세 블록 구조의 Moore FSM을 상태표와 대조합니다.

## 앞에서 배운 내용

3장에서는 명세에서 상태도와 상태표를 만들었습니다. HDL에서도 먼저 상태의 뜻을 정하고 그 표를 코드로 옮깁니다.

## 작업 완료 표시기를 세 블록으로 나눈다

명세는 다음과 같습니다. IDLE에서 start=1을 샘플하면 RUN으로 갑니다. RUN에서 finish=1을 샘플하면 DONE으로 갑니다. DONE에서는 다음 에지에 IDLE로 돌아갑니다. done은 DONE 상태에서만 1입니다. reset은 active-high 동기식이며 start·finish는 클록에 맞춰 준비된 입력입니다.

```systemverilog
module job_fsm(input logic clk, reset, start, finish,
               output logic done);
  typedef enum logic [1:0] {IDLE=2'b00, RUN=2'b01,
                            DONE=2'b10} state_t;
  state_t state, next_state;
  always_ff @(posedge clk)
    if (reset) state <= IDLE;
    else state <= next_state;

  always_comb begin
    next_state = IDLE;
    case (state)
      IDLE: if (start) next_state = RUN;
            else next_state = IDLE;
      RUN:  if (finish) next_state = DONE;
            else next_state = RUN;
      DONE: next_state = IDLE;
      default: next_state = IDLE;
    endcase
  end
  assign done = (state == DONE);
endmodule
```

`typedef enum`은 상태 값에 이름을 붙인 자료형을 만듭니다. state는 저장된 현재 상태, next_state는 현재 상태와 입력에서 계산한 다음 값입니다. 상태 레지스터만 `<=`, 조합 블록은 `=`를 사용합니다. done은 현재 상태만 보므로 Moore 출력입니다. start와 finish가 동시에 1이어도 현재 IDLE이면 RUN까지만 이동합니다. 한 에지에 두 상태를 연달아 지나가지 않습니다.

2비트의 남는 코드 11은 default에서 IDLE로 복귀하도록 RTL에 기술했습니다. 실제 합성 시 FSM 재인코딩이나 불법 상태 최적화 정책은 도구에 따라 달라지므로 물리적인 오류 복구 보장이 필요하면 별도의 구현 검증이 필요합니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-13-t c4-13-d">
<title id="c4-13-t">FSM 기술: 상태 레지스터·다음 상태·출력</title>
<desc id="c4-13-d">job_fsm의 전이 조건을 요약한 상태 개념도입니다. IDLE의 start=0과 RUN의 finish=0은 자기 상태를 유지합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">IDLE</text><text x="75" y="91">start=1 → RUN</text><text x="223" y="63">RUN</text><text x="223" y="91">finish=1 → DONE</text><text x="371" y="63">DONE</text><text x="371" y="91">다음 에지 IDLE</text></g>
</svg>
<p class="diagram-caption">그림 4-13a. job_fsm의 전이 조건을 요약한 상태 개념도입니다. IDLE의 start=0과 RUN의 finish=0은 자기 상태를 유지합니다.</p>

<svg viewBox="0 0 460 240" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-13b-t c4-13b-d">
<title id="c4-13b-t">작업 완료 표시기의 상태 전이</title>
<desc id="c4-13b-d">동기 리셋은 IDLE로 갑니다. IDLE은 start=1에서 RUN으로, RUN은 finish=1에서 DONE으로 갑니다. DONE은 다음 에지에 IDLE로 돌아갑니다. IDLE의 start=0과 RUN의 finish=0은 자기 상태를 유지합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"><circle cx="75" cy="100" r="40"/><circle cx="225" cy="100" r="40"/><circle cx="380" cy="100" r="40"/></g>
<g stroke="var(--ink)" stroke-width="2" fill="none"><path d="M115 100 H185 M175 94 L185 100 L175 106 M265 100 H340 M330 94 L340 100 L330 106 M380 140 V185 H75 V140 M69 150 L75 140 L81 150 M75 25 V60 M69 50 L75 60 L81 50"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="96">IDLE</text><text x="75" y="116">done=0</text><text x="225" y="96">RUN</text><text x="225" y="116">done=0</text><text x="380" y="96">DONE</text><text x="380" y="116">done=1</text><text x="150" y="83">start=1</text><text x="302" y="83">finish=1</text><text x="225" y="207">다음 에지·무조건 복귀</text><text x="75" y="18">reset</text></g>
</svg>
<p class="diagram-caption">그림 4-13b. 조건은 상승 에지에서 읽습니다. 가독성을 위해 start=0인 IDLE의 자기 고리와 finish=0인 RUN의 자기 고리는 생략했습니다.</p>

## 따라 풀기

리셋 직후 IDLE,done=0입니다. E1 직전 start=finish=1이면 E1 후 RUN,done=0입니다. E2 직전 start=0,finish=1이면 E2 후 DONE,done=1입니다. E3 후에는 입력과 관계없이 IDLE,done=0입니다. done은 두 번째 에지 후부터 세 번째 에지 후까지 한 주기 활성입니다. 상태표를 이 순서와 대조하면 start와 finish를 같은 에지에 처리한 잘못된 구현을 찾을 수 있습니다.

## 헷갈리기 쉬운 점

next_state는 별도 저장 신호가 아닙니다. next_state를 always_ff에서 갱신하면 추가 지연을 만드는 다른 설계가 됩니다. 상태 enum에 이름이 세 개 있다고 플립플롭이 반드시 세 개인 것은 아닙니다. 이 RTL 표현은 2비트이며 합성기는 다른 인코딩을 선택할 수 있습니다.

## 직접 확인하기

1. RUN에서 start=1,finish=0이면 다음 상태는 무엇인가요?
2. DONE에서 start=1이면 곧바로 RUN으로 가나요?
3. done을 Moore 출력이라 부르는 이유는 무엇인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. RUN을 유지합니다. RUN에서는 start를 사용하지 않습니다.</p>
<p>2. 아닙니다. 명세상 IDLE로 돌아가고 이후 에지에서 start를 다시 읽습니다.</p>
<p>3. 출력이 state만의 함수이기 때문입니다.</p>
</details>

## 다음으로 이어가기

다음에는 같은 패턴 검출을 Moore와 Mealy로 기술해 출력 시점을 비교합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.6, 인쇄 pp. 207–209 / PDF pp. 228–230. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
