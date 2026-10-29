## 이번 레슨의 목표

독립 읽기 주소와 동기 쓰기를 추적하고 0번 엔트리 및 동시 접근의 명세를 정합니다.

## 앞에서 배운 내용

배열은 많은 워드를 주소로 골랐습니다. 연산기에 두 입력을 동시에 주려면 두 읽기 포트가 유용합니다.

## 연산 입력 둘을 읽고 결과 하나를 저장한다

레지스터 파일(register file)은 작은 워드 집합에 여러 포트를 제공하는 블록입니다. 두 읽기 포트는 서로 다른 주소의 값을 함께 내고 한 쓰기 포트는 클록 에지에서 선택 워드를 갱신합니다. SRAM이나 플립플롭 등 실제 구현은 포트 수·기술·합성 결과에 따라 달라집니다.

```systemverilog
module ch5_regfile8(input logic clk, we,
                    input logic [2:0] ra, rb, wa,
                    input logic [7:0] wd,
                    output logic [7:0] rd_a, rd_b);
  logic [7:0] regs [0:7];
  always_ff @(posedge clk)
    if (we && (wa != 3'd0)) regs[wa] <= wd;
  assign rd_a = (ra == 3'd0) ? 8'd0 : regs[ra];
  assign rd_b = (rb == 3'd0) ? 8'd0 : regs[rb];
endmodule
```

8워드×8비트의 주소는 3비트입니다. ra·rb는 읽기, wa는 쓰기 주소입니다. 0번은 언제나 0으로 읽고 쓰기를 무시하도록 명시했습니다. 나머지 엔트리는 초기화하지 않았으므로 처음에는 X일 수 있습니다. 모든 레지스터 파일이 0번을 고정하는 것은 아닙니다.

이 RTL은 비동기 읽기·상승 에지 쓰기입니다. ra=wa이면 에지 직전에는 옛 값, nonblocking 갱신 후 조합논리가 반영되면 새 값을 봅니다. 같은 에지에 rd_a를 받는 다른 레지스터는 옛 값을 샘플한다는 사건 순서를 구별합니다. 물리 메모리 매크로의 동시 읽기/쓰기 동작은 별도 명세를 확인해야 하며 이 모델을 그대로 보장한다고 가정하지 않습니다.

원문 32워드 예제는 주소 선언이 6비트로 인쇄되어 있지만 실제 32엔트리에는 5비트면 충분합니다. 여기서는 독립적인 8워드 예제에서 3비트 주소와 배열 범위를 일치시킵니다.

<svg viewBox="0 0 450 295" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-20-study-t c5-20-study-d">
<title id="c5-20-study-t">두 읽기 포트와 한 쓰기 포트의 독립 주소</title>
<desc id="c5-20-study-d">ra·rb는 독립 읽기 주소이고 rd_a·rd_b는 각각의 8비트 데이터입니다. wa·wd·we는 클록 에지 쓰기 경로입니다. 배열 내부 디코더와 0번 상수 선택은 생략한 인터페이스 기능도입니다.</desc>
<rect x="155" y="40" width="145" height="180" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="227.5" y="135.0" font-size="15" text-anchor="middle" fill="var(--ink)">8 × 8 배열</text><path d="M35 65 H155 M35 105 H155 M35 145 H155 M35 185 H155 M225 250 V220 M300 85 H425 M300 175 H425" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="75" y="53" font-size="14" text-anchor="middle" fill="var(--ink)">ra[2:0]</text><text x="75" y="93" font-size="14" text-anchor="middle" fill="var(--ink)">rb[2:0]</text><text x="75" y="133" font-size="14" text-anchor="middle" fill="var(--ink)">wa[2:0]</text><text x="75" y="173" font-size="13" text-anchor="middle" fill="var(--ink)">wd[7:0]·we</text><text x="225" y="273" font-size="14" text-anchor="middle" fill="var(--ink)">clk</text><text x="368" y="70" font-size="14" text-anchor="middle" fill="var(--ink)">rd_a[7:0]</text><text x="368" y="160" font-size="14" text-anchor="middle" fill="var(--ink)">rd_b[7:0]</text>
</svg>
<p class="diagram-caption">그림 5-20. ra·rb는 독립 읽기 주소이고 rd_a·rd_b는 각각의 8비트 데이터입니다. wa·wd·we는 클록 에지 쓰기 경로입니다. 배열 내부 디코더와 0번 상수 선택은 생략한 인터페이스 기능도입니다.</p>

## 한 쓰기가 두 읽기 출력에 언제 보이는가

두 읽기 포트는 서로 다른 행을 선택하는 두 주소와 두 데이터 출력을 가집니다. ra와 rb가 같으면 같은 행을 동시에 읽을 수도 있습니다. 하나의 8비트 출력을 두 용도로 나눠 쓰는 회로와는 인터페이스가 다릅니다.

쓰기는 we=1인 상승 에지에서 wa가 가리키는 행 하나에 wd를 저장합니다. 비동기 읽기에서는 그 행을 읽는 출력이 갱신 뒤 새 값으로 바뀝니다. 하지만 같은 상승 에지에 다른 레지스터가 rd_a를 샘플했다면 아직 옛 값을 읽었습니다. ‘동시에 읽고 쓸 수 있다’는 말만으로 새 값 우선인지 옛 값 우선인지 결론낼 수 없습니다.

0번 엔트리는 읽기 MUX가 상수 0을 선택하고 쓰기 조건에서도 제외됩니다. 배열의 regs[0] 자체를 초기화하는 대신 외부 계약을 0으로 보장합니다. 다른 엔트리는 쓰기 전 미지이므로 전체를 0이라고 가정하는 테스트는 틀립니다. 필요한 주소를 먼저 쓰는 준비 단계를 포함합니다.

## 따라 풀기

이미 regs[2]=0x12,regs[5]=0xA0을 썼다고 합시다. ra=2,rb=5이면 출력은 각각 0x12,0xA0입니다. wa=2,wd=0x34,we=1인 상승 에지 뒤에는 rd_a가 0x34로 바뀌고 rd_b는 0xA0을 유지합니다. 다음에 wa=0으로 0xFF를 써도 rd_a의 주소를 0으로 두면 0입니다. 읽기 주소와 쓰기 주소가 독립이라는 점을 한 행씩 추적하면 됩니다.

### 조건을 바꾸어 한 번 더 풀기

regs[2]=0x12,ra=rb=wa=2,we=1,wd=0x34라고 합시다.

| 관찰 시점 | rd_a | rd_b | 이유 |
| --- | --- | --- | --- |
| 상승 에지 직전 | 0x12 | 0x12 | 아직 옛 배열 값 |
| 같은 에지에서 별도 레지스터가 샘플 | 옛 값 0x12 | 옛 값 0x12 | nonblocking 갱신 전 |
| 배열 갱신과 조합 평가 후 | 0x34 | 0x34 | 같은 행의 새 값 |

읽기 주소 하나를 0으로 바꾸면 해당 출력은 그 시점부터 상수 0을 선택합니다. 실제 메모리 매크로로 바꿀 때는 이 기능 모델과 read-during-write 명세가 맞는지 따로 확인합니다.

## 헷갈리기 쉬운 점

물리 저장 비트 수 8×8=64와 0번을 상수로 처리한 구현의 최적화된 셀 수는 다를 수 있습니다. 포트 하나당 전체 배열이 무조건 복제된다고 가정하지 않습니다. 읽기 주소 유효성과 쓰기 이전의 초기 상태를 검증합니다.

## 직접 확인하기

1. 32워드에 필요한 주소 폭은?
2. we=0이면 쓰기 데이터가 바뀌어도 저장되나요?
3. 이 예제에서 0번에 써도 읽기가 0인 이유는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 5비트입니다.</p>
<p>2. 아닙니다.</p>
<p>3. 쓰기를 막고 읽기에서도 주소 0을 상수 0으로 선택하기 때문입니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

regs[1]·regs[3]에 각각 0x11·0x33을 쓴 뒤 ra=1,rb=3으로 둡니다. wa=1,wd=0xAA,we=0인 에지와 이어 we=1인 에지 후 두 출력을 적으세요. 주소 0 쓰기도 함께 검사하려면 어떤 기대값을 사용하나요?

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>we=0인 에지 후에는 0x11,0x33 그대로입니다. 이어 we=1인 에지의 갱신 후에는 0xAA,0x33입니다. 선택하지 않은 행은 바뀌지 않습니다.</p>
<p>wa=0으로 임의 데이터를 쓰려 한 뒤 ra 또는 rb를 0으로 두고 항상 0을 기대합니다. 쓰기 금지와 상수 읽기 계약을 정상 행 갱신 검사와 구별합니다.</p>
</details>

## 다음으로 이어가기

다음에는 제조·설정된 표를 읽는 ROM과 LUT를 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.5.5, 5.5.8, 인쇄 pp. 269, 272–274 / PDF pp. 290, 293–295. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
