## 이번 레슨의 목표

논리·산술 시프트와 회전을 계산하고 MUX 단계로 가변 이동량을 구현하는 원리를 설명합니다.

## 앞에서 배운 내용

4장의 슬라이스·연결은 비트를 조립했습니다. 시프터는 이동량에 따라 각 출력에 어떤 비트를 연결할지 고릅니다.

## 빈자리를 무엇으로 채우는가

논리 시프트는 빈자리를 0으로 채웁니다. 산술 오른쪽 시프트는 원래 부호 비트를 복제합니다. 왼쪽 이동 자체는 논리·산술에서 같고 폭 밖으로 밀린 비트는 사라집니다. 회전(rotate)은 밀려난 비트를 반대편 빈자리로 넣어 모든 비트를 보존합니다.

```systemverilog
module ch5_shift8(input logic [7:0] a, input logic [2:0] shamt,
                  output logic [7:0] left_y, right_y, arithmetic_y, ror_y);
  assign left_y = a << shamt;
  assign right_y = a >> shamt;
  assign arithmetic_y = $unsigned($signed(a) >>> shamt);
  assign ror_y = (a >> shamt) | (a << (4'd8-{1'b0,shamt}));
endmodule
```

`>>>`의 왼쪽 피연산자가 unsigned라면 부호 확장을 기대할 수 없습니다. 위 코드는 이동 연산을 signed로 수행한 뒤 그 비트 패턴을 unsigned 출력으로 명시 변환합니다. shamt는 0부터 7까지이며, 회전량 0에서는 두 번째 항이 8비트 왼쪽 이동으로 0이 되어 원래 a가 나옵니다. 다른 폭에 적용하려면 이동량 범위도 다시 정합니다.

N비트 가변 시프터는 출력마다 N:1 MUX를 두는 방식으로 볼 수 있습니다. 보충 구조로 8비트는 1·2·4비트 이동 여부를 고르는 2:1 MUX 세 단계로도 만들 수 있습니다. log₂8=3단계 조합 경로이며 세 클록 지연은 아닙니다. 회전기는 0 입력 대신 반대편 비트를 연결합니다.

<svg viewBox="0 0 450 275" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-9-study-t c5-9-study-d">
<title id="c5-9-study-t">오른쪽 이동의 채움 비트와 공통 비트</title>
<desc id="c5-9-study-d">8비트 10110001을 두 자리 이동한 세 결과입니다. 작은 왼쪽 칸은 새 상위 두 비트,오른쪽 큰 칸은 원래 a[7:2] 여섯 비트입니다. 비트별 값으로 채움 규칙을 비교합니다.</desc>
<text x="225" y="25" font-size="16" text-anchor="middle" fill="var(--ink)">입력 a = 10 110001 · 오른쪽 두 자리 이동</text><text x="15" y="75" font-size="15" text-anchor="start" fill="var(--ink)">논리</text><rect x="95" y="50" width="76" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="133.0" y="75.0" font-size="15" text-anchor="middle" fill="var(--ink)">00</text><rect x="171" y="50" width="240" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="291.0" y="75.0" font-size="15" text-anchor="middle" fill="var(--ink)">101100</text><text x="15" y="133" font-size="15" text-anchor="start" fill="var(--ink)">산술</text><rect x="95" y="108" width="76" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="133.0" y="133.0" font-size="15" text-anchor="middle" fill="var(--ink)">11</text><rect x="171" y="108" width="240" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="291.0" y="133.0" font-size="15" text-anchor="middle" fill="var(--ink)">101100</text><text x="15" y="191" font-size="15" text-anchor="start" fill="var(--ink)">회전</text><rect x="95" y="166" width="76" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="133.0" y="191.0" font-size="15" text-anchor="middle" fill="var(--ink)">01</text><rect x="171" y="166" width="240" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="291.0" y="191.0" font-size="15" text-anchor="middle" fill="var(--ink)">101100</text><text x="225" y="245" font-size="14" text-anchor="middle" fill="var(--ink)">오른쪽 회전의 상위 01은 원래 하위 a[1:0]</text>
</svg>
<p class="diagram-caption">그림 5-9. 8비트 10110001을 두 자리 이동한 세 결과입니다. 작은 왼쪽 칸은 새 상위 두 비트,오른쪽 큰 칸은 원래 a[7:2] 여섯 비트입니다. 비트별 값으로 채움 규칙을 비교합니다.</p>

## 출력의 각 위치에 어떤 입력 비트가 오는가

시프트는 먼저 비트 위치의 문제로 풀어야 합니다. 8비트를 오른쪽 두 자리 옮기면 원래 bit7은 출력 bit5, 원래 bit2는 출력 bit0으로 갑니다. 원래 bit1·0은 출력 범위를 벗어납니다. 남은 출력 bit7·6에 0을 넣으면 논리, 원래 a[7]을 넣으면 산술, 원래 a[1:0]을 넣으면 회전입니다.

따라서 같은 입력으로 세 결과를 비교할 때 하위 여섯 비트는 같고 상위 두 비트만 채움 규칙이 다릅니다. 오른쪽 회전에서는 잘려 나간 두 비트를 버리지 않고 그 순서 그대로 상위로 돌립니다. 산술 이동도 비트 보존 연산은 아니므로 밀려난 낮은 비트는 사라집니다.

그 뒤에 숫자로 해석합니다. unsigned 논리 오른쪽 이동은 2의 거듭제곱으로 나눈 몫입니다. signed 산술 오른쪽 이동은 부호를 보존하며 음수의 분수 부분을 아래 방향으로 내리는 효과가 있습니다. 왼쪽 이동은 폭을 넘는 비트가 없을 때만 수학적인 곱과 같은 값을 유지합니다. 위치 계산·잘림·숫자 해석 순서로 풀면 혼동이 줄어듭니다.

## 따라 풀기

a=10110001,이동량=2입니다. 논리 오른쪽 00101100, 산술 오른쪽 11101100, 왼쪽 11000100, 오른쪽 회전 01101100입니다. signed 원래 값은 −79, 산술 오른쪽 결과는 −20입니다. −79/4=−19.75를 음의 무한대 방향으로 내린 값으로 0 방향 절삭과 다릅니다. 왼쪽 이동을 무조건 정확한 ×4로 읽으면 상위 비트 잘림을 놓칩니다.

### 조건을 바꾸어 한 번 더 풀기

a=10110001에서 오른쪽 두 자리 이동을 다음처럼 나눕니다.

| 항목 | 원래 비트/채움 | 결과 |
| --- | --- | --- |
| 공통으로 내려온 하위 6비트 | a[7:2] | 101100 |
| 논리 상위 2비트 | 00 | 00_101100 |
| 산술 상위 2비트 | a[7] 두 번=11 | 11_101100 |
| 회전 상위 2비트 | a[1:0]=01 | 01_101100 |

세 결과의 길이가 모두 8인지, 내려온 여섯 비트가 동일한지 검산합니다. 회전량 0에서는 원래 비트 순서를 그대로 유지해야 합니다. 이동량을 1·2·4로 나눌 때 shamt=110₂는 2와 4를 선택해 총 6자리 이동합니다.

### 실습: 비트 위치와 수치 연산으로 독립 기대값 만들기

입력 256개와 이동량 8개를 모두 검사합니다. 논리 이동의 기대값은 정수의 곱셈·나눗셈으로,산술 이동은 음수의 아래 방향 반올림으로,회전은 출력 bit k가 원래 어느 비트에서 오는지로 구합니다. DUT의 식을 그대로 복사하지 않고 같은 명세를 다른 방식으로 표현하는 실습입니다.

```systemverilog
module tb_ch5_shift8;
  timeunit 1ns;
  timeprecision 1ps;
  logic [7:0] a, left_y, right_y, arithmetic_y, ror_y;
  logic [2:0] shamt;
  logic [7:0] expected_rotate;
  integer factor, signed_value, expected_left, expected_right, expected_arithmetic;
  ch5_shift8 dut(.a(a), .shamt(shamt), .left_y(left_y),
                .right_y(right_y), .arithmetic_y(arithmetic_y), .ror_y(ror_y));
  initial begin
    for (int av=0; av<256; av=av+1)
      for (int amount=0; amount<8; amount=amount+1) begin
        a=av[7:0]; shamt=amount[2:0];
        factor=2**amount;
        expected_left=(av*factor)%256;
        expected_right=av/factor;
        signed_value=(av>=128) ? av-256 : av;
        if (signed_value>=0) expected_arithmetic=signed_value/factor;
        else expected_arithmetic=-((-signed_value+factor-1)/factor);
        for (int bit_index=0; bit_index<8; bit_index=bit_index+1)
          expected_rotate[bit_index]=a[(bit_index+amount)%8];
        #1;
        if (left_y !== expected_left[7:0] || right_y !== expected_right[7:0] ||
            arithmetic_y !== expected_arithmetic[7:0] || ror_y !== expected_rotate)
          $fatal(1, "Shift mismatch a=%b amount=%0d", a, amount);
      end
    $display("PASS: 2048 shift vectors");
    $finish;
  end
endmodule
```

4장 레슨18의 내보내기 도구를 사용하고 최상위 `tb_ch5_shift8`로 실행합니다. 기대 완료 로그는 `PASS: 2048 shift vectors`입니다. `>>>`를 unsigned a에 직접 적용하는 오류 사본은 a의 MSB가 1이고 이동량이 0보다 큰 검사에서 실패해야 합니다. 이 실습은 8비트·이동량 0부터 7의 기능에 한정하며 실제 FPGA의 타이밍은 검증하지 않습니다.

## 헷갈리기 쉬운 점

시프터는 조합논리이고 시프트 레지스터는 에지마다 데이터를 저장·이동하는 순차논리입니다. signed 정수 나눗셈과 산술 오른쪽 이동은 음수의 반올림 규칙이 다를 수 있습니다.

## 직접 확인하기

1. 00000001을 오른쪽 1비트 회전하면?
2. 11111101을 signed 산술 오른쪽 1비트 이동하면?
3. 1·2·4 단계에서 이동량 5는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 10000000입니다.</p>
<p>2. 11111110 즉 −2입니다.</p>
<p>3. 1과 4 이동을 선택하고 2 이동은 통과합니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

a=10010110을 오른쪽 3자리 논리 이동·산술 이동·회전한 결과를 구하세요. 버린 낮은 세 비트와 각 결과의 상위 세 비트를 먼저 적은 다음, 각 결과가 8비트인지 확인하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>남는 a[7:3]=10010이고 낮은 세 비트는 110입니다. 논리는 000_10010=00010010, 산술은 111_10010=11110010, 회전은 110_10010=11010010입니다.</p>
<p>각각 채움 3비트와 내려온 5비트로 총 8비트입니다. 회전에서 110을 011로 뒤집어 붙이면 비트 순서를 바꾸는 오류입니다.</p>
</details>

## 다음으로 이어가기

다음 두 선택 심화는 곱셈·나눗셈입니다. 핵심 과정은 레슨12 고정소수점으로 이어갑니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.5, 인쇄 pp. 251–252 / PDF pp. 272–273. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
