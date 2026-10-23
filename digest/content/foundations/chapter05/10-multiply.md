## 이번 레슨의 목표

선택 심화입니다. 부분곱을 정렬하고 전체 결과 폭과 signed 해석을 설명합니다.

## 앞에서 배운 내용

왼쪽 시프트는 자릿값을 바꿉니다. 곱셈은 각 비트에 따라 원래 수 또는 0을 정렬하여 더합니다.

## 각 행은 AND, 행들의 결합은 덧셈이다

부호 없는 N×N 곱셈은 전체 결과에 최대 2N비트가 필요합니다. B_i=1이면 A를 i자리 왼쪽으로 옮긴 부분곱, 0이면 0입니다. 한 비트 곱셈은 AND이므로 N²개의 비트별 AND로 부분곱을 만들 수 있고 정렬한 행을 가산기로 합칩니다. 최종 셀 수와 지연은 합산 구조와 최적화에 따라 다릅니다.

```systemverilog
module ch5_mul4(input logic [3:0] a, b,
                output logic [7:0] unsigned_product,
                output logic signed [7:0] signed_product);
  assign unsigned_product = a * b;
  assign signed_product = $signed(a) * $signed(b);
endmodule
```

같은 패턴이어도 signed와 unsigned의 8비트 전체 곱은 다를 수 있습니다. 하위 4비트는 같지만 이 사실이 전체 곱도 같다는 뜻은 아닙니다. signed 부분곱은 부호 보정 없이 unsigned 배열에 그대로 적용할 수 없습니다.

곱하고 누적하는 MAC(multiply accumulate)은 A×B+누적값입니다. 예를 들어 계수와 샘플을 차례로 곱해 더하려면 곱셈기·가산기·누적 레지스터로 구성할 수 있습니다. 누적 폭·넘침 정책·처리 주기 수는 별도 명세입니다. *는 조합 함수 표현이며 자동으로 여러 주기 실행을 약속하지 않습니다. FPGA의 DSP 전용 블록 사용 여부도 합성 대상에 따릅니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-10-t c5-10-d">
<title id="c5-10-t">[선택 심화] 곱셈기와 MAC: 부분곱을 더하기</title>
<desc id="c5-10-d">부호 없는 곱셈의 부분곱 생성과 정렬을 나타낸 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">B_i=0</text><text x="75" y="87">해당 부분곱 0</text><text x="223" y="59">B_i=1</text><text x="223" y="87">A를 i자리 정렬</text><text x="371" y="59">행 합산</text><text x="371" y="87">최대 2N비트 결과</text></g>
</svg>
<p class="diagram-caption">그림 5-10. 부호 없는 곱셈의 부분곱 생성과 정렬을 나타낸 개념도입니다.</p>

## 따라 풀기

A=1001₂=9,B=0110₂=6입니다. 부분곱은 차례로 00000000,00010010,00100100,00000000입니다. 합은 00110110₂=54입니다. A를 signed −7로 읽고 B를 6으로 읽으면 −42로 11010110₂입니다. 두 결과 모두 하위 네 비트는 0110입니다. 초기값 2에 unsigned 곱 54를 누적하면 56으로 8비트 범위 안입니다.

## 헷갈리기 쉬운 점

N비트 결과만 받으면 상위 절반이 잘릴 수 있습니다. 출력만 signed로 선언해도 unsigned 피연산자의 해석이 저절로 고쳐지지는 않습니다. 코드 길이와 하드웨어 비용을 구별합니다.

## 직접 확인하기

1. 4비트 unsigned 최댓값끼리 곱하면?
2. 1111×0010의 signed 8비트 곱은?
3. MAC에서 저장 소자는 언제 필요한가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 225로 8비트 11100001입니다.</p>
<p>2. −2로 11111110입니다.</p>
<p>3. 이전 누적값을 다음 입력까지 유지해야 할 때입니다.</p>
</details>

## 다음으로 이어가기

다음에는 부분 나머지를 반복 갱신하는 나눗셈을 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.6, 인쇄 pp. 253–254 / PDF pp. 274–275. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
