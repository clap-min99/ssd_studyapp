## 이번 레슨의 목표

버스의 폭과 인덱스를 읽고 비트별·축약·논리 연산의 결과 폭을 구별합니다.

## 앞에서 배운 내용

1장의 게이트와 2장의 다입력 XOR를 HDL로 옮깁니다. 한 비트 회로를 네 개 나란히 놓는 경우와 네 비트를 하나로 모으는 경우는 다릅니다.

## 연산 기호보다 피연산자 수와 결과 폭을 본다

`logic [3:0] a`는 a[3]부터 a[0]까지 4비트입니다. 여기서는 오른쪽 비트 a[0]이 LSB입니다. `[7:0]`이면 8비트이며 `[N-1:0]` 꼴을 일관되게 사용합니다. 이 번호 순서는 메모리에 바이트를 배치하는 엔디언 규칙과 구별합니다.

```systemverilog
module flags4(input logic [3:0] a, b,
              output logic [3:0] masked, inverted,
              output logic any_set, all_set, odd);
  assign masked = a & b;
  assign inverted = ~a;
  assign any_set = |a;
  assign all_set = &a;
  assign odd = ^a;
endmodule
```

`a & b`, `a | b`, `a ^ b`는 대응하는 비트끼리 AND·OR·XOR하여 4비트를 만듭니다. `~a`도 각 비트를 반전합니다. 반면 피연산자가 하나인 `&a`, `|a`, `^a`는 축약(reduction)으로 버스 전체를 1비트로 모읍니다. `^a`는 1의 개수가 홀수일 때 1입니다. `~&a`, `~|a`, `~^a`는 각각 축약 결과의 반전입니다.

보충 비교로 `a && b`, `a || b`, `!a`는 논리 연산입니다. 이진 입력에서는 벡터가 0인지 아닌지를 참·거짓으로 해석하고 1비트 결과를 냅니다. 비트 마스크를 만들려면 `&&` 대신 `&`를 써야 합니다. X와 Z가 포함된 경우는 레슨 5에서 따로 봅니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-2-t c4-2-d">
<title id="c4-2-t">버스와 연산자: 비트별 연산과 축약 연산</title>
<desc id="c4-2-d">4비트 입력에 대한 세 연산의 결과 폭을 비교한 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">비트별</text><text x="75" y="91">a &amp; b → 4비트</text><text x="223" y="63">축약</text><text x="223" y="91">&amp;a → 1비트</text><text x="371" y="63">논리</text><text x="371" y="91">a &amp;&amp; b → 1비트</text></g>
</svg>
<p class="diagram-caption">그림 4-2. 4비트 입력에 대한 세 연산의 결과 폭을 비교한 개념도입니다.</p>

## 따라 풀기

a=1010₂, b=1100₂입니다. 위에서부터 각 열을 AND하면 1·1=1, 0·1=0, 1·0=0, 0·0=0이므로 masked=1000₂입니다. inverted=0101₂입니다. a에는 1이 두 개이므로 odd=0, 한 개 이상 있으므로 any_set=1, 모든 비트가 1은 아니므로 all_set=0입니다. a와 b는 둘 다 0이 아니므로 a&&b는 1입니다. 1000₂와 1은 결과 폭부터 다릅니다.

## 헷갈리기 쉬운 점

벡터 선언의 [3:0]은 네 비트이지 세 비트가 아닙니다. ^는 거듭제곱이 아니라 XOR입니다. 축약 XOR를 반복 적용하면 1의 홀짝을 구하지만 1의 개수 자체를 세지는 않습니다. 버스에 붙은 ~가 렌더링에서 취소선으로 보이지 않도록 코드를 코드 블록에 둡니다.

## 직접 확인하기

1. a=1110일 때 &a, |a, ^a는 얼마인가요?
2. a=0011, b=1100일 때 a&b와 a&&b는 어떻게 다른가요?
3. [5:0]의 폭과 최상위 비트 이름은 무엇인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0, 1, 1입니다. 1이 세 개라 홀수 패리티는 1입니다.</p>
<p>2. 비트별 결과는 0000이고 논리 결과는 1입니다. 두 입력 모두 0이 아닙니다.</p>
<p>3. 6비트이고 a라고 선언했다면 최상위는 a[5]입니다.</p>
</details>

## 다음으로 이어가기

다음에는 조건 연산자로 버스 하나를 고르고 중간 신호로 회로를 나눕니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.2.1–4.2.3, 인쇄 pp. 175–178 / PDF pp. 196–199. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
