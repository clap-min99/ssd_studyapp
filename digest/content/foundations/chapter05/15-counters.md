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

<svg viewBox="0 0 450 230" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-15-study-t c5-15-study-d">
<title id="c5-15-study-t">카운터의 덧셈기·선택·레지스터 피드백</title>
<desc id="c5-15-study-d">현재 q에 1을 더하고 enable에 따라 새 합 또는 이전 q를 선택합니다. reset은 0 선택이 우선입니다. 상승 에지에서 저장한 q가 덧셈기 입력으로 돌아오는 기능도이며 실제 선택 소자는 묶어 표시했습니다.</desc>
<rect x="65" y="60" width="75" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="102.5" y="95.0" font-size="15" text-anchor="middle" fill="var(--ink)">+1</text><rect x="205" y="60" width="105" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="257.5" y="95.0" font-size="15" text-anchor="middle" fill="var(--ink)">선택</text><rect x="350" y="60" width="65" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="382.5" y="95.0" font-size="15" text-anchor="middle" fill="var(--ink)">FF</text><path d="M30 180 H435 V90 H415 M30 180 V90 H65 M140 90 H205 M310 90 H350 M170 180 V135 H240 V120 M382 25 V60" fill="none" stroke="var(--ink)" stroke-width="2"/><circle cx="170" cy="180" r="3" fill="var(--ink)"/><text x="230" y="35" font-size="15" text-anchor="middle" fill="var(--ink)">reset·en</text><text x="382" y="20" font-size="14" text-anchor="middle" fill="var(--ink)">clk</text><text x="225" y="205" font-size="15" text-anchor="middle" fill="var(--ink)">q 피드백</text>
</svg>
<p class="diagram-caption">그림 5-15. 현재 q에 1을 더하고 enable에 따라 새 합 또는 이전 q를 선택합니다. reset은 0 선택이 우선입니다. 상승 에지에서 저장한 q가 덧셈기 입력으로 돌아오는 기능도이며 실제 선택 소자는 묶어 표시했습니다.</p>

## 이진 카운터의 각 비트가 왜 분주되는가

카운터의 bit0은 매 증가마다 0·1을 번갈아 내고 bit1은 두 증가마다 한 번 반전합니다. bit k는 아래 k비트가 한 바퀴 돌 때마다 반전하므로 반전 간격은 2ᵏ클록,완전한 주기는 2ᵏ⁺¹클록입니다. N비트 최상위 k=N−1을 대입하면 주기 2ᴺ클록이 됩니다.

enable이 계속 1일 때의 규칙이며 중간에 유지가 있으면 원래 클록에 대한 일정 분주 파형은 깨질 수 있습니다. reset 역시 주기 중간의 상태를 바꿉니다. f_clk/2ᴺ을 계산하기 전에 지속 증가·reset 비활성 조건을 확인합니다.

위상 누산기는 p씩 건너뛰어 modulo 공간을 진행합니다. p가 나눠떨어지지 않으면 ‘평균 주파수’와 ‘모든 에지 간격이 동일’은 다릅니다. 출력은 입력 클록의 격자 시각에서만 바뀌므로 목표 평균 주기에 해당하는 정확한 분수 시각을 매번 만들 수는 없습니다. 제어용 신호와 별도 클록 자원을 구별해야 합니다.

## 따라 풀기

q=1110에서 en=1이면 다음 두 에지 후 1111,0000입니다. en=0인 에지에서는 유지합니다. 4비트 카운터에 160Hz 클록을 넣고 en=1이면 MSB 반전 간격은 8/160=0.05s, 완전한 주기는 16/160=0.1s라 10Hz입니다. 별도 N=8,p=4,f_clk=1024Hz 누산기는 평균 1024×4/256=16Hz입니다. 이 예는 p가 256을 나누어 에지 간격도 일정합니다.

### 조건을 바꾸어 한 번 더 풀기

3비트 증가 카운터를 8회 관찰합니다.

| 증가 횟수 | q | bit2 |
| --- | --- | --- |
| 0·1·2·3 | 000·001·010·011 | 0 |
| 4·5·6·7 | 100·101·110·111 | 1 |
| 8 | 000 | 0 |

bit2는 4회마다 반전하지만 0에서 다시 0으로 한 주기를 마치려면 8회가 필요합니다. 별도로 N=4,p=3이면 상태는 0,3,6,9,12,15,2,…로 진행하며 MSB 상승 사이의 클록 수가 항상 같지는 않습니다.

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

### 적용 문제: 직접 구성하고 이유 설명하기

N=4 카운터에서 reset 후 en=1,1,0,1,0,1을 여섯 에지에 넣습니다. q를 모두 적으세요. 이를 근거로 enable이 불규칙할 때 단순 분주 주파수를 적용할 수 있는지 설명하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>q는 0001,0010,0010,0011,0011,0100입니다. en=0인 두 에지는 상태를 증가시키지 않습니다.</p>
<p>bit 변화가 원래 입력 클록의 일정 횟수마다 일어난다고 보장할 수 없습니다. f_clk/16은 계속 증가하는 4비트 카운터의 MSB 규칙이며 이 입력열에는 그대로 적용하지 않습니다.</p>
</details>

## 다음으로 이어가기

다음에는 더하기 대신 이전 비트를 옆 저장 위치로 옮깁니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.4–5.4.1, 인쇄 pp. 261–262 / PDF pp. 282–283. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
