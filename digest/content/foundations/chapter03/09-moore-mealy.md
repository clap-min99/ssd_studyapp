## 이번 레슨의 목표

Moore형과 Mealy형의 출력 의존성을 구별하고, 같은 입력열을 검출할 때 출력이 언제 나타나는지 비교합니다.

## 앞에서 배운 내용

레슨 7의 ready는 현재 상태만으로 정해졌습니다. 출력을 만드는 조합논리가 현재 입력까지 참조하게 바꿀 수도 있습니다.

## 출력 함수의 차이

두 형태 모두 `S_next=F(S,I)`입니다. Moore형은 `Y=G(S)`, Mealy형은 `Y=G(S,I)`입니다. Moore 상태도는 출력값을 상태 안에, Mealy 상태도는 입력/출력을 전이 화살표에 적는 방식이 자연스럽습니다.

<svg viewBox="0 0 440 155" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c3-9-t c3-9-d">
<title id="c3-9-t">Moore와 Mealy의 출력 의존성</title>
<desc id="c3-9-d">Moore 출력은 현재 상태 S에서만 계산합니다. Mealy 출력은 현재 상태 S와 현재 입력 I에서 계산합니다. 두 형태 모두 다음 상태는 S와 I에 의존합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="20" y="20" width="185" height="110"/><rect x="235" y="20" width="185" height="110"/></g><g fill="var(--ink)" font-size="16" text-anchor="middle"><text x="112" y="50">Moore</text><text x="112" y="83">S → 출력 논리 → Y</text><text x="112" y="112">상태 변화 후 반응</text><text x="327" y="50">Mealy</text><text x="327" y="83">S, I → 출력 논리 → Y</text><text x="327" y="112">입력 변화에도 반응</text></g>
</svg>
<p class="diagram-caption">그림 3-9a. 출력 논리만 비교한 기능도입니다. Moore 출력에도 조합 지연은 있습니다.</p>

## 따라 풀기

입력 비트 x를 매 상승 에지마다 한 개씩 받아 연속된 ‘10’을 검출합니다. 겹치는 패턴을 허용합니다. Mealy형의 상태 A는 ‘직전 비트가 1이 아님’, B는 ‘직전 비트가 1’입니다. 리셋은 A입니다.

| 상태 | x | 다음 상태 | Y |
| --- | --- | --- | --- |
| A | 0 | A | 0 |
| A | 1 | B | 0 |
| B | 0 | A | 1 |
| B | 1 | B | 0 |

B를 저장 비트 p=1로 인코딩하면 `D_p=x`, `Y=p·¬x`입니다. 두 번째 비트 0이 입력되고 아직 B일 때 Y=1이 됩니다. 에지 직전의 안정된 Y를 수신 레지스터가 샘플할 수 있습니다.

Moore형은 A(기본), B(직전 1), C(10 검출)의 세 상태를 둡니다. A와 C에서는 x=0이면 A, x=1이면 B입니다. B에서는 x=1이면 B, x=0이면 C입니다. 출력은 C에서만 1입니다.

| 이번에 샘플할 x | 에지 직전 Mealy 상태/Y | 에지 직후 Moore 상태/Y |
| --- | --- | --- |
| 1 | A / 0 | B / 0 |
| 0 | B / 1 | C / 1 |
| 1 | A / 0 | B / 0 |
| 0 | B / 1 | C / 1 |

이 표는 서로 다른 관측 시점을 명시했습니다. Mealy 출력은 마지막 비트가 도착한 주기 안에서 반응하고, Moore 출력은 그 비트를 샘플해 상태를 갱신한 뒤 반응합니다. 이 명세에서는 Mealy Y를 에지에서 레지스터에 저장하면 Moore 출력의 주기 단위 결과와 맞출 수 있습니다.

## 같은 입력의 출력을 시간축에서 비교하기

입력은 에지 직후 바뀌어 다음 에지까지 안정된다고 가정합니다. 리셋 뒤 x=1을 준비하고 첫 에지 E1에서 읽은 다음, x를 0으로 바꾸어 둘째 에지 E2에서 읽습니다. 아래는 전파 지연과 에지 직후의 과도현상을 생략한 기능 파형입니다.

<svg viewBox="0 0 460 245" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c3-9b-t c3-9b-d">
<title id="c3-9b-t">10 검출기의 Mealy와 Moore 출력 시점</title>
<desc id="c3-9b-d">첫 에지 E1에서 1을 읽고 입력이 0으로 바뀌면 Mealy 출력이 올라갑니다. 둘째 에지 E2에서 0을 읽으면 Mealy는 A로 돌아가 출력이 내려가고 Moore는 C가 되어 출력이 올라갑니다.</desc>
<g stroke="var(--muted)" stroke-dasharray="4 4"><path d="M190 15 V205 M330 15 V205"/></g><g stroke="var(--ink)" fill="none" stroke-width="2"><path d="M110 45 H190 V25 H220 V45 H330 V25 H360 V45 H430 M110 70 H230 V90 H430 M110 135 H230 V115 H330 V135 H430 M110 180 H330 V160 H430"/></g><g fill="var(--ink)" font-size="14"><text x="10" y="43">CLK</text><text x="10" y="88">x</text><text x="10" y="133">Mealy Y</text><text x="10" y="178">Moore Y</text><text x="180" y="225">E1: 1 저장</text><text x="320" y="225">E2: 0 저장</text></g>
</svg>
<p class="diagram-caption">그림 3-9b. Mealy 출력은 E1과 E2 사이 입력 0의 도착에 반응합니다. Moore 출력은 E2 뒤 검출 상태 C에서 1입니다.</p>

1. E1 직후 두 검출기 모두 B입니다. 아직 x=1이면 Mealy 식은 `1·¬1=0`입니다.
2. 같은 주기 안에 x=0이 도착하면 상태는 B인 채 Mealy Y만 `1·¬0=1`로 바뀝니다. Moore는 여전히 B라 Y=0입니다.
3. E2에서 Mealy는 A로, Moore는 C로 갑니다. 이후 Mealy Y=0, Moore Y=1입니다. E2에서 별도 수신 플립플롭이 Mealy Y를 저장했다면 에지 직전의 1을 받습니다.

이렇게 ‘입력이 도착한 시점’, ‘상태가 바뀐 에지’, ‘출력을 읽는 시점’을 따로 표시해야 두 결과를 비교할 수 있습니다. Mealy의 짧은 조합 출력을 다음 회로가 언제 샘플할지도 명세의 일부입니다.

## 헷갈리기 쉬운 점

Mealy가 항상 정확히 한 주기 빠르다는 구호보다 입력 도착·샘플·출력 관측 시점을 적는 것이 정확합니다. Mealy 조합 출력은 입력 변화나 글리치에 반응할 수 있습니다. Moore도 여러 상태 비트가 전환되는 순간 출력 디코더에 글리치가 생길 수 있으므로 무조건 무글리치라고 말하지 않습니다. 다른 클록 도메인에 직접 연결해도 안전하다는 뜻도 아닙니다.

## 직접 확인하기

1. `Y=p·¬x`가 Mealy인 이유는 무엇인가요?
2. 입력열 11010에서 10 검출은 몇 번인가요?
3. Moore형의 C에서 x=1이면 B로 가야 하는 이유는 무엇인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 저장 상태 p뿐 아니라 현재 입력 x에 직접 의존하기 때문입니다.</p>
<p>2. 세 번째와 다섯 번째 비트까지 읽었을 때 두 번입니다.</p>
<p>3. 방금 읽은 1이 다음 10 패턴의 시작이 될 수 있기 때문입니다.</p>
</details>

## 다음으로 이어가기

FSM이 커지면 역할을 나누고, 서로 주고받는 신호의 시점을 명시해야 합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §3.4.3, 인쇄 pp. 130–133 / PDF pp. 151–154. 10 검출기·입력열·관측 시점 표는 자체 구성입니다.
