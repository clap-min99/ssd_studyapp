## 이번 레슨의 목표

비트 이동 방향과 load 우선순위를 정하고 에지 전후의 직렬 출력을 추적합니다.

## 앞에서 배운 내용

4장의 두 단계 레지스터는 이전 단계 값을 함께 읽었습니다. 더 많은 단계를 연결하면 여러 비트의 이력을 저장할 수 있습니다.

## 새 비트는 bit0에, 이전 최상위 비트는 밖으로

아래는 4비트 q를 왼쪽으로 한 자리 옮기고 serial_in을 bit0에 넣는 시프트 레지스터입니다. 직렬 출력 serial_out은 현재 q[3]입니다. reset > load > shift의 우선순위를 사용합니다.

```systemverilog
module ch5_shiftreg4(input logic clk, reset, load, serial_in,
                     input logic [3:0] d,
                     output logic [3:0] q, output logic serial_out);
  always_ff @(posedge clk)
    if (reset) q <= '0;
    else if (load) q <= d;
    else q <= {q[2:0],serial_in};
  assign serial_out = q[3];
endmodule
```

직렬 입력을 네 에지 동안 넣으면 최근 네 입력을 병렬 q에서 읽을 수 있습니다. 먼저 들어온 비트가 높은 위치에 있습니다. 병렬 load는 네 비트를 한 에지에 저장하고 이후 shift로 MSB부터 하나씩 내보냅니다. 받는 쪽이 같은 상승 에지에서 serial_out을 샘플하면 갱신 전 q[3]을 읽습니다. 에지 직후 파형은 이미 다음 비트를 보여주므로 관측 시점을 명시해야 합니다.

이 코드는 매 상승 에지마다 이동하며 유지 enable은 없습니다. 필요하면 명세와 코드를 함께 확장합니다. N비트 일반화에서 `{q[N-2:0],serial_in}`은 N=1의 경계가 문제가 되므로 폭 제한 또는 generate 분기가 필요합니다. 고정 4비트 예제를 그 조건 없이 복사하지 않습니다.

<svg viewBox="0 0 450 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-16-study-t c5-16-study-d">
<title id="c5-16-study-t">시프트 레지스터의 단계별 직렬 연결</title>
<desc id="c5-16-study-d">Sin이 Q0 단계로 들어가고 Q0→Q1→Q2→Q3 순서로 이동합니다. Q3가 Sout입니다. 같은 clk를 공유하며 reset·병렬 load MUX는 생략한 기능 회로입니다.</desc>
<rect x="55" y="70" width="65" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="87.5" y="105.0" font-size="15" text-anchor="middle" fill="var(--ink)">Q0</text><path d="M120 100 H150" fill="none" stroke="var(--ink)" stroke-width="2"/><path d="M87 175 V130" fill="none" stroke="var(--ink)" stroke-width="2"/><rect x="150" y="70" width="65" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="105.0" font-size="15" text-anchor="middle" fill="var(--ink)">Q1</text><path d="M215 100 H245" fill="none" stroke="var(--ink)" stroke-width="2"/><path d="M182 175 V130" fill="none" stroke="var(--ink)" stroke-width="2"/><rect x="245" y="70" width="65" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="277.5" y="105.0" font-size="15" text-anchor="middle" fill="var(--ink)">Q2</text><path d="M310 100 H340" fill="none" stroke="var(--ink)" stroke-width="2"/><path d="M277 175 V130" fill="none" stroke="var(--ink)" stroke-width="2"/><rect x="340" y="70" width="65" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="372.5" y="105.0" font-size="15" text-anchor="middle" fill="var(--ink)">Q3</text><path d="M372 175 V130" fill="none" stroke="var(--ink)" stroke-width="2"/><path d="M15 100 H55 M405 100 H435 M35 175 H372" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="40" y="70" font-size="14" text-anchor="middle" fill="var(--ink)">Sin</text><text x="420" y="70" font-size="14" text-anchor="middle" fill="var(--ink)">Sout</text><text x="35" y="200" font-size="14" text-anchor="middle" fill="var(--ink)">clk</text><text x="225" y="235" font-size="14" text-anchor="middle" fill="var(--ink)">같은 에지에서 각 단계가 이전 단계의 값을 저장</text>
</svg>
<p class="diagram-caption">그림 5-16. Sin이 Q0 단계로 들어가고 Q0→Q1→Q2→Q3 순서로 이동합니다. Q3가 Sout입니다. 같은 clk를 공유하며 reset·병렬 load MUX는 생략한 기능 회로입니다.</p>

## 직렬 비트 순서를 에지 전후 표로 복원하기

`{q[2:0],serial_in}`은 이전 q의 bit2·1·0을 새 bit3·2·1로 옮기고 새 bit0에 serial_in을 넣습니다. 네 플립플롭이 같은 에지에서 이전 값을 읽으므로 새 비트가 한 에지에 모든 단계를 통과하지 않습니다. 두 단계 파이프라인에서 배운 nonblocking의 의미가 그대로 이어집니다.

병렬 load는 이동 경로 대신 d를 네 저장 위치에 동시에 넣습니다. 다음 shift부터 이전 MSB가 빠져나갑니다. serial_out은 단순히 현재 q[3]에 연결했으므로 첫 shift 에지 직전의 출력과 직후의 출력은 다를 수 있습니다. 받는 회로가 같은 에지에 읽는다면 직전 MSB를 샘플한다는 점을 표의 열 이름에 명시합니다.

직렬에서 병렬로 모을 때 먼저 입력한 비트가 가장 높은 자리에 도달합니다. 반대로 병렬 데이터를 직렬로 보낼 때도 이 구조는 MSB부터 보냅니다. 데이터의 표현과 프로토콜의 전송 순서는 각각 별도 계약이며, LSB 우선 송신기가 필요하면 연결 방향을 다시 정해야 합니다.

## 따라 풀기

리셋 후 serial_in=1,0,1,1을 네 에지에 넣으면 q는 0001,0010,0101,1011입니다. 병렬 데이터 1011을 load한 뒤 serial_in=0으로 계속 shift하면 에지 직전 빠져나가는 비트는 1,0,1,1입니다. 각 에지 직후 q는 0110,1100,1000,0000입니다. serial_out의 에지 전 값과 직후 값을 뒤섞지 않으면 원래 1011을 복원할 수 있습니다.

### 조건을 바꾸어 한 번 더 풀기

d=1101을 load한 뒤 serial_in=0으로 네 번 shift합니다.

| shift 에지 | 직전 q | 수신할 serial_out | 직후 q |
| --- | --- | --- | --- |
| 1 | 1101 | 1 | 1010 |
| 2 | 1010 | 1 | 0100 |
| 3 | 0100 | 0 | 1000 |
| 4 | 1000 | 1 | 0000 |

출력열 1,1,0,1이 원래 데이터의 MSB부터 일치합니다. 직후 q[3]만 읽어 1,0,1,0으로 기록하면 한 비트 밀린 결과를 얻습니다. 출력 배선이 아니라 관찰 시점이 문제일 수 있습니다.

## 헷갈리기 쉬운 점

레슨9의 조합 시프터는 이동량을 한 번에 고르고, 이 레지스터는 매 에지 한 자리씩 저장 위치를 옮깁니다. 직렬/병렬 변환에서 어느 쪽 비트가 먼저 오는지 별도로 약속합니다.

## 직접 확인하기

1. load=1과 serial_in=1이 동시에 오면?
2. q=1001,serial_in=1에서 shift 후 q는?
3. serial_out을 같은 에지에 받는 레지스터는 어느 q[3]을 읽나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. d를 저장합니다. shift는 실행하지 않습니다.</p>
<p>2. 0011입니다. 이전 bit3=1은 빠져나갑니다.</p>
<p>3. setup/hold를 만족했다면 갱신 전 값입니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

리셋 후 0,1,1,0을 serial_in에 넣어 네 번 이동합니다. 각 에지 직후 q와 최종 병렬 값의 비트 순서를 구하세요. 마지막 두 비트만 교환해서 입력하면 어떤 두 위치가 달라지나요?

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>0000→0001→0011→0110입니다. 최종 q[3:0]은 입력 순서 0,1,1,0 그대로입니다.</p>
<p>마지막 두 입력을 0,1로 교환하면 전체 입력열 0,1,0,1이 되어 최종 0101입니다. 마지막으로 들어온 두 비트가 q[1:0]에 있으므로 그 두 위치가 달라집니다.</p>
</details>

## 다음으로 이어가기

다음 선택 심화는 이 직렬 연결로 내부 상태를 검사하는 스캔 체인입니다. 핵심 과정은 레슨18 메모리 배열로 이어갑니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.4.2, 인쇄 pp. 262–264 / PDF pp. 283–285. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
