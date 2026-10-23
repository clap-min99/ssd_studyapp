## 이번 레슨의 목표

동등 비교와 크기 비교를 구별하고 뺄셈 부호만 보는 비교의 반례를 설명합니다.

## 앞에서 배운 내용

덧셈·뺄셈기는 같은 비트 연산을 수행해도 signed·unsigned 해석에 따라 의미가 달랐습니다.

## 같은 패턴과 같은 크기 해석을 구별한다

동등 비교기는 각 자리의 A와 B를 XNOR하고 그 결과를 모두 AND합니다. `equal=¬(A0⊕B0)·¬(A1⊕B1)·…`입니다. 하나라도 다른 자리가 있으면 같지 않습니다. HDL의 `==`·`!=`는 1비트 결과를 내며 X·Z가 있으면 결과가 미지일 수 있으므로 검증에서는 입력 유효성도 봅니다.

크기 비교는 부호 해석이 필요합니다. unsigned는 최상위에서 처음 다른 자리를 비교해 결정할 수 있습니다. signed는 최상위 비트가 부호이므로 같은 해석을 그대로 적용할 수 없습니다.

```systemverilog
module ch5_compare4(input logic [3:0] a, b,
                    output logic eq, unsigned_lt, signed_lt);
  assign eq = (a == b);
  assign unsigned_lt = (a < b);
  assign signed_lt = ($signed(a) < $signed(b));
endmodule
```

두 피연산자를 모두 같은 4비트 signed로 해석했습니다. 한쪽만 캐스팅하거나 폭이 다른 피연산자를 섞어 원래 의도와 다르게 확장하지 않습니다. `<=`는 식 안에서는 작거나 같음 비교이고 always_ff의 할당 위치에서는 nonblocking입니다.

A−B의 최상위 비트를 N_flag, 뺄셈 오버플로를 V, carry-out을 C라 부르면 signed의 A<B는 N_flag⊕V, unsigned의 A<B는 ¬C입니다. 단순히 차의 부호만 보면 signed overflow에서 틀립니다. 상태 플래그가 없어도 HDL 비교 연산자로 폭·부호를 명시할 수 있습니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-6-t c5-6-d">
<title id="c5-6-t">비교기: 비트의 같음과 수의 크기</title>
<desc id="c5-6-d">비교 목적과 뺄셈 기반 판정 신호를 비교한 개념도입니다. C는 이 장의 no-borrow 정의입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">동등</text><text x="75" y="87">각 자리 XNOR·AND</text><text x="223" y="59">unsigned 크기</text><text x="223" y="87">A−B의 NOT C</text><text x="371" y="59">signed 크기</text><text x="371" y="87">A−B의 N XOR V</text></g>
</svg>
<p class="diagram-caption">그림 5-6. 비교 목적과 뺄셈 기반 판정 신호를 비교한 개념도입니다. C는 이 장의 no-borrow 정의입니다.</p>

## 따라 풀기

A=1000₂,B=0011₂입니다. unsigned로는 8<3이 거짓이고 signed로는 −8<3이 참입니다. 4비트 차는 0101₂여서 N=0이지만 실제 −11이 표현 범위를 벗어나 V=1입니다. N⊕V=1로 보정하면 참입니다. A와 B의 패턴은 다르므로 eq=0이며 이 결론은 부호 해석과 관계없습니다.

## 헷갈리기 쉬운 점

비교 결과 1은 참을 나타내는 한 비트입니다. SLT처럼 넓은 버스의 숫자 1을 만드는 회로는 별도 확장이 필요합니다. N_flag는 입력 폭 N과 구별합니다.

## 직접 확인하기

1. 1110과 0010의 unsigned/signed 작은가 결과는?
2. 같은 폭 정상 입력에서 A−B=0이면?
3. signed 비교에 N만 쓰면 왜 안 되나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. unsigned는 거짓, signed는 참입니다. 14와 −2의 해석이 다릅니다.</p>
<p>2. A와 B가 같습니다.</p>
<p>3. 오버플로로 차의 부호가 뒤집힐 수 있습니다.</p>
</details>

## 다음으로 이어가기

다음에는 덧셈·뺄셈·논리 연산을 ALU에 묶습니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.3–5.2.4, 인쇄 pp. 245–250 / PDF pp. 266–271. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
