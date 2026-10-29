## 이번 레슨의 목표

N비트 CPA의 폭과 캐리 연결을 설명하고 리플 구조의 지연 모델을 계산합니다.

## 앞에서 배운 내용

전가산기는 한 자리 덧셈을 완성했습니다. 같은 블록을 반복하면 여러 비트를 더할 수 있습니다.

## 아래 자리의 캐리를 위 자리 입력으로 연결한다

캐리 전파 덧셈기(carry propagate adder, CPA)는 N비트 A·B와 1비트 C_in을 받아 N비트 S와 1비트 C_out을 만듭니다. 리플 캐리(ripple-carry) 구현은 N개의 전가산기를 직렬로 연결합니다. 비트 0이 가장 낮은 자리입니다.

이 트랙은 c[0]=C_in, 비트 i의 출력 캐리=c[i+1]로 표기합니다. 따라서 비트 i는 A[i],B[i],c[i]를 읽습니다. 책의 C_i가 ‘비트 i의 출력’인 표기와 한 칸 다르므로 아래 식의 인덱스를 기준으로 읽습니다.

```systemverilog
module ch5_ripple4(input logic [3:0] a, b, input logic cin,
                   output logic [3:0] sum, output logic cout);
  logic [4:0] c;
  assign c[0] = cin;
  for (genvar i=0; i<4; i=i+1) begin : g_bit
    ch5_fulladd u(.a(a[i]), .b(b[i]), .cin(c[i]),
                  .sum(sum[i]), .cout(c[i+1]));
  end
  assign cout = c[4];
endmodule
```

레슨 1의 ch5_fulladd 정의도 컴파일에 포함합니다.

최상위 합은 낮은 자리의 캐리를 기다릴 수 있습니다. 각 전가산기의 대표 지연을 t_FA로 단순화하면 t_ripple≈N·t_FA입니다. 실제 셀의 합 경로와 캐리 경로 지연, 입력 도착 시각은 다를 수 있으므로 이는 구조 비교용 모델입니다. generate가 클록을 생성하지 않으므로 캐리 네 개가 네 주기에 이동하는 뜻은 아닙니다.

행동 기술에서는 충분히 넓힌 덧셈으로 `assign {cout,sum}={1'b0,a}+{1'b0,b}+{4'b0000,cin};`처럼 쓸 수 있습니다. 합성기는 목표에 따라 리플 외의 구조를 선택할 수 있습니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-2-t c5-2-d">
<title id="c5-2-t">리플 캐리 덧셈기: 자리올림의 긴 경로</title>
<desc id="c5-2-d">4비트 리플의 캐리 경로를 낮은 자리부터 묶어 그린 기능 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">비트 0</text><text x="75" y="87">c[0] → c[1]</text><text x="223" y="59">비트 1·2</text><text x="223" y="87">중간 캐리 전달</text><text x="371" y="59">비트 3</text><text x="371" y="87">sum[3]·c[4]</text></g>
</svg>
<p class="diagram-caption">그림 5-2a. 4비트 리플의 캐리 경로를 낮은 자리부터 묶어 그린 기능 개념도입니다.</p>

<svg viewBox="0 0 470 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-2b-t c5-2b-d">
<title id="c5-2b-t">4비트 리플의 전가산기 연결</title>
<desc id="c5-2b-d">왼쪽부터 비트 0,1,2,3 전가산기가 연결됩니다. 각 전가산기는 위에서 해당 자리의 A와 B를 받고 아래로 합을 냅니다. 캐리는 c0에서 c4까지 오른쪽으로 진행합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"><rect x="45" y="60" width="70" height="65"/><rect x="145" y="60" width="70" height="65"/><rect x="245" y="60" width="70" height="65"/><rect x="345" y="60" width="70" height="65"/></g>
<g stroke="var(--ink)" stroke-width="2" fill="none"><path d="M15 92 H45 M115 92 H145 M215 92 H245 M315 92 H345 M415 92 H455 M72 35 V60 M88 35 V60 M172 35 V60 M188 35 V60 M272 35 V60 M288 35 V60 M372 35 V60 M388 35 V60 M80 125 V155 M180 125 V155 M280 125 V155 M380 125 V155 M135 86 L145 92 L135 98 M235 86 L245 92 L235 98 M335 86 L345 92 L335 98"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="80" y="24">A0·B0</text><text x="180" y="24">A1·B1</text><text x="280" y="24">A2·B2</text><text x="380" y="24">A3·B3</text><text x="80" y="99">FA0</text><text x="180" y="99">FA1</text><text x="280" y="99">FA2</text><text x="380" y="99">FA3</text><text x="18" y="78">c0</text><text x="130" y="78">c1</text><text x="230" y="78">c2</text><text x="330" y="78">c3</text><text x="442" y="78">c4</text><text x="80" y="177">S0</text><text x="180" y="177">S1</text><text x="280" y="177">S2</text><text x="380" y="177">S3</text></g>
</svg>
<p class="diagram-caption">그림 5-2b. 코드의 비트 번호대로 낮은 자리를 왼쪽에 배치한 기능 회로입니다. 일반 숫자 표기의 MSB 왼쪽 순서와 반대이며 캐리 방향을 보기 위한 배치입니다.</p>

## 네 자릿값을 한 줄씩 계산하며 캐리 연결 검증하기

일반 종이 덧셈처럼 최하위 자리부터 시작합니다. 비트 i에 들어가는 값은 A_i+B_i+c[i]이고, 0·1·2·3 중 하나입니다. 이 값의 하위 비트가 S_i, 2 이상인지가 다음 c[i+1]입니다. c[0]를 외부 입력 캐리로 정했으므로 비트 i의 ‘입력’과 ‘출력’을 한 칸씩 정확히 연결해야 합니다.

가장 높은 자리의 합을 결정하려면 그 아래에서 오는 캐리도 알아야 합니다. A XOR B가 1인 자리들이 길게 이어지면 낮은 자리의 캐리 변화가 높은 자리까지 영향을 줍니다. 이 의존 경로가 리플 지연의 원인입니다. 전가산기 N개를 나란히 그렸다고 서로 독립적으로 정답을 낼 수 있는 것은 아닙니다.

지연 모델 N·t_FA는 구조를 비교하기 위한 근사입니다. 실제 합·캐리의 핀 간 지연을 모두 같은 값으로 묶었고, 배선과 부하도 단순화했습니다. 모델에 수치를 대입한 답과 실제 구현의 타이밍 보고서는 구분합니다.

## 따라 풀기

A=0111₂,B=0001₂,C_in=0입니다. 비트 0은 1+1+0=2라 S0=0,c1=1입니다. 비트 1은 1+0+1=2, 비트 2도 1+0+1=2라 캐리가 계속 1입니다. 비트 3은 0+0+1=1이므로 S=1000₂,C_out=0입니다. 부호 없는 7+1=8로 검산합니다. 교육용 t_FA=180ps에서 12비트 리플은 12×180=2160ps=2.16ns입니다.

### 조건을 바꾸어 한 번 더 풀기

A=1010₂,B=0111₂,c0=0인 계산을 펼칩니다.

| i | A_i | B_i | c[i] | 자리 합 | S_i | c[i+1] |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 1 | 0 | 1 | 1 | 0 |
| 1 | 1 | 1 | 0 | 2 | 0 | 1 |
| 2 | 0 | 1 | 1 | 2 | 0 | 1 |
| 3 | 1 | 0 | 1 | 2 | 0 | 1 |

합 비트는 표를 거꾸로 읽어 S3S2S1S0=0001이고 최종 c4=1입니다. 전체 10001₂=17은 unsigned 10+7과 같습니다. S만 1로 읽으면 상위 캐리를 버린 modulo 16 결과입니다.

## 헷갈리기 쉬운 점

합 결과 폭과 최상위 캐리를 구별합니다. 부호 없는 N비트 합을 모두 보존하려면 N+1비트가 필요합니다. 최대 캐리 경로는 입력 패턴에 따라 활성화되며 모든 입력에서 항상 최대 지연이 관측되는 것은 아닙니다.

## 직접 확인하기

1. 4비트 1111+0001의 S와 C_out은?
2. 16비트에서 t_FA=150ps인 단순 지연은?
3. generate 네 반복이 네 주기 지연인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0000과 1입니다. 전체 결과는 10000입니다.</p>
<p>2. 2400ps=2.4ns입니다.</p>
<p>3. 아닙니다. 네 전가산기의 조합 연결입니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

c0=1,A=0011,B=0100을 네 자리 표로 계산하세요. 최종 캐리가 0인데도 signed overflow가 발생하는지 판단하고, 어떤 두 가지 검산을 해야 하는지 적으세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>bit0은 1+0+1=2로 S0=0,c1=1; bit1도 2로 S1=0,c2=1; bit2는 0+1+1=2로 S2=0,c3=1; bit3은 1로 S3=1,c4=0입니다. 결과는 1000입니다.</p>
<p>unsigned는 3+4+1=8로 정상입니다. signed 4비트에서는 +8이 범위 밖이므로 overflow입니다. 전체 unsigned 합과 signed 허용 범위를 따로 검산해야 합니다.</p>
</details>

## 다음으로 이어가기

다음에는 한 자리씩 기다리는 대신 블록의 캐리를 미리 계산합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.1, 인쇄 pp. 238–244 / PDF pp. 259–265. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
