## 이번 레슨의 목표

U a.b와 Q a.b의 범위·해상도를 구하고 같은 배율의 덧셈과 곱셈 후 배율을 설명합니다.

## 앞에서 배운 내용

1장의 2의 보수는 정수 표현이었습니다. 같은 패턴을 일정한 2의 거듭제곱으로 나누어 해석하면 분수를 표현할 수 있습니다.

## 소수점은 비트에 저장되지 않는다

고정소수점(fixed-point)은 이진 소수점의 위치를 미리 약속합니다. 이 책의 U a.b는 정수 a비트·소수 b비트의 unsigned, Q a.b는 부호를 포함한 정수 a비트·소수 b비트의 2의 보수입니다. 두 형식의 폭은 a+b이고 값은 저장 정수/2ᵇ입니다. 다른 문헌은 Q의 정수 비트에 부호를 포함하는 규칙이 다를 수 있어 폭을 함께 명시합니다.

해상도는 2⁻ᵇ입니다. U a.b의 범위는 0부터 2ᵃ−2⁻ᵇ, Q a.b는 −2ᵃ⁻¹부터 2ᵃ⁻¹−2⁻ᵇ입니다. Q3.3은 총 6비트, 해상도 1/8, 범위 −4부터 3.875입니다. 부호-크기 표현도 가능하지만 이 트랙의 산술은 2의 보수를 사용합니다.

같은 b를 쓰는 두 값을 더하면 일반 정수 덧셈기를 그대로 사용할 수 있습니다. 배율이 다르면 먼저 정렬합니다. 곱셈에서는 소수 비트 수가 더해집니다. Q3.3끼리 곱한 전체 12비트 결과는 소수 6비트이며 원래 형식으로 줄일 때 시프트·반올림·범위 초과 정책이 필요합니다. 하위 비트를 자르는 것과 포화시키는 것은 다른 선택입니다.

고정소수점은 소수점 저장 장치가 따로 없으므로 같은 비트를 다르게 해석해도 하드웨어가 알려주지 않습니다. 모듈 입출력 명세에 폭·signed·배율을 함께 적어야 합니다.

<svg viewBox="0 0 450 230" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-12-study-t c5-12-study-d">
<title id="c5-12-study-t">Q3.3의 비트별 가중치</title>
<desc id="c5-12-study-d">Q3.3은 부호 포함 정수 세 비트와 소수 세 비트입니다. 왼쪽부터 가중치를 붙여 패턴 101010을 해석합니다. 세 번째와 네 번째 사이 세로선은 암묵적 소수점 위치입니다.</desc>
<text x="225" y="25" font-size="15" text-anchor="middle" fill="var(--ink)">Q3.3 · 총 6비트 · 실제 값 = 저장 정수 / 8</text><text x="51" y="65" font-size="14" text-anchor="middle" fill="var(--ink)">−4</text><rect x="20" y="80" width="62" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="51.0" y="109.0" font-size="15" text-anchor="middle" fill="var(--ink)">1</text><text x="119" y="65" font-size="14" text-anchor="middle" fill="var(--ink)">2</text><rect x="88" y="80" width="62" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="119.0" y="109.0" font-size="15" text-anchor="middle" fill="var(--ink)">0</text><text x="187" y="65" font-size="14" text-anchor="middle" fill="var(--ink)">1</text><rect x="156" y="80" width="62" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="187.0" y="109.0" font-size="15" text-anchor="middle" fill="var(--ink)">1</text><text x="255" y="65" font-size="14" text-anchor="middle" fill="var(--ink)">1/2</text><rect x="224" y="80" width="62" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="255.0" y="109.0" font-size="15" text-anchor="middle" fill="var(--ink)">0</text><text x="323" y="65" font-size="14" text-anchor="middle" fill="var(--ink)">1/4</text><rect x="292" y="80" width="62" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="323.0" y="109.0" font-size="15" text-anchor="middle" fill="var(--ink)">1</text><text x="391" y="65" font-size="14" text-anchor="middle" fill="var(--ink)">1/8</text><rect x="360" y="80" width="62" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="391.0" y="109.0" font-size="15" text-anchor="middle" fill="var(--ink)">0</text><path d="M220 72 V142" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="225" y="175" font-size="16" text-anchor="middle" fill="var(--ink)">−4 + 1 + 1/4 = −2.75</text><text x="225" y="205" font-size="13" text-anchor="middle" fill="var(--ink)">101010을 2의 보수 정수로 읽으면 −22 · −22/8 = −2.75</text>
</svg>
<p class="diagram-caption">그림 5-12. Q3.3은 부호 포함 정수 세 비트와 소수 세 비트입니다. 왼쪽부터 가중치를 붙여 패턴 101010을 해석합니다. 세 번째와 네 번째 사이 세로선은 암묵적 소수점 위치입니다.</p>

## 비트의 자릿값과 배율을 같은 표에 적기

Q3.3의 6비트 가중치는 왼쪽부터 −4,2,1,1/2,1/4,1/8입니다. 부호 비트를 제외한 양수 자릿값은 일반 이진 분수와 같고 최상위만 음의 가중치를 가집니다. 101010은 −4+1+1/4=−2.75입니다. 동일 패턴을 먼저 signed 정수 −22로 읽고 8로 나누어도 −2.75이므로 두 방식이 서로 검산이 됩니다.

덧셈은 두 저장 정수의 배율이 같아야 합니다. 소수 3비트인 저장값 8과 소수 4비트인 저장값 8은 각각 1과 0.5이므로 그대로 더한 16의 해석은 정해지지 않습니다. 예를 들어 소수 4비트로 맞추려면 첫 값을 16으로 확장한 뒤 8을 더해 24,즉 1.5로 읽어야 합니다.

양자화는 표현 격자에 없는 값을 어느 이웃으로 보낼지 고르는 과정입니다. 소수 3비트의 간격은 0.125입니다. 0.2는 0.125와 0.25 사이이며 가장 가까운 값은 0.25,양수의 하위 비트 절삭은 0.125입니다. 격자·반올림·범위 처리를 구별해 적습니다.

## 따라 풀기

Q3.3에서 1.25는 1.25×8=10으로 001010, −0.375는 −3을 저장하므로 111101입니다. 합은 001010+111101=1_000111이고 하위 6비트 000111을 8로 나누면 0.875입니다. 1.25−0.375=0.875로 검산합니다. 1.25×0.5는 저장 정수 10×4=40, 소수 6비트 결과이므로 40/64=0.625입니다. Q3.3으로 줄이면 저장 정수 5가 되어 정확히 표현됩니다.

### 조건을 바꾸어 한 번 더 풀기

Q3.3의 1.375와 0.625를 곱합니다. 저장 정수는 각각 11과 5입니다. 전체 곱은 55이며 소수 비트가 6개이므로 실제 값 55/64=0.859375입니다.

다시 소수 3비트로 줄이려면 저장 정수 55를 8로 나눈 6.875를 정수화합니다. 양수 절삭이면 6을 저장해 0.75,가장 가까운 값이면 7을 저장해 0.875입니다. 전체 곱이 잘 계산되어도 재양자화에서 오차가 생깁니다. 단순히 소수점 위치만 다시 붙이는 작업이 아닙니다.

## 헷갈리기 쉬운 점

모든 십진 소수가 정확히 표현되지는 않습니다. 예를 들어 소수 3비트에서 0.1은 격자 0,0.125,0.25 등에 없으므로 양자화가 필요합니다. 덧셈 결과의 캐리를 버려도 signed overflow가 없다는 뜻은 아닙니다.

## 직접 확인하기

1. Q3.3의 최솟값 패턴은?
2. 소수 4비트의 해상도는?
3. 소수 3비트와 4비트 값을 곱하면 전체 결과의 소수 비트는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 100000으로 −32/8=−4입니다.</p>
<p>2. 1/16=0.0625입니다.</p>
<p>3. 7비트입니다. 2³×2⁴의 배율이 곱해집니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

Q3.3에서 001101과 111010의 실제 값을 각각 구하고 합을 계산하세요. 비트 덧셈과 십진 덧셈으로 두 번 검산하고 범위 초과 여부를 판단하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>001101은 저장 정수 13이므로 1.625입니다. 111010은 6비트 signed 정수 −6이므로 −0.75입니다. 합은 0.875입니다.</p>
<p>13+(−6)=7, 하위 6비트 000111을 8로 나누면 0.875입니다. 범위 −4부터 3.875 안이므로 overflow가 없습니다. 부호가 다른 두 값의 덧셈이라는 점도 확인합니다.</p>
</details>

## 다음으로 이어가기

다음 두 선택 심화는 지수로 배율을 바꾸는 부동소수점입니다. 핵심 과정은 레슨15 카운터로 이어가도 됩니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.3–5.3.1, 인쇄 pp. 256–257 / PDF pp. 277–278. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
