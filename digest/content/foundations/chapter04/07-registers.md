## 이번 레슨의 목표

always_ff와 nonblocking 할당을 읽고 에지 사이의 유지와 에지 직후 갱신을 구별합니다.

## 앞에서 배운 내용

3장의 D 플립플롭은 상승 에지에서 입력을 받아 다음 에지까지 유지했습니다. 그 동작을 그대로 기술합니다.

## 에지 사건과 데이터 갱신을 분리한다

```systemverilog
module sample3(input logic clk,
               input logic [2:0] d,
               output logic [2:0] q);
  always_ff @(posedge clk)
    q <= d;
endmodule
```

`posedge clk`는 상승 에지를 기다리는 사건 조건입니다. `always_ff`는 플립플롭을 기술하려는 의도를 도구에 알립니다. `q <= d`는 nonblocking 할당으로, 사건을 처리할 때 오른쪽 d를 평가하고 해당 시각의 뒤쪽 갱신 단계에서 q에 반영합니다. 여기서 `<=`는 작거나 같다는 비교가 아닙니다.

폭이 3비트이므로 1비트 플립플롭 세 개가 같은 클록을 공유하는 레지스터를 나타냅니다. 입력 d가 에지 사이에서 바뀌어도 q는 유지됩니다. 리셋이 없으므로 시뮬레이션 시작 시 q는 XXX일 수 있습니다. 첫 유효 샘플 전에 000이라고 가정하지 않습니다.

이 코드는 기능 모델입니다. 실제 하드웨어에서 setup·hold를 만족해야 한다는 3장의 조건은 사라지지 않습니다. 일반 RTL 시뮬레이션이 에지에서 값을 복사했다고 실제 회로의 물리 타이밍까지 확인한 것은 아닙니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-7-t c4-7-d">
<title id="c4-7-t">레지스터 기술: 상승 에지에서 값 저장하기</title>
<desc id="c4-7-d">한 상승 에지에서 3비트 레지스터를 갱신하는 사건 순서입니다. 실제 clock-to-Q 지연값을 그린 시간도는 아닙니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">에지 직전</text><text x="75" y="91">d=101·q=010</text><text x="223" y="63">상승 에지</text><text x="223" y="91">오른쪽 d 평가</text><text x="371" y="63">갱신 후</text><text x="371" y="91">q=101 유지</text></g>
</svg>
<p class="diagram-caption">그림 4-7. 한 상승 에지에서 3비트 레지스터를 갱신하는 사건 순서입니다. 실제 clock-to-Q 지연값을 그린 시간도는 아닙니다.</p>

## 따라 풀기

첫 상승 에지가 5ns이고 직전 d=101입니다. 갱신 후 q=101이 됩니다. 7ns에 d=011로 바뀌어도 q는 101입니다. 다음 상승 에지가 15ns이고 직전 d=110이면 갱신 후 q=110입니다. 7ns의 011은 에지에서 읽히지 않았으므로 저장되지 않습니다. 에지마다 입력 하나를 샘플한다는 규칙으로 검산합니다.

## 헷갈리기 쉬운 점

always_ff는 반복문으로 값이 계속 흘러가는 코드가 아닙니다. q를 다른 assign이나 다른 always 블록에서도 쓰면 구동 주체가 겹칩니다. 이 트랙에서는 한 저장 신호의 갱신을 한 always_ff에 모읍니다. 에지와 정확히 같은 순간에 테스트벤치가 d를 바꾸면 경합이 생길 수 있으므로 검사에서는 입력 변경 시점을 분리합니다.

## 직접 확인하기

1. d만 바뀌고 clk 상승 에지가 없으면 q는 어떻게 되나요?
2. 3비트 레지스터는 몇 비트의 정보를 저장하나요?
3. 초기 q가 XXX인 것을 바로 설계 오류라고 단정할 수 있나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 기존 값을 유지합니다.</p>
<p>2. 3비트입니다. 두 클록 사이에도 상태가 남습니다.</p>
<p>3. 아닙니다. 리셋 없는 초기 상태일 수 있습니다. 사용 전에 초기화하거나 유효 샘플이 들어오도록 명세해야 합니다.</p>
</details>

## 다음으로 이어가기

다음에는 리셋과 enable의 우선순위를 코드로 표현합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.4.1, 인쇄 pp. 191–192 / PDF pp. 212–213. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
