## 이번 레슨의 목표

선택 심화입니다. generate 반복과 시뮬레이션 반복을 구별하고 경계 폭과 하드웨어 비용을 확인합니다.

## 앞에서 배운 내용

매개변수는 버스 폭을 바꿨습니다. 이제 폭에 따라 배선과 연산 블록의 개수도 함께 바꿉니다.

## 반복 횟수만큼 구조가 생긴다

아래는 입력 비트가 누적해서 XOR되는 연결을 만듭니다. prefix[k]는 a[0]부터 a[k]까지의 패리티이고 마지막 parity는 전체 패리티입니다. W≥1을 전제로 합니다.

```systemverilog
module parity_chain #(parameter int W = 5)
  (input logic [W-1:0] a,
   output logic parity);
  logic [W-1:0] prefix;
  assign prefix[0] = a[0];
  genvar k;
  generate
    for (k = 1; k < W; k = k + 1) begin : g_xor
      assign prefix[k] = prefix[k-1] ^ a[k];
    end
  endgenerate
  assign parity = prefix[W-1];
endmodule
```

genvar는 회로를 구성할 때 사용하는 인덱스입니다. W=5이면 k=1,2,3,4에 해당하는 네 XOR 연결이 만들어집니다. begin 뒤의 g_xor는 생성 블록의 이름이며 각 인덱스로 구별됩니다. 루프가 4클록 동안 실행되어 하나씩 XOR하는 의미가 아닙니다. 클록이나 저장 소자는 없습니다.

W=1일 때 반복은 한 번도 생성되지 않고 prefix[0]=a[0]이 곧 parity입니다. 첫 비트를 별도로 처리했기 때문에 prefix[-1] 접근이 생기지 않습니다. 입력의 일부만 바뀌어도 연결된 조합논리는 그 변화에 반응합니다.

이 기능만 필요하면 `assign parity = ^a;`가 더 간단합니다. 체인 예제는 구조 생성 원리를 배우기 위한 것이며 최적 회로 권장이 아닙니다. 직접 기술한 연결은 직렬 의존성을 보이지만 실제 합성기는 재구성할 수 있습니다. 코드 줄 수가 적다고 면적이나 임계 경로가 작다고 판단하지 않습니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-17-t c4-17-d">
<title id="c4-17-t">[선택 심화] Generate: 반복문으로 회로 구성하기</title>
<desc id="c4-17-d">패리티 체인의 첫 연결과 반복 연결, 최종 출력을 요약한 기능도입니다. 중간 k=2부터 W−2 연결은 생략했습니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">prefix[0]</text><text x="75" y="91">a[0]</text><text x="223" y="63">prefix[1]</text><text x="223" y="91">prefix[0] XOR a[1]</text><text x="371" y="63">prefix[W−1]</text><text x="371" y="91">전체 입력 패리티</text></g>
</svg>
<p class="diagram-caption">그림 4-17. 패리티 체인의 첫 연결과 반복 연결, 최종 출력을 요약한 기능도입니다. 중간 k=2부터 W−2 연결은 생략했습니다.</p>

## 따라 풀기

W=5,a=10110₂입니다. a[0]부터 읽으면 0,1,1,0,1입니다. prefix[0]=0, prefix[1]=0⊕1=1, prefix[2]=1⊕1=0, prefix[3]=0⊕0=0, prefix[4]=0⊕1=1입니다. 전체 1의 개수는 세 개이므로 ^a=1과 일치합니다. XOR 연결은 W−1=4개이며 이를 4클록 지연으로 해석하면 안 됩니다.

## 헷갈리기 쉬운 점

generate의 조건·반복 범위는 구성 시 결정되어야 합니다. 입력값이 바뀔 때 회로 개수가 실시간으로 늘어나는 구조가 아닙니다. always_comb 안의 정해진 횟수 for도 합성 시 펼쳐질 수 있지만 genvar와 generate의 구조 구성 문맥과는 구별합니다.

## 직접 확인하기

1. W=1에서 parity는 무엇인가요?
2. W=8에서 이 체인이 기술하는 XOR 연결은 몇 개인가요?
3. a=1111이면 최종 패리티는 무엇인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. a[0] 그대로입니다. 반복 블록이 생성되지 않습니다.</p>
<p>2. 7개입니다. 실제 합성 결과의 셀 수는 최적화에 따라 달라질 수 있습니다.</p>
<p>3. 0입니다. 1이 네 개로 짝수입니다.</p>
</details>

## 다음으로 이어가기

이제 핵심 과정으로 돌아와 만들어진 회로에 입력을 넣고 자동으로 검사합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.8, 인쇄 pp. 217–218 / PDF pp. 238–239. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
