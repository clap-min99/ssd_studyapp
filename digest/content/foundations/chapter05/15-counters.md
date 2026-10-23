## 이번 레슨의 목표

카운터의 wrap·분주·enable을 추적하고 누산기의 증가량과 평균 위상 진행률을 계산합니다.

## 앞에서 배운 내용

4장의 레지스터는 다음 값을 저장했습니다. 현재 값에 1을 더한 값을 다음 입력으로 돌려주면 카운터입니다.

## 조합 덧셈기 뒤에 에지 저장을 둔다

N비트 이진 카운터는 0부터 2ᴺ−1까지 간 뒤 0으로 돌아옵니다. 이 예제는 4비트이고 active-high 동기 reset, enable을 사용합니다. 책의 비동기 reset 예제와 사건 조건을 구별합니다.

```systemverilog
module ch5_counter4(input logic clk, reset, en,
                    output logic [3:0] q);
  always_ff @(posedge clk)
    if (reset) q <= '0;
    else if (en) q <= q + 4'd1;
endmodule
```

enable=1이 계속되면 최상위 비트는 2ᴺ⁻¹클록마다 한 번 반전하고 완전한 주기는 2ᴺ클록입니다. 따라서 출력 주파수는 f_clk/2ᴺ입니다. 반전 간격과 주기를 혼동하면 두 배 오류가 납니다. 카운터 출력으로 새 클록을 만드는 실제 구현은 별도 클록 설계가 필요하므로 일반 제어에서는 enable 펄스 활용도 검토합니다.

위상 누산기는 매번 1 대신 정수 p를 더해 modulo 2ᴺ으로 저장합니다. 낮은 양의 증가량 0<p≤2ᴺ⁻¹을 쓰는 MSB 출력의 평균 위상 진행 주파수 모델은 f_out=f_clk·p/2ᴺ, 주파수 해상도는 f_clk/2ᴺ입니다. p가 한 주기에 정확히 나누어떨어지지 않으면 에지 간격이 일정하지 않을 수 있습니다. 이것은 임의 주파수의 이상적 무지터 클록을 만든다는 보장이 아닙니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-15-t c5-15-d">
<title id="c5-15-t">카운터와 위상 누산기: 저장값을 반복 갱신하기</title>
<desc id="c5-15-d">카운터의 피드백 갱신을 시간 순서로 나눈 개념도입니다. 실제 데이터 경로는 레지스터로 돌아오는 고리입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">현재 q</text><text x="75" y="87">레지스터 출력</text><text x="223" y="59">다음 q</text><text x="223" y="87">q+1 또는 q+p</text><text x="371" y="59">상승 에지</text><text x="371" y="87">modulo 2의 N승 저장</text></g>
</svg>
<p class="diagram-caption">그림 5-15. 카운터의 피드백 갱신을 시간 순서로 나눈 개념도입니다. 실제 데이터 경로는 레지스터로 돌아오는 고리입니다.</p>

## 따라 풀기

q=1110에서 en=1이면 다음 두 에지 후 1111,0000입니다. en=0인 에지에서는 유지합니다. 4비트 카운터에 160Hz 클록을 넣고 en=1이면 MSB 반전 간격은 8/160=0.05s, 완전한 주기는 16/160=0.1s라 10Hz입니다. 별도 N=8,p=4,f_clk=1024Hz 누산기는 평균 1024×4/256=16Hz입니다. 이 예는 p가 256을 나누어 에지 간격도 일정합니다.

## 헷갈리기 쉬운 점

비트가 반전할 때마다 한 주기라고 세지 않습니다. p 선택의 근사 오차와 출력 에지의 시간 간격 변동은 다른 항목입니다. 위 누산기는 위상 진행 모델이며 아날로그 발진기 회로 전체를 설명하지 않습니다.

## 직접 확인하기

1. N=3,80Hz의 MSB 주파수는?
2. reset=en=1인 에지에서는?
3. N을 늘리면 위상 누산기의 주파수 간격은?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 80/8=10Hz입니다.</p>
<p>2. reset이 우선해 q=0입니다.</p>
<p>3. f_clk/2ᴺ이 작아져 더 촘촘해집니다.</p>
</details>

## 다음으로 이어가기

다음에는 더하기 대신 이전 비트를 옆 저장 위치로 옮깁니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.4–5.4.1, 인쇄 pp. 261–262 / PDF pp. 282–283. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
