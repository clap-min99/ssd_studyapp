## 이번 레슨의 목표

크기가 명시된 상수를 읽고 슬라이스·연결·반복으로 만든 결과의 폭과 값을 계산합니다.

## 앞에서 배운 내용

1장에서 비트 패턴과 숫자의 해석을 구별했습니다. HDL에서는 그 패턴을 저장할 폭도 코드에 드러내야 합니다.

## 먼저 몇 비트인지 더한다

`6'b001101`은 6비트 이진 상수이고 `6'd13`, `6'h0D`도 같은 패턴입니다. 작은따옴표 앞은 폭, 뒤의 b·o·d·h는 2·8·10·16진법입니다. 밑줄은 읽기 편하게 넣으며 값에 영향을 주지 않습니다. `'0`, `'1`은 할당 문맥의 모든 비트를 각각 0 또는 1로 채우는 표현입니다.

```systemverilog
module pack_bits(input logic [3:0] nibble,
                 input logic flag,
                 output logic [7:0] packed_value);
  assign packed_value = {nibble[2:0], {2{flag}}, 3'b010};
endmodule
```

`nibble[2:0]`은 연속한 3비트 슬라이스이고 nibble[3]은 제외합니다. 바깥 `{...}`는 왼쪽 항부터 상위 비트에 배치하는 연결(concatenation)입니다. `{2{flag}}`는 flag를 두 번 복제하는 반복(replication)입니다. 전체 폭은 3+2+3=8비트입니다.

부호 없는 4비트 값을 8비트로 만들려면 `{4'b0000, a}`처럼 0 확장을, 2의 보수 4비트 값을 비트 패턴 기준으로 확장하려면 `{{4{a[3]}}, a}`처럼 최상위 비트를 복제합니다. 후자의 연결 결과 자체는 signed 선언을 자동으로 얻지 않으므로 이후 산술 해석도 명시해야 합니다. signed 연산은 선택 심화에서 다시 다룹니다.

크기를 생략한 정수는 문맥과 언어의 폭·부호 규칙이 관여합니다. 특히 연결 내부에는 크기를 명시한 상수를 사용합니다. 넓은 결과를 좁은 출력에 넣으면 상위 비트가 잘릴 수 있으므로 컴파일 경고를 확인합니다.

<svg viewBox="0 0 450 185" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-4-study-t c4-4-study-d">
<title id="c4-4-study-t">비트 연결식의 목적지 위치</title>
<desc id="c4-4-study-d">nibble[2:0]은 출력 [7:5], flag 두 개는 [4:3], 상수 010은 [2:0]에 배치됩니다. 왼쪽이 최상위입니다.</desc>
<text x="225" y="25" font-size="16" text-anchor="middle" fill="var(--ink)">packed_value[7:0]의 목적지 번호</text><rect x="22" y="75" width="48" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="46.0" y="104.0" font-size="15" text-anchor="middle" fill="var(--ink)">n[2]</text><text x="46" y="60" font-size="12" text-anchor="middle" fill="var(--ink)">bit7</text><rect x="73" y="75" width="48" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="97.0" y="104.0" font-size="15" text-anchor="middle" fill="var(--ink)">n[1]</text><text x="97" y="60" font-size="12" text-anchor="middle" fill="var(--ink)">bit6</text><rect x="124" y="75" width="48" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="148.0" y="104.0" font-size="15" text-anchor="middle" fill="var(--ink)">n[0]</text><text x="148" y="60" font-size="12" text-anchor="middle" fill="var(--ink)">bit5</text><rect x="175" y="75" width="48" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="199.0" y="104.0" font-size="15" text-anchor="middle" fill="var(--ink)">flag</text><text x="199" y="60" font-size="12" text-anchor="middle" fill="var(--ink)">bit4</text><rect x="226" y="75" width="48" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="250.0" y="104.0" font-size="15" text-anchor="middle" fill="var(--ink)">flag</text><text x="250" y="60" font-size="12" text-anchor="middle" fill="var(--ink)">bit3</text><rect x="277" y="75" width="48" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="301.0" y="104.0" font-size="15" text-anchor="middle" fill="var(--ink)">0</text><text x="301" y="60" font-size="12" text-anchor="middle" fill="var(--ink)">bit2</text><rect x="328" y="75" width="48" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="352.0" y="104.0" font-size="15" text-anchor="middle" fill="var(--ink)">1</text><text x="352" y="60" font-size="12" text-anchor="middle" fill="var(--ink)">bit1</text><rect x="379" y="75" width="48" height="48" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="403.0" y="104.0" font-size="15" text-anchor="middle" fill="var(--ink)">0</text><text x="403" y="60" font-size="12" text-anchor="middle" fill="var(--ink)">bit0</text><text x="225" y="155" font-size="14" text-anchor="middle" fill="var(--ink)">n = nibble · 폭 = 3 + 2 + 3 = 8비트</text>
</svg>
<p class="diagram-caption">그림 4-4. nibble[2:0]은 출력 [7:5], flag 두 개는 [4:3], 상수 010은 [2:0]에 배치됩니다. 왼쪽이 최상위입니다.</p>

## 연결한 비트의 목적지 번호를 먼저 붙이기

연결식은 오른쪽의 조각들을 왼쪽부터 상위 비트에 배치합니다. 따라서 `{nibble[2:0],{2{flag}},3'b010}`을 읽을 때 먼저 총 8비트를 확인하고 출력 위치에 번호를 붙입니다. nibble[2]·[1]·[0]은 결과 [7]·[6]·[5], flag 두 개는 [4]·[3], 상수는 [2:0]입니다. 입력 nibble[3]은 사용하지 않습니다.

0 확장은 값의 상위에 0을 붙여 unsigned 수를 보존합니다. 부호 확장은 원래 최상위 비트를 복제해 2의 보수 값을 보존합니다. 예를 들어 4비트 1011은 unsigned 11이지만 signed −5입니다. 각각 00001011과 11111011로 확장해야 자기 해석의 수가 유지됩니다. 같은 비트 조립 연산도 어떤 값을 보존하려는지에 따라 다릅니다.

출력 폭이 부족하면 상위 조각이 잘릴 수 있습니다. 이때 합성이나 시뮬레이션이 실행됐다는 사실만으로 인터페이스가 맞다고 판단하지 않습니다. 연결 전에 각 조각의 폭을 적고 연결 후 목적지 위치를 역으로 읽어 확인합니다.

## 따라 풀기

nibble=1101₂, flag=1이면 nibble[2:0]=101₂입니다. 반복 부분은 11₂, 끝은 010₂이므로 결과는 101_11_010₂=10111010₂=0xBA입니다. 합이 아니라 비트 연결이므로 5+3+2처럼 십진수를 더하지 않습니다. 검산은 상위 세 비트 101, 중간 두 비트 11, 하위 세 비트 010을 다시 분리하면 됩니다.

### 조건을 바꾸어 한 번 더 풀기

nibble=0110,flag=0으로 바꿉니다. 낮은 세 비트는 110, 반복은 00, 상수는 010입니다. 따라서 결과는 110_00_010=11000010₂=0xC2입니다.

같은 식을 실수로 6비트 출력에 넣으면 하위 6비트 000010만 남고 nibble의 위 두 선택 비트를 잃습니다. 8비트 출력의 상위가 우연히 00인 입력만 검사하면 이 오류를 발견하기 어렵습니다. 여기처럼 위쪽이 11인 입력을 포함해야 폭 잘림을 드러낼 수 있습니다.

## 헷갈리기 쉬운 점

8비트에 4비트 값을 넣는 것과 상위 비트를 반복하는 것은 다른 동작입니다. {a,b}는 a+b가 아닙니다. packed는 SystemVerilog 예약어이므로 신호 이름으로 사용하지 않고 packed_value처럼 뜻이 분명한 이름을 씁니다.

## 직접 확인하기

1. 8'h36의 이진 패턴은 무엇인가요?
2. a=1011을 8비트로 0 확장한 결과와 부호 확장한 패턴은 무엇인가요?
3. {2{3'b101}}의 폭과 값은 무엇인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 00110110입니다. 16진 한 자리는 4비트입니다.</p>
<p>2. 00001011과 11111011입니다. 전자는 부호 없는 11, 후자를 2의 보수로 읽으면 −5입니다.</p>
<p>3. 6비트 101101입니다. 3비트 패턴을 두 번 복제합니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

8비트 y를 `{a[1:0],b[3:0],2'b01}`로 만듭니다. a=1101,b=1010에서 y를 구하고, y[7:6],y[5:2],y[1:0]이 각각 어디서 왔는지 적으세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>a[1:0]=01, b=1010, 마지막 두 비트=01이므로 y=01_1010_01=01101001=0x69입니다.</p>
<p>폭은 2+4+2=8입니다. y[7:6]=a[1:0], y[5:2]=b[3:0], y[1:0]=01로 다시 나누면 원래 세 조각을 얻습니다. a[3:2]는 결과에 들어가지 않습니다.</p>
</details>

## 다음으로 이어가기

다음에는 0·1 이외의 X·Z와 시뮬레이션 지연을 구별합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.2.7, 4.2.9, 인쇄 pp. 183–186 / PDF pp. 204–207. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
