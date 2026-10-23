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

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-16-t c5-16-d">
<title id="c5-16-t">시프트 레지스터: 직렬·병렬 데이터 바꾸기</title>
<desc id="c5-16-d">새 입력·저장된 비트·직렬 출력의 관계를 나타낸 개념도입니다. 이동은 상승 에지에서만 일어납니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">serial_in</text><text x="75" y="87">에지에서 bit0로</text><text x="223" y="59">q[3:0]</text><text x="223" y="87">각 비트 한 칸 이동</text><text x="371" y="59">serial_out</text><text x="371" y="87">현재 q[3]</text></g>
</svg>
<p class="diagram-caption">그림 5-16. 새 입력·저장된 비트·직렬 출력의 관계를 나타낸 개념도입니다. 이동은 상승 에지에서만 일어납니다.</p>

## 따라 풀기

리셋 후 serial_in=1,0,1,1을 네 에지에 넣으면 q는 0001,0010,0101,1011입니다. 병렬 데이터 1011을 load한 뒤 serial_in=0으로 계속 shift하면 에지 직전 빠져나가는 비트는 1,0,1,1입니다. 각 에지 직후 q는 0110,1100,1000,0000입니다. serial_out의 에지 전 값과 직후 값을 뒤섞지 않으면 원래 1011을 복원할 수 있습니다.

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

## 다음으로 이어가기

다음 선택 심화는 이 직렬 연결로 내부 상태를 검사하는 스캔 체인입니다. 핵심 과정은 레슨18 메모리 배열로 이어갑니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.4.2, 인쇄 pp. 262–264 / PDF pp. 283–285. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
