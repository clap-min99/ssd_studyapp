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

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-3-t c4-3-d">
<title id="c4-3-t">조건 선택과 중간 신호: 식을 연결망으로 보기</title>
<desc id="c4-3-d">선택 결과 picked를 마스크 게이트에 연결하는 기능도입니다. 블록은 배선으로 연결되며 클록 단계는 없습니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">입력 a·b</text><text x="75" y="91">s로 하나 선택</text><text x="223" y="63">picked</text><text x="223" y="91">4비트 MUX 출력</text><text x="371" y="63">출력 y</text><text x="371" y="91">picked &amp; mask</text></g>
</svg>
<p class="diagram-caption">그림 4-3. 선택 결과 picked를 마스크 게이트에 연결하는 기능도입니다. 블록은 배선으로 연결되며 클록 단계는 없습니다.</p>

## 따라 풀기

a=0011₂, b=1010₂, mask=0110₂, s=1입니다. picked=b=1010₂이고 y=1010₂ AND 0110₂=0010₂입니다. s만 0으로 바꾸면 picked=0011₂, y=0010₂로 출력이 우연히 같습니다. 따라서 s가 회로에 없다고 결론내리면 안 됩니다. mask=1111₂로 바꿔 다시 검사하면 두 선택 결과 0011₂와 1010₂가 드러납니다.

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

## 다음으로 이어가기

다음에는 상수의 비트 폭과 버스를 잘라 붙이는 방법을 정합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.2.4–4.2.6, 인쇄 pp. 179–183 / PDF pp. 200–204. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
