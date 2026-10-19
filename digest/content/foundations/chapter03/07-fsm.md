## 이번 레슨의 목표

작은 제어기의 명세를 상태도·전이표·출력식·다음 상태식으로 바꾸고, 한 클록씩 검산합니다.

## 앞에서 배운 내용

동기식 회로는 조합논리와 상태 레지스터로 나눕니다. 유한 상태 머신(finite state machine, FSM)은 유한한 상태 집합과 입력에 따라 다음 상태와 출력을 결정하는 모델입니다. k개 상태 비트는 최대 2ᵏ개의 조합을 나타내며 실제로 모두 사용할 필요는 없습니다.

## 예제 명세: 작업 완료 표시기

동기화된 1비트 입력 start와 done을 받아 다음처럼 동작하는 교육용 제어기를 만듭니다. 실제 장치 프로토콜을 완성한 예제는 아닙니다.

- 대기 Idle에서 start=1이면 다음 에지에 작업 Busy로 갑니다.
- Busy에서 done=1이면 다음 에지에 표시 Report로 갑니다.
- Report는 한 주기 유지하고 무조건 Idle로 돌아갑니다.
- ready는 Report에서만 1입니다. 리셋은 Idle로 초기화합니다.

상태에는 단순 번호보다 ‘미래 행동을 결정하는 기억’을 담습니다. Busy는 작업이 시작되었다는 과거를, Report는 완료 결과를 한 주기 표시해야 한다는 과거를 기억합니다.

<svg viewBox="0 0 460 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c3-7-t c3-7-d">
<title id="c3-7-t">작업 완료 표시기의 상태도</title>
<desc id="c3-7-d">Idle은 start가 1이면 Busy, Busy는 done이 1이면 Report, Report는 무조건 Idle로 갑니다. Idle과 Busy는 조건이 0이면 자기 상태를 유지합니다. ready는 Report에서만 1입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><circle cx="70" cy="70" r="40"/><circle cx="230" cy="70" r="40"/><circle cx="390" cy="70" r="40"/></g><path d="M110 70 H190 M270 70 H350 M390 110 V145 H70 V110" fill="none" stroke="var(--ink)" stroke-width="2"/><g fill="var(--ink)" font-size="13" text-anchor="middle"><text x="70" y="65">Idle</text><text x="70" y="85">ready=0</text><text x="230" y="65">Busy</text><text x="230" y="85">ready=0</text><text x="390" y="65">Report</text><text x="390" y="85">ready=1</text><text x="150" y="50">start=1 →</text><text x="310" y="50">done=1 →</text><text x="230" y="165">← 무조건 복귀</text><text x="70" y="15">start=0: 유지</text><text x="230" y="15">done=0: 유지</text></g>
</svg>
<p class="diagram-caption">그림 3-7a. 자기 유지 전이는 글자로 표시했습니다. 모든 전이는 상승 에지에서 일어납니다.</p>

## 표에서 식과 회로로

이진 인코딩을 Idle=00, Busy=01, Report=10으로 정하고 상태 비트를 q1, q0라고 합시다. 아래에서는 사용하지 않는 11도 Idle로 복귀하도록 직접 정의합니다.

| 현재 상태 | 조건 | 다음 상태 | ready |
| --- | --- | --- | --- |
| 00 | start=0 | 00 | 0 |
| 00 | start=1 | 01 | 0 |
| 01 | done=0 | 01 | 0 |
| 01 | done=1 | 10 | 0 |
| 10 | 항상 | 00 | 1 |
| 11 | 항상 | 00 | 0 |

표에서 다음 q1이 1인 경우는 Busy에서 done=1일 때뿐입니다. 다음 q0가 1인 경우는 Idle에서 start=1이거나 Busy에서 done=0일 때입니다.

`D1=¬q1·q0·done`

`D0=¬q1·¬q0·start+¬q1·q0·¬done`

`ready=q1·¬q0`

D1과 D0를 두 플립플롭의 D에 연결하고 Q를 q1, q0로 되돌립니다. 출력은 현재 상태만 보므로 Moore형입니다. 11을 don't care로 최소화하면 다른 식이 나올 수 있지만 여기서는 복귀 동작까지 명세한 표를 보존합니다.

## 식을 실제 저장 경로에 연결하기

다음 상태식은 스스로 값을 기억하지 않습니다. start·done과 현재 Q를 받아 두 D 입력을 계산하는 조합논리입니다. 아래에서는 데이터 식 뒤에 리셋 선택기를 두어 RESET=1이면 두 D 입력을 0으로 만듭니다. 이 예제의 리셋은 active-high 동기식이며 다음 상승 에지에 Idle=00으로 들어갑니다.

<svg viewBox="0 0 460 285" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c3-7b-t c3-7b-d">
<title id="c3-7b-t">작업 완료 표시기의 완성 기능 회로</title>
<desc id="c3-7b-d">start와 done 및 현재 상태 q1 q0가 다음 상태 조합논리로 들어갑니다. 결과는 동기식 리셋 선택기를 거쳐 공통 클록의 두 D 플립플롭에 저장됩니다. Q는 조합논리로 피드백되며 출력 디코더는 ready를 계산합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="65" y="55" width="135" height="110"/><rect x="230" y="55" width="85" height="110"/><rect x="350" y="55" width="90" height="110"/><rect x="245" y="215" width="115" height="45"/></g><g stroke="var(--ink)" stroke-width="2" fill="none"><path d="M10 80 H65 M10 125 H65 M200 85 H230 M200 135 H230 M315 85 H350 M315 135 H350 M440 85 H450 V190 H40 V150 H65 M450 190 H395 V235 H360 M395 190 V165 M272 20 V55 M395 20 V55 M245 235 H180"/><path d="M385 55 L395 65 L405 55"/></g><g fill="var(--ink)" font-size="13" text-anchor="middle"><text x="33" y="72">start</text><text x="33" y="118">done</text><text x="132" y="85">다음 상태</text><text x="132" y="110">D1·D0 식</text><text x="132" y="140">조합논리</text><text x="272" y="85">RESET=1</text><text x="272" y="110">→ 00 선택</text><text x="272" y="140">리셋 MUX</text><text x="395" y="95">DFF × 2</text><text x="395" y="125">q1, q0</text><text x="272" y="15">RESET</text><text x="395" y="15">CLK</text><text x="120" y="182">현재 상태 Q[1:0] 피드백</text><text x="302" y="242">q1·¬q0</text><text x="150" y="240">ready</text></g>
</svg>
<p class="diagram-caption">그림 3-7b. 두 상태 비트의 배선을 묶어 표시한 기능도입니다. 아래 출력 디코더의 입력도 현재 Q이며, 리셋 선택기는 데이터 식보다 우선합니다.</p>

예를 들어 현재 q1q0=01, done=1이면 조합논리는 D1D0=10을 만듭니다. **에지 전에는 Q=01, D=10이 동시에 존재**합니다. 다음 상승 에지에서 두 플립플롭이 함께 D를 저장하면 Q=10이 되고 ready가 1로 바뀝니다. 그 뒤 피드백된 10을 보고 조합논리는 벌써 다음 D=00을 준비하지만, Q는 다음 에지까지 10을 유지합니다. RESET=1인 에지에는 이 계산 결과에 관계없이 00을 저장합니다.

## 따라 풀기

리셋 후 00입니다. 첫 에지의 start=1이면 D1D0=01이므로 Busy가 됩니다. 둘째 에지의 done=0이면 01을 유지합니다. 셋째 에지의 done=1이면 10이 되고 조합 지연 후 ready=1입니다. 넷째 에지에는 입력에 관계없이 00으로 돌아가 ready=0입니다. Report 동안 start가 1이어도 그 에지에 새 작업을 받지는 않는다는 명세도 드러납니다.

## 헷갈리기 쉬운 점

상태도 화살표의 조건은 전이를 고르며, 클록은 전이가 일어나는 시점을 정합니다. done이 에지 사이에 1이 되었다고 즉시 Report가 되지는 않습니다. 또한 next state는 에지 사이에도 바뀔 수 있는 조합 신호입니다. 현재 상태와 혼동하지 않습니다.

## 직접 확인하기

1. Busy에서 start만 1이면 다음 상태는 무엇인가요?
2. 상태 11을 식에 대입하면 다음 상태와 ready는 무엇인가요?
3. Report에서 Idle로 가는 에지에 start=1이면 즉시 Busy가 되나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. done=0이면 Busy 유지이며 start는 이 상태에서 무관합니다.</p>
<p>2. D1=D0=0, ready=0입니다.</p>
<p>3. 아닙니다. 그 에지에는 Idle로 가며, 이후 Idle에서 start를 평가합니다. 더 높은 처리량이 필요하면 명세부터 수정해야 합니다.</p>
</details>

## 다음으로 이어가기

같은 세 상태도 어떤 비트 패턴을 붙이는지에 따라 회로가 달라집니다. 이진 인코딩과 one-hot을 비교합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §3.4–3.4.1, 인쇄 pp. 121–127 / PDF pp. 142–148. 책의 교통 제어기 대신 자체 작업 표시기로 설계 과정을 풀었습니다.
