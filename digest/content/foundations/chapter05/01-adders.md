## 이번 레슨의 목표

합 비트와 캐리를 구별하고 전가산기의 8가지 입력을 식과 수치로 검증합니다.

## 앞에서 배운 내용

1장의 이진 덧셈과 4장의 모듈을 연결합니다. 5장에서는 작은 회로를 조립하여 산술·저장·논리 블록을 만듭니다. 각 블록의 입력 폭과 기능을 먼저 약속합니다.

## 한 비트의 합도 두 자리까지 필요하다

반가산기(half adder)는 1비트 A와 B를 받아 S=A⊕B, C_out=A·B를 만듭니다. 1+1=10₂에서 오른쪽 0은 S, 왼쪽 1은 다음 자리로 넘길 캐리입니다. 출력이 둘이라고 서로 같은 정보를 중복 출력하는 것은 아닙니다.

전가산기(full adder)는 아래 자리에서 올라온 C_in도 더합니다. 식은 S=A⊕B⊕C_in, C_out=A·B+A·C_in+B·C_in입니다. 이 식의 +는 OR이고, 수치 검산에서는 A+B+C_in=2C_out+S라는 산술 관계를 사용합니다. 세 입력 중 1이 둘 이상이면 캐리가 1입니다.

```systemverilog
module ch5_fulladd(input logic a, b, cin,
                   output logic sum, cout);
  logic p, g;
  assign p = a ^ b;
  assign g = a & b;
  assign sum = p ^ cin;
  assign cout = g | (p & cin);
endmodule
```

여기서 내부 p는 합 계산용 XOR입니다. 뒤의 CLA 레슨에서는 책을 따라 OR 형태의 전파 신호를 P로 정의하므로 두 정의를 섞지 않습니다. 단일 비트 전가산기의 cout 식은 두 표현 모두 가능하지만 합 비트는 XOR로 계산합니다.

| A B C_in | S | C_out |
| --- | --- | --- |
| 000 / 001 | 0 / 1 | 0 / 0 |
| 010 / 011 | 1 / 0 | 0 / 1 |
| 100 / 101 | 1 / 0 | 0 / 1 |
| 110 / 111 | 0 / 1 | 1 / 1 |

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-1-t c5-1-d">
<title id="c5-1-t">반가산기와 전가산기: 한 자리 덧셈의 입출력</title>
<desc id="c5-1-d">전가산기의 입력과 두 출력 함수를 나란히 나타낸 개념도입니다. 클록이나 저장 소자는 없습니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">입력</text><text x="75" y="87">A·B·C_in</text><text x="223" y="59">합 S</text><text x="223" y="87">세 입력 XOR</text><text x="371" y="59">캐리 C_out</text><text x="371" y="87">1이 둘 이상</text></g>
</svg>
<p class="diagram-caption">그림 5-1. 전가산기의 입력과 두 출력 함수를 나란히 나타낸 개념도입니다. 클록이나 저장 소자는 없습니다.</p>

## 따라 풀기

A=1,B=0,C_in=1입니다. p=1⊕0=1, g=1·0=0이므로 S=1⊕1=0, C_out=0+(1·1)=1입니다. 산술로는 1+0+1=2, 출력으로는 2×1+0=2라 일치합니다. C_in이 없는 반가산기로 이 자리를 처리하면 결과가 1로 잘못됩니다.

## 헷갈리기 쉬운 점

반가산기의 반은 비트 폭이 절반이라는 뜻이 아니라 캐리 입력이 없다는 뜻입니다. 이 회로는 signed 여부를 판정하지 않으며 최상위 자리의 캐리만으로 부호 있는 오버플로를 알 수 없습니다.

## 직접 확인하기

1. 입력 111에서 S와 C_out은?
2. 전가산기에 C_in이 필요한 이유는?
3. A=B=0이면 C_in과 S의 관계는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 1과 1입니다. 3=2×1+1입니다.</p>
<p>2. 낮은 자리의 자리올림까지 더해야 여러 비트 덧셈이 되기 때문입니다.</p>
<p>3. S=C_in이고 C_out=0입니다.</p>
</details>

## 다음으로 이어가기

다음에는 전가산기를 여러 자리 연결하고 캐리가 이동하는 경로를 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.1–5.2.1, 인쇄 pp. 237–238 / PDF pp. 258–259. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
