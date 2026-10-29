## 이번 레슨의 목표

A−B를 고정 폭 덧셈으로 바꾸고 캐리·borrow·부호 있는 오버플로를 구별합니다.

## 앞에서 배운 내용

1장의 2의 보수는 모든 비트를 반전하고 1을 더했습니다. 이 과정을 덧셈기의 입력 경로로 만듭니다.

## B의 반전과 마지막 1을 한 덧셈기에 넣는다

N비트에서 A−B는 A+¬B+1의 하위 N비트입니다. ¬B는 N비트 안에서의 반전입니다. sub=0이면 A+B, sub=1이면 A−B를 수행하도록 B의 각 비트를 sub와 XOR하고 입력 캐리도 sub로 둡니다.

```systemverilog
module ch5_addsub4(input logic [3:0] a, b, input logic sub,
                   output logic [3:0] result, output logic carry);
  logic [3:0] bx;
  assign bx = b ^ {4{sub}};
  assign {carry,result} = {1'b0,a} + {1'b0,bx} + {4'b0000,sub};
endmodule
```

sub=1에서 연산은 2⁴+A−B입니다. 따라서 부호 없는 A≥B이면 carry=1, A<B이면 carry=0입니다. 이 정의의 캐리는 뺄셈에서 ‘빌림이 없음’을 나타내므로 borrow=¬carry입니다. 다른 장치의 상태 플래그 명세와 같은 이름이라고 무조건 같은 극성으로 가정하지 않습니다.

부호 있는 오버플로는 수학적 결과가 −8부터 7까지 범위를 벗어나는 사건입니다. carry와는 다른 질문입니다. 뺄셈의 오버플로 식은 `(A_msb⊕B_msb)·(A_msb⊕S_msb)`이며, 두 입력의 부호가 다르고 결과 부호가 A와 달라질 때입니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-5-t c5-5-d">
<title id="c5-5-t">덧셈·뺄셈 공유: 반전과 Carry-in</title>
<desc id="c5-5-d">하나의 덧셈기로 덧셈과 뺄셈을 선택하는 입력 경로 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">sub=0</text><text x="75" y="87">B 그대로·C_in=0</text><text x="223" y="59">sub=1</text><text x="223" y="87">B 반전·C_in=1</text><text x="371" y="59">출력</text><text x="371" y="87">하위 합·최종 캐리</text></g>
</svg>
<p class="diagram-caption">그림 5-5. 하나의 덧셈기로 덧셈과 뺄셈을 선택하는 입력 경로 개념도입니다.</p>

## Modulo 연산에서 반전과 빌림을 유도하기

N비트 B의 비트 반전은 수치로 2ᴺ−1−B입니다. 여기에 1을 더하면 2ᴺ−B이므로 A+¬B+1=2ᴺ+A−B입니다. 하위 N비트만 남기면 2ᴺ은 사라져 A−B의 modulo 2ᴺ 결과가 됩니다. 이 유도에서 반전 폭 N과 마지막 +1이 모두 필요합니다.

A≥B이면 확장 합이 2ᴺ 이상이어서 carry=1이고 하위 결과는 A−B입니다. A<B이면 확장 합이 2ᴺ 미만이라 carry=0이고 하위 결과는 음수 차를 modulo로 감싼 값입니다. 따라서 unsigned 빌림은 이 carry의 부정입니다.

signed overflow는 다른 조건입니다. 양수에서 음수를 빼면 결과가 더 커져 넘칠 수 있고, 음수에서 양수를 빼면 더 작아져 넘칠 수 있습니다. 같은 부호끼리 빼면 수학적 차가 N비트 signed 범위 안이므로 이 종류의 overflow는 없습니다. 결과의 부호 비트만 보고 판단하지 말고 원래 두 수의 해석과 허용 범위를 확인합니다.

## 따라 풀기

4비트 A=0010,B=0101입니다. B 반전은 1010이고 0010+1010+1=01101입니다. result=1101,carry=0이므로 부호 없는 2−5는 borrow가 있습니다. 같은 결과를 2의 보수로 읽으면 −3입니다. A=0111,B=1111이면 7−(−1)=8이지만 result=1000으로 −8처럼 보이며 signed overflow=1입니다. 입력 비트가 같아도 어떤 수로 해석하는지 먼저 정합니다.

### 조건을 바꾸어 한 번 더 풀기

4비트 A=0101,B=0010에서 ¬B=1101입니다. 확장 합 00101+01101+00001=10011이므로 결과 0011,carry=1입니다. unsigned 5−2=3이고 빌림이 없습니다.

순서를 바꾸어 A=0010,B=0101이면 ¬B=1010이고 확장 합 01101이므로 carry=0,result=1101입니다. unsigned 결과는 13으로 감싸졌고, 같은 패턴을 signed로 읽으면 −3입니다. 두 경우를 함께 풀면 carry가 no-borrow라는 극성이 명확해집니다.

## 헷갈리기 쉬운 점

반전 뒤의 +1을 빼거나 두 번 넣지 않습니다. 고정 폭 결과의 음수처럼 보이는 패턴과 실제 unsigned 음수 표현은 다릅니다. 부호 없는 결과는 modulo 16으로 돌아옵니다.

## 직접 확인하기

1. 4비트 1001−0011의 결과와 carry는?
2. carry=1이면 signed overflow도 1인가요?
3. sub=0에서 bx는 무엇인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0110과 1입니다. 부호 없는 9−3=6으로 빌림이 없습니다.</p>
<p>2. 아닙니다. 캐리와 부호 범위 초과는 별도입니다.</p>
<p>3. b 그대로입니다. 0과 XOR하면 바뀌지 않습니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

4비트 signed A=1000,B=0001에서 뺄셈 결과·carry·overflow를 구하세요. unsigned 해석에서는 같은 결과를 어떻게 설명하나요?

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>1000+1110+1=10111이므로 result=0111,carry=1입니다. signed로 −8−1=−9는 범위 밖이며 +7 패턴으로 돌아왔으므로 overflow=1입니다.</p>
<p>unsigned로 8−1=7은 정상이며 carry=1은 빌림 없음을 나타냅니다. 같은 carry=1에서 signed overflow도 발생할 수 있으므로 두 판정을 별도로 해야 합니다.</p>
</details>

## 다음으로 이어가기

다음에는 뺄셈 결과를 이용한 비교에서 오버플로를 보정합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.2, 인쇄 pp. 244–245 / PDF pp. 265–266. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
