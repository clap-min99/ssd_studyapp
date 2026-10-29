## 이번 레슨의 목표

조건 연산자로 MUX를 기술하고 연속 할당의 병렬성과 연산 우선순위를 설명합니다.

## 앞에서 배운 내용

2장에서 MUX는 선택 신호로 입력 하나를 골랐습니다. HDL의 조건식도 이 선택 회로와 연결해서 읽습니다.

## 중간 신호는 임시 실행 단계가 아니라 배선이다

```systemverilog
module select_mask(input logic [3:0] a, b, mask,
                   input logic s,
                   output logic [3:0] y);
  logic [3:0] picked;
  assign picked = s ? b : a;
  assign y = picked & mask;
endmodule
```

`조건 ? 참일 때 값 : 거짓일 때 값`에서 s=1이면 b, s=0이면 a를 고릅니다. picked는 외부 포트가 아닌 내부 신호입니다. 4비트 MUX 뒤에 4비트 AND가 연결되어 있습니다. `assign` 두 줄은 함께 존재하는 회로이므로, 두 줄의 위치를 바꿔도 안정된 함수는 같습니다. 각 줄을 한 클록씩 실행하는 뜻이 아닙니다.

4:1 선택은 `s[1] ? (s[0] ? d3 : d2) : (s[0] ? d1 : d0)`처럼 두 단계로 쓸 수 있습니다. s=10이면 먼저 상위 절반 d2·d3를 고르고 s[0]=0이므로 d2가 나옵니다. 각 단계와 신호의 폭을 먼저 확인합니다.

SystemVerilog에서 비트 AND는 XOR보다, XOR는 OR보다 우선합니다. `g | (p & c)`는 괄호를 빼도 같은 함수지만 `(g | p) & c`와는 다릅니다. 비교·시프트·산술식과 섞일 때는 우선순위를 외워 추측하기보다 의도한 묶음을 괄호로 표시합니다. `==`는 같음 비교이고 `=`는 할당입니다.

<svg viewBox="0 0 450 245" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-3-study-t c4-3-study-d">
<title id="c4-3-study-t">선택 후 마스킹하는 데이터 경로</title>
<desc id="c4-3-study-d">a와 b의 4비트 버스가 s로 선택되는 MUX에 들어가 picked를 만듭니다. picked와 mask를 비트별 AND하여 y를 냅니다. 클록 단계는 없습니다.</desc>
<rect x="105" y="65" width="90" height="90" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="150.0" y="115.0" font-size="15" text-anchor="middle" fill="var(--ink)">MUX</text><rect x="300" y="85" width="80" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="340.0" y="120.0" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><path d="M25 85 H105 M25 135 H105 M150 205 V155 M195 110 H300 M260 30 V135 H300 M380 115 H425" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="45" y="70" font-size="13" text-anchor="middle" fill="var(--ink)">a[3:0]</text><text x="45" y="160" font-size="13" text-anchor="middle" fill="var(--ink)">b[3:0]</text><text x="150" y="225" font-size="15" text-anchor="middle" fill="var(--ink)">s</text><text x="242" y="95" font-size="13" text-anchor="middle" fill="var(--ink)">picked</text><text x="263" y="20" font-size="13" text-anchor="middle" fill="var(--ink)">mask[3:0]</text><text x="421" y="98" font-size="14" text-anchor="middle" fill="var(--ink)">y</text>
</svg>
<p class="diagram-caption">그림 4-3. a와 b의 4비트 버스가 s로 선택되는 MUX에 들어가 picked를 만듭니다. picked와 mask를 비트별 AND하여 y를 냅니다. 클록 단계는 없습니다.</p>

## MUX와 AND를 식에서 한 블록씩 꺼내기

`picked=s?b:a`는 네 비트의 데이터를 고르는 MUX이고 `y=picked&mask`는 그 다음 비트별 AND입니다. 두 연산은 데이터 의존성 때문에 경로상 앞뒤가 있지만, 프로그램의 두 실행 단계나 두 클록을 뜻하지 않습니다. 입력이 바뀌면 MUX 출력이 변하고 이어 AND 출력이 안정됩니다.

내부 신호의 목적은 같은 식을 길게 반복하지 않고 블록 경계를 드러내는 것입니다. `assign y=(s?b:a)&mask`도 같은 안정 함수를 표현합니다. 내부 신호를 썼다고 자동으로 값이 저장되지 않습니다. 저장은 에지나 유지 조건을 가진 별도 회로 의미가 있어야 합니다.

검사할 때는 출력만 보지 말고 picked도 예상하세요. mask가 특정 비트를 지우면 MUX의 잘못된 선택이 최종 출력에서 가려질 수 있습니다. 먼저 mask=1111로 선택 기능을 확인하고, 그 다음 한 비트씩 0인 mask로 각 AND 경로를 검사하면 두 기능을 분리해서 이해할 수 있습니다.

## 따라 풀기

a=0011₂, b=1010₂, mask=0110₂, s=1입니다. picked=b=1010₂이고 y=1010₂ AND 0110₂=0010₂입니다. s만 0으로 바꾸면 picked=0011₂, y=0010₂로 출력이 우연히 같습니다. 따라서 s가 회로에 없다고 결론내리면 안 됩니다. mask=1111₂로 바꿔 다시 검사하면 두 선택 결과 0011₂와 1010₂가 드러납니다.

### 조건을 바꾸어 한 번 더 풀기

a=0101,b=1010에서 mask를 고정하지 않고 바꿔 봅니다.

| s | mask | picked | y |
| --- | --- | --- | --- |
| 0 | 1111 | 0101 | 0101 |
| 1 | 1111 | 1010 | 1010 |
| 1 | 0011 | 1010 | 0010 |
| 1 | 0000 | 1010 | 0000 |

마지막 행만 검사하면 선택기가 고장 나도 출력은 0000입니다. 입력 조합의 수를 채우기보다 실제로 다른 경로를 관찰하는 벡터를 고르는 것이 중요합니다.

## 헷갈리기 쉬운 점

연속 할당의 문장 순서와 한 always_comb 블록 안의 blocking 문장 순서는 다릅니다. 후자는 레슨 11에서 다룹니다. g=1,p=0,c=0이면 g|(p&c)=1이지만 (g|p)&c=0이므로 괄호를 마음대로 옮길 수 없습니다.

## 직접 확인하기

1. 4:1 식에서 s=01이면 어떤 입력을 고르나요?
2. picked를 output으로 선언해야 내부에서 쓸 수 있나요?
3. 두 assign 줄의 순서를 바꾸면 한 주기 늦어지나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. d1입니다. s[1]=0으로 아래쪽 두 입력을 고르고 s[0]=1로 d1을 선택합니다.</p>
<p>2. 아닙니다. 모듈 안에 logic으로 선언하면 내부 배선으로 쓸 수 있습니다.</p>
<p>3. 아닙니다. 연속 할당에는 클록이나 주기 지연이 없습니다. 실제 게이트의 물리 지연은 따로 존재합니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

s=0일 때 a가 선택되어야 하는데 코드가 `s?a:b`로 작성됐습니다. a·b·mask·s를 하나씩 정해 반드시 실패하는 검사 입력을 만들고, mask=0000이 왜 부적절한지 설명하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>a=0001,b=0010,mask=1111,s=0이면 기대 출력은 0001이고 잘못된 코드는 0010을 냅니다. 서로 다른 입력과 모든 비트를 통과시키는 mask를 선택했습니다.</p>
<p>mask=0000에서는 어느 입력을 잘못 선택해도 y=0000이라 오류가 가려집니다. 선택 회로와 후단 마스크를 분리해서 검사해야 합니다.</p>
</details>

## 다음으로 이어가기

다음에는 상수의 비트 폭과 버스를 잘라 붙이는 방법을 정합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.2.4–4.2.6, 인쇄 pp. 179–183 / PDF pp. 200–204. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
