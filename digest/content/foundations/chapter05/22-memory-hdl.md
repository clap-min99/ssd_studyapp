## 이번 레슨의 목표

RAM 배열 선언과 동기 쓰기·비동기 읽기를 추적하고 ROM case의 완전 할당을 확인합니다.

## 앞에서 배운 내용

4장의 always_ff와 assign을 메모리 인터페이스에 적용합니다. 레슨20의 레지스터 파일보다 단순한 단일 주소 RAM부터 봅니다.

## 동일한 배열에도 접근 시점의 약속이 필요하다

```systemverilog
module ch5_ram8x8(input logic clk, we,
                  input logic [2:0] addr, input logic [7:0] din,
                  output logic [7:0] dout);
  logic [7:0] mem [0:7];
  always_ff @(posedge clk)
    if (we) mem[addr] <= din;
  assign dout = mem[addr];
endmodule

module ch5_rom4x2(input logic [1:0] addr,
                  output logic [1:0] data);
  always_comb begin
    case (addr)
      2'b00: data = 2'b00;
      2'b01: data = 2'b10;
      2'b10: data = 2'b10;
      2'b11: data = 2'b01;
      default: data = '0;
    endcase
  end
endmodule
```

`logic [7:0] mem [0:7]`는 8비트 워드 여덟 개입니다. 앞의 범위는 워드 안의 비트, 뒤의 범위는 워드 인덱스입니다. RAM 쓰기는 상승 에지에서 we=1일 때만 일어납니다. 읽기는 주소 또는 해당 메모리 내용이 바뀌면 조합적으로 반영됩니다. 초기 내용은 쓰기나 초기화 전까지 미지입니다.

같은 주소를 읽으며 쓰면 에지 직전에는 옛 값이고 nonblocking 갱신 및 조합 평가 뒤에는 새 값입니다. 같은 에지에 읽기 출력을 저장하는 다른 레지스터는 직전 값을 읽는 모델입니다. FPGA의 특정 RAM 블록은 동기 읽기나 별도 read-during-write 정책을 요구할 수 있으므로 합성 추론 보고를 확인해야 합니다. 비동기 읽기 코드를 적었다고 모든 장치의 전용 block RAM이 같은 형태로 사용되는 것은 아닙니다.

ROM은 레슨21의 자체 표를 코드로 옮겼습니다. 모든 정상 주소와 default에서 출력이 정해져 저장 래치가 생기지 않습니다. RAM은 상태를 갖지만 고정 ROM 함수의 읽기 논리는 조합논리로 표현할 수 있습니다. 전체 메모리를 reset으로 지우는 코드는 구현 비용과 추론을 바꿀 수 있으므로 초기값 요구가 있을 때 별도로 설계합니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-22-t c5-22-d">
<title id="c5-22-t">메모리 HDL: 배열과 읽기·쓰기 시점</title>
<desc id="c5-22-d">RAM의 저장 조직과 접근 시점을 나란히 나타낸 기능 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">배열 선언</text><text x="75" y="87">8비트 워드 8개</text><text x="223" y="59">쓰기</text><text x="223" y="87">posedge·we=1</text><text x="371" y="59">읽기</text><text x="371" y="87">현재 addr의 mem 값</text></g>
</svg>
<p class="diagram-caption">그림 5-22. RAM의 저장 조직과 접근 시점을 나란히 나타낸 기능 개념도입니다.</p>

## 따라 풀기

addr=3,we=1,din=0x5A로 상승 에지를 맞으면 갱신 후 mem[3]=0x5A이고 dout도 0x5A입니다. we=0으로 바꾸고 din만 0xC3으로 바꿔도 저장값은 0x5A입니다. addr를 4로 바꾸면 dout은 mem[4]이며, 한 번도 쓰지 않았다면 시뮬레이션에서 X일 수 있습니다. ROM에 addr=3을 넣으면 주소 11의 데이터 01이 나옵니다.

## 헷갈리기 쉬운 점

RAM을 선언했다고 DRAM의 refresh가 이 코드에서 자동 구현되는 것은 아닙니다. 이 코드는 논리 메모리 모델이며 실제 저장 기술과 물리 인터페이스는 다른 층입니다. 검증에서 미작성 주소를 정답 0으로 가정하지 않습니다.

## 직접 확인하기

1. mem [0:7]과 [7:0] mem의 역할은?
2. we=1이지만 클록 에지가 없으면?
3. ROM의 default를 쓰는 이유는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 배열 쪽 범위는 워드 개수·인덱스, 앞 packed 범위는 워드 비트 폭을 정합니다.</p>
<p>2. 쓰기가 일어나지 않습니다.</p>
<p>3. 정확한 case에 맞지 않는 값까지 출력 경로를 정해 시뮬레이션 의미를 명확히 하기 위해서입니다.</p>
</details>

## 다음으로 이어가기

다음에는 최소항 전체 대신 필요한 곱항만 공유하는 PLA를 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.5.8, 인쇄 pp. 272–274 / PDF pp. 293–295. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
