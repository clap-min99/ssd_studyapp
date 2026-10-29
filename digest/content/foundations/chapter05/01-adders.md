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

<svg viewBox="0 0 450 245" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-1-study-t c5-1-study-d">
<title id="c5-1-study-t">반가산기 두 개로 구성한 전가산기</title>
<desc id="c5-1-study-d">A·B가 첫 반가산기로 h와 c0를 만들고,h·C_in이 둘째 반가산기로 S와 c1을 만듭니다. 두 캐리를 OR하여 C_out을 얻습니다. 기능 블록 기호입니다.</desc>
<rect x="75" y="45" width="100" height="65" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="125.0" y="82.5" font-size="15" text-anchor="middle" fill="var(--ink)">반가산기1</text><rect x="260" y="45" width="100" height="65" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="310.0" y="82.5" font-size="15" text-anchor="middle" fill="var(--ink)">반가산기2</text><rect x="260" y="165" width="100" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="310.0" y="192.5" font-size="15" text-anchor="middle" fill="var(--ink)">OR</text><path d="M20 65 H75 M20 90 H75 M175 65 H260 M205 90 H260 M360 75 H425 M125 110 V187 H260 M310 110 V165 M360 187 H425" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="30" y="50" font-size="14" text-anchor="middle" fill="var(--ink)">A</text><text x="30" y="117" font-size="14" text-anchor="middle" fill="var(--ink)">B</text><text x="220" y="52" font-size="14" text-anchor="middle" fill="var(--ink)">h</text><text x="220" y="112" font-size="14" text-anchor="middle" fill="var(--ink)">C_in</text><text x="420" y="60" font-size="14" text-anchor="middle" fill="var(--ink)">S</text><text x="150" y="170" font-size="14" text-anchor="middle" fill="var(--ink)">c0</text><text x="330" y="143" font-size="14" text-anchor="middle" fill="var(--ink)">c1</text><text x="408" y="222" font-size="14" text-anchor="middle" fill="var(--ink)">C_out</text>
</svg>
<p class="diagram-caption">그림 5-1. A·B가 첫 반가산기로 h와 c0를 만들고,h·C_in이 둘째 반가산기로 S와 c1을 만듭니다. 두 캐리를 OR하여 C_out을 얻습니다. 기능 블록 기호입니다.</p>

## 전가산기의 캐리식을 두 경우로 나누어 유도하기

세 입력의 1 개수를 먼저 세어 보면 합 S는 1이 홀수 개일 때 1이고, C_out은 1이 두 개 이상일 때 1입니다. 따라서 S는 세 입력 XOR이고 캐리는 세 쌍의 AND를 OR한 식입니다. 000·001·010·100은 캐리 0, 011·101·110·111은 캐리 1이라는 표가 이 식의 출발점입니다.

내부 신호 p=A XOR B,g=A·B로 다시 나누어 봅니다. A=B=1이면 g=1이므로 C_in에 관계없이 캐리가 나옵니다. A와 B 중 하나만 1이면 p=1이어서 C_in도 1일 때만 캐리가 생깁니다. A=B=0이면 둘 다 0이므로 캐리가 없습니다. 이 세 경우를 합치면 C_out=g+(p·C_in)입니다.

합과 캐리가 모두 필요한 이유는 0부터 3까지의 네 결과를 표현해야 하기 때문입니다. C_out을 상위 비트, S를 하위 비트로 연결한 두 비트가 전체 산술 합입니다. 출력 이름만 외우지 말고 각 입력에서 이 두 비트를 한 숫자로 다시 읽어 보세요.

## 따라 풀기

A=1,B=0,C_in=1입니다. p=1⊕0=1, g=1·0=0이므로 S=1⊕1=0, C_out=0+(1·1)=1입니다. 산술로는 1+0+1=2, 출력으로는 2×1+0=2라 일치합니다. C_in이 없는 반가산기로 이 자리를 처리하면 결과가 1로 잘못됩니다.

### 조건을 바꾸어 한 번 더 풀기

A=B=1을 고정하고 C_in만 바꿉니다.

| C_in | 전체 덧셈 | p | g | C_out·S |
| --- | --- | --- | --- | --- |
| 0 | 1+1+0=2 | 0 | 1 | 10 |
| 1 | 1+1+1=3 | 0 | 1 | 11 |

두 행 모두 캐리는 1이고 합 비트만 바뀝니다. 이제 A=1,B=0이면 g=0,p=1이므로 C_in=0에서는 01, C_in=1에서는 10입니다. ‘생성’과 ‘입력 캐리 의존’의 차이가 드러납니다.

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

### 적용 문제: 직접 구성하고 이유 설명하기

반가산기 두 개와 OR 한 개로 전가산기를 구성하세요. 첫 반가산기에 A·B를, 둘째에 첫 합과 C_in을 넣을 때 중간 합·두 캐리·최종 출력을 식으로 적고 A=0,B=1,C_in=1에서 검산하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>첫 합 h=A XOR B, 첫 캐리 c0=A·B입니다. 둘째 합 S=h XOR C_in, 둘째 캐리 c1=h·C_in이며 최종 C_out=c0+c1입니다.</p>
<p>입력 0,1,1에서 h=1,c0=0,S=0,c1=1이므로 출력은 10입니다. 두 캐리 중 하나라도 생기면 전체 합이 2 이상이므로 OR로 합치는 이유를 설명할 수 있습니다.</p>
</details>

## 다음으로 이어가기

다음에는 전가산기를 여러 자리 연결하고 캐리가 이동하는 경로를 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.1–5.2.1, 인쇄 pp. 237–238 / PDF pp. 258–259. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
