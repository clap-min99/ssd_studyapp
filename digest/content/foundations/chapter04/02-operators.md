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

<svg viewBox="0 0 450 255" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-2-study-t c4-2-study-d">
<title id="c4-2-study-t">비트별 AND 네 개와 축약 AND 하나</title>
<desc id="c4-2-study-d">왼쪽은 각 자리 a·b가 별개 AND로 y의 네 비트를 만드는 기능도입니다. 오른쪽은 a의 네 비트를 모으는 축약 AND를 기호화했습니다.</desc>
<text x="28" y="43" font-size="13" text-anchor="middle" fill="var(--ink)">a[3]</text><text x="100" y="43" font-size="13" text-anchor="middle" fill="var(--ink)">b[3]</text><rect x="150" y="23" width="65" height="32" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="44.0" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><path d="M48 38 H63 V30 H150 M120 38 H132 V46 H150 M215 38 H265" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="300" y="43" font-size="14" text-anchor="middle" fill="var(--ink)">y[3]</text><text x="28" y="90" font-size="13" text-anchor="middle" fill="var(--ink)">a[2]</text><text x="100" y="90" font-size="13" text-anchor="middle" fill="var(--ink)">b[2]</text><rect x="150" y="70" width="65" height="32" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="91.0" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><path d="M48 85 H63 V77 H150 M120 85 H132 V93 H150 M215 85 H265" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="300" y="90" font-size="14" text-anchor="middle" fill="var(--ink)">y[2]</text><text x="28" y="137" font-size="13" text-anchor="middle" fill="var(--ink)">a[1]</text><text x="100" y="137" font-size="13" text-anchor="middle" fill="var(--ink)">b[1]</text><rect x="150" y="117" width="65" height="32" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="138.0" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><path d="M48 132 H63 V124 H150 M120 132 H132 V140 H150 M215 132 H265" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="300" y="137" font-size="14" text-anchor="middle" fill="var(--ink)">y[1]</text><text x="28" y="184" font-size="13" text-anchor="middle" fill="var(--ink)">a[0]</text><text x="100" y="184" font-size="13" text-anchor="middle" fill="var(--ink)">b[0]</text><rect x="150" y="164" width="65" height="32" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="185.0" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><path d="M48 179 H63 V171 H150 M120 179 H132 V187 H150 M215 179 H265" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="300" y="184" font-size="14" text-anchor="middle" fill="var(--ink)">y[0]</text><path d="M338 35 V180 M338 105 H365 M345 98 L355 112 M430 105 H445" fill="none" stroke="var(--ink)" stroke-width="2"/><rect x="365" y="85" width="65" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="397.5" y="110.0" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><text x="385" y="150" font-size="14" text-anchor="middle" fill="var(--ink)">&amp;a</text><text x="385" y="177" font-size="14" text-anchor="middle" fill="var(--ink)">1비트</text><text x="375" y="25" font-size="13" text-anchor="middle" fill="var(--ink)">a[3:0]</text><text x="215" y="235" font-size="12" text-anchor="middle" fill="var(--ink)">왼쪽: a &amp; b는 자리마다 게이트 · 오른쪽: &amp;a는 전체 축약</text>
</svg>
<p class="diagram-caption">그림 4-2. 왼쪽은 각 자리 a·b가 별개 AND로 y의 네 비트를 만드는 기능도입니다. 오른쪽은 a의 네 비트를 모으는 축약 AND를 기호화했습니다.</p>

## 같은 AND 기호를 회로 크기와 연결해 읽기

`a & b`의 a와 b가 각각 4비트이면 bit0의 a·b를 AND하는 게이트, bit1의 게이트, bit2의 게이트, bit3의 게이트가 나란히 필요합니다. 서로 다른 자리끼리는 섞이지 않습니다. 따라서 출력도 네 비트입니다. 마스크의 bit k가 0이면 출력 bit k를 지우고, 1이면 a의 해당 비트를 통과시킵니다.

`&a`는 질문 자체가 다릅니다. ‘a의 모든 비트가 1인가?’를 한 비트로 답합니다. a[3] AND a[2] AND a[1] AND a[0]으로 펼쳐 보면 결과 폭이 1인 이유가 드러납니다. `|a`는 한 비트라도 켜졌는지, `^a`는 켜진 비트의 수가 홀수인지 묻습니다. `a && b`는 각 벡터가 0이 아닌지를 먼저 해석하므로 대응 자리의 AND와 다릅니다.

식을 쓸 때 먼저 결과가 ‘값의 버스’인지 ‘예/아니오 신호’인지 결정하세요. 같은 선언 폭의 출력에 넣더라도 이미 1비트로 계산된 결과를 할당하면 잃어버린 비트별 정보를 복구할 수 없습니다.

## 따라 풀기

a=1010₂, b=1100₂입니다. 위에서부터 각 열을 AND하면 1·1=1, 0·1=0, 1·0=0, 0·0=0이므로 masked=1000₂입니다. inverted=0101₂입니다. a에는 1이 두 개이므로 odd=0, 한 개 이상 있으므로 any_set=1, 모든 비트가 1은 아니므로 all_set=0입니다. a와 b는 둘 다 0이 아니므로 a&&b는 1입니다. 1000₂와 1은 결과 폭부터 다릅니다.

### 조건을 바꾸어 한 번 더 풀기

a=0011₂,b=1100₂를 사용해 세 AND를 분리합니다.

| 식 | 계산 과정 | 결과 폭·값 |
| --- | --- | --- |
| a & b | 0·1, 0·1, 1·0, 1·0 | 4비트 0000 |
| &a | 0·0·1·1 | 1비트 0 |
| a && b | a≠0이고 b≠0 | 1비트 1 |

이제 a만 0000으로 바꾸면 첫 두 결과는 여전히 0이지만 논리 AND도 0이 됩니다. 서로 다른 결과가 드러나는 입력을 선택해야 연산자 혼동을 잡을 수 있습니다.

## 헷갈리기 쉬운 점

벡터 선언의 [3:0]은 네 비트이지 세 비트가 아닙니다. ^는 거듭제곱이 아니라 XOR입니다. 축약 XOR를 반복 적용하면 1의 홀짝을 구하지만 1의 개수 자체를 세지는 않습니다. `~a`는 각 비트를 뒤집고 `!a`는 벡터 전체가 0인지 판단한 1비트 결과이므로 출력 폭부터 구별합니다.

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

### 적용 문제: 직접 구성하고 이유 설명하기

4비트 상태 a에서 any_error는 한 비트라도 1일 때, all_ready는 모두 1일 때, clean은 모두 0일 때 1이어야 합니다. 세 식을 적고 a=0000,0100,1111에서 기대값을 구하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>any_error=|a, all_ready=&amp;a, clean=~|a입니다. 모두 1비트 출력입니다.</p>
<p>입력이 0000이면 (0,0,1), 0100이면 (1,0,0), 1111이면 (1,1,0)입니다. clean은 any_error의 부정이므로 세 행 모두 두 값이 서로 반대인지 검산할 수 있습니다.</p>
</details>

## 다음으로 이어가기

다음에는 조건 연산자로 버스 하나를 고르고 중간 신호로 회로를 나눕니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.2.1–4.2.3, 인쇄 pp. 175–178 / PDF pp. 196–199. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
