## 이번 레슨의 목표

선택 심화입니다. parameter의 기본값·재정의와 실행 중 입력을 구별하고 매개변수 디코더의 출력을 계산합니다.

## 앞에서 배운 내용

레슨 6에서는 고정 폭의 작은 모듈을 연결했습니다. 폭만 다른 같은 기능을 매번 복사하지 않도록 매개변수로 묶습니다.

## 회로를 구성할 때 정하는 상수다

```systemverilog
module choose_n #(parameter int W = 5)
  (input logic [W-1:0] a, b, input logic s,
   output logic [W-1:0] y);
  assign y = s ? b : a;
endmodule

module choose10(input logic [9:0] a, b, input logic s,
                 output logic [9:0] y);
  choose_n #(.W(10)) u_pick(.a(a), .b(b), .s(s), .y(y));
endmodule
```

W는 기본 5이며 인스턴스에서 이름 기반 `#(.W(10))`으로 10으로 정했습니다. 회로를 구성하는 elaboration 단계에서 포트 폭과 구조가 결정됩니다. 동작 중 s를 바꾸면 입력 선택이 바뀌지만 W를 입력처럼 매 주기 바꿀 수는 없습니다. 이 예제는 W≥1을 전제로 합니다. W=0이면 `[W-1:0]`이 빈 버스가 된다고 가정하지 말고 유효하지 않은 설정으로 취급합니다.

아래는 N비트 주소를 2의 N승 개 출력으로 바꾸는 디코더입니다. N은 작은 양의 정수로 제한해 사용합니다.

```systemverilog
module decode_n #(parameter int N = 2)
  (input logic [N-1:0] addr,
   output logic [(2**N)-1:0] onehot);
  always_comb begin
    onehot = '0;
    onehot[addr] = 1'b1;
  end
endmodule
```

먼저 전체 출력을 0으로 만든 뒤 선택한 비트만 1로 덮어씁니다. 기본값은 매 조합 평가마다 적용되므로 이전 주소의 1이 남지 않습니다. 코드의 별표 두 개는 거듭제곱이며 XOR인 `^`와 다릅니다. N이 하나 늘 때 출력 폭은 두 배가 되므로 간단한 코드라도 회로 비용이 빠르게 늘 수 있습니다. VHDL에서는 이 역할에 generic을 사용합니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-16-t c4-16-d">
<title id="c4-16-t">[선택 심화] 매개변수 모듈: 폭을 정해 재사용하기</title>
<desc id="c4-16-d">구성 시 정하는 폭과 동작 중 바뀌는 선택 신호를 비교한 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">W 기본값 5</text><text x="75" y="91">5비트 선택 회로</text><text x="223" y="63">W 재정의 10</text><text x="223" y="91">10비트 선택 회로</text><text x="371" y="63">실행 중 s</text><text x="371" y="91">폭 고정·선택 변경</text></g>
</svg>
<p class="diagram-caption">그림 4-16. 구성 시 정하는 폭과 동작 중 바뀌는 선택 신호를 비교한 개념도입니다.</p>

## 따라 풀기

choose10에서 a=10'b00000_00101, b=10'b10000_00001, s=1이면 y=b입니다. 10비트 폭이므로 상위 1도 보존됩니다. decode_n의 N=3이면 출력 폭은 2³=8비트이고 addr=101₂=5이면 onehot[5]=1, 나머지 0이므로 00100000₂입니다. addr=2로 바꾸면 00000100₂로 바뀌어 이전 bit5는 0이 됩니다.

## 헷갈리기 쉬운 점

#(.W(10))은 매개변수 재정의이고 #10은 시뮬레이션 지연이므로 같은 # 기호라도 문맥이 다릅니다. 매개변수의 폭과 연결 신호 폭이 맞는지 확인합니다. 디코더에서 미지 주소는 정상 one-hot 출력을 보장하지 않으며 검증 대상입니다.

## 직접 확인하기

1. W=7이면 choose_n의 입력 a는 몇 비트인가요?
2. N=4 디코더의 출력 폭과 addr=3의 패턴은 무엇인가요?
3. parameter를 입력 포트처럼 매 클록 갱신할 수 있나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 7비트입니다. 범위는 [6:0]입니다.</p>
<p>2. 16비트이고 0000000000001000입니다.</p>
<p>3. 아닙니다. 인스턴스의 구조를 정할 때 결정되는 값입니다.</p>
</details>

## 다음으로 이어가기

다음 선택 심화에서는 generate로 반복된 연결을 구성합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.8, 인쇄 pp. 215–217 / PDF pp. 236–238. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
