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

<svg viewBox="0 0 450 270" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-13-study-t c4-13-study-d">
<title id="c4-13-study-t">FSM의 다음 상태 계산과 상태 저장의 피드백</title>
<desc id="c4-13-study-d">현재 state와 start·finish가 다음 상태 논리로 들어갑니다. next_state가 클록 에지에서 상태 레지스터에 저장되고 state가 다시 계산 입력으로 돌아갑니다. done은 현재 state의 별도 디코드입니다.</desc>
<rect x="75" y="100" width="120" height="65" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="135.0" y="137.5" font-size="15" text-anchor="middle" fill="var(--ink)">다음 상태</text><rect x="275" y="100" width="105" height="65" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="327.5" y="137.5" font-size="15" text-anchor="middle" fill="var(--ink)">상태 FF</text><rect x="275" y="20" width="105" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="327.5" y="47.5" font-size="15" text-anchor="middle" fill="var(--ink)">== DONE</text><path d="M25 120 H75 M25 145 H75 M195 130 H275 M380 130 H420 V240 H50 V160 H75 M325 80 V100 M400 130 V42 H380 M275 42 H230" fill="none" stroke="var(--ink)" stroke-width="2"/><circle cx="400" cy="130" r="3" fill="var(--ink)"/><text x="45" y="90" font-size="14" text-anchor="middle" fill="var(--ink)">입력</text><text x="233" y="115" font-size="12" text-anchor="middle" fill="var(--ink)">next_state</text><text x="240" y="230" font-size="14" text-anchor="middle" fill="var(--ink)">state 피드백</text><text x="325" y="78" font-size="14" text-anchor="middle" fill="var(--ink)">clk</text><text x="230" y="30" font-size="13" text-anchor="middle" fill="var(--ink)">done</text>
</svg>
<p class="diagram-caption">그림 4-13a. 현재 state와 start·finish가 다음 상태 논리로 들어갑니다. next_state가 클록 에지에서 상태 레지스터에 저장되고 state가 다시 계산 입력으로 돌아갑니다. done은 현재 state의 별도 디코드입니다.</p>

<svg viewBox="0 0 460 240" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-13b-t c4-13b-d">
<title id="c4-13b-t">작업 완료 표시기의 상태 전이</title>
<desc id="c4-13b-d">동기 리셋은 IDLE로 갑니다. IDLE은 start=1에서 RUN으로, RUN은 finish=1에서 DONE으로 갑니다. DONE은 다음 에지에 IDLE로 돌아갑니다. IDLE의 start=0과 RUN의 finish=0은 자기 상태를 유지합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"><circle cx="75" cy="100" r="40"/><circle cx="225" cy="100" r="40"/><circle cx="380" cy="100" r="40"/></g>
<g stroke="var(--ink)" stroke-width="2" fill="none"><path d="M115 100 H185 M175 94 L185 100 L175 106 M265 100 H340 M330 94 L340 100 L330 106 M380 140 V185 H75 V140 M69 150 L75 140 L81 150 M75 25 V60 M69 50 L75 60 L81 50"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="96">IDLE</text><text x="75" y="116">done=0</text><text x="225" y="96">RUN</text><text x="225" y="116">done=0</text><text x="380" y="96">DONE</text><text x="380" y="116">done=1</text><text x="150" y="83">start=1</text><text x="302" y="83">finish=1</text><text x="225" y="207">다음 에지·무조건 복귀</text><text x="75" y="18">reset</text></g>
</svg>
<p class="diagram-caption">그림 4-13b. 조건은 상승 에지에서 읽습니다. 가독성을 위해 start=0인 IDLE의 자기 고리와 finish=0인 RUN의 자기 고리는 생략했습니다.</p>

## 명세를 완전한 상태표로 만든 뒤 코드와 대조하기

FSM을 코딩하기 전에는 각 상태에서 어떤 입력을 실제로 읽는지 표시합니다. IDLE은 start만, RUN은 finish만 읽습니다. DONE에서는 입력을 보지 않고 IDLE로 돌아갑니다. 이렇게 명세를 정하면 start=finish=1을 만났을 때도 한 에지에 어디까지 진행하는지 분명해집니다.

| 현재 상태 | 조건 | 다음 상태 | 현재 done |
| --- | --- | --- | --- |
| IDLE | start=0 | IDLE | 0 |
| IDLE | start=1 | RUN | 0 |
| RUN | finish=0 | RUN | 0 |
| RUN | finish=1 | DONE | 0 |
| DONE | 모든 정상 입력 | IDLE | 1 |

이 표의 ‘다음 상태’가 always_comb이고, 그 결과를 다음 상승 에지에 state로 옮기는 것이 always_ff입니다. 현재 done 열은 assign의 현재 상태 디코드입니다. 세 블록을 표의 각 열과 대응시키면 state와 next_state를 뒤바꾼 코드를 찾기 쉽습니다. reset=1인 에지의 IDLE 강제는 표보다 우선하는 초기화 계약입니다.

## 따라 풀기

리셋 직후 IDLE,done=0입니다. E1 직전 start=finish=1이면 E1 후 RUN,done=0입니다. E2 직전 start=0,finish=1이면 E2 후 DONE,done=1입니다. E3 후에는 입력과 관계없이 IDLE,done=0입니다. done은 두 번째 에지 후부터 세 번째 에지 후까지 한 주기 활성입니다. 상태표를 이 순서와 대조하면 start와 finish를 같은 에지에 처리한 잘못된 구현을 찾을 수 있습니다.

### 조건을 바꾸어 한 번 더 풀기

start가 계속 1이고 finish도 계속 1이라고 합시다. 리셋 이후 각 에지 직후 상태는 RUN,DONE,IDLE,RUN,DONE,IDLE로 반복됩니다. 첫 RUN은 start를 받아서, DONE은 직전 RUN이 finish를 받아서 생깁니다. DONE에서 IDLE로 복귀한 그 에지에 start를 다시 읽어 RUN으로 곧바로 넘어가지는 않습니다.

반대로 finish가 RUN에 들어오기 전 잠깐 1이었다가 사라지면 이 FSM은 그 과거 사건을 기억하지 않습니다. ‘완료 펄스를 언제 허용하는가’도 인터페이스 명세에 필요하며, 코드를 고치기 전에 외부 입력의 유효 시점을 정해야 합니다.

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

### 적용 문제: 직접 구성하고 이유 설명하기

리셋 후 start 입력열은 1,0,1,1이고 finish는 0,1,1,0입니다. 네 에지 직후 상태와 done을 구하세요. 마지막 에지의 start=1이 무시되는지 여부도 설명하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>E1 후 RUN/0, E2 후 DONE/1, E3 후 IDLE/0, E4 후 RUN/0입니다.</p>
<p>E3에서는 직전 상태가 DONE이므로 start=1을 사용하지 않고 IDLE로 돌아갑니다. E4에서는 직전 상태가 IDLE이므로 start=1을 받아 RUN으로 갑니다. 같은 입력값도 현재 상태에 따라 역할이 달라집니다.</p>
</details>

## 다음으로 이어가기

다음에는 같은 패턴 검출을 Moore와 Mealy로 기술해 출력 시점을 비교합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.6, 인쇄 pp. 207–209 / PDF pp. 228–230. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
