## 이번 레슨의 목표

always_latch의 투명 구간을 추적하고 불완전한 조합 할당이 저장 동작을 요구하는 이유를 설명합니다.

## 앞에서 배운 내용

3장의 D 래치는 gate가 1인 동안 투명했습니다. 레지스터의 상승 에지 샘플과 비교합니다.

## 새 값이 없으면 이전 값을 유지한다

```systemverilog
module hold2(input logic gate,
             input logic [1:0] d,
             output logic [1:0] q);
  always_latch
    if (gate) q <= d;
endmodule
```

gate=1인 동안 d가 바뀌면 q도 따라가고, gate=0이면 q는 이전 값을 유지합니다. `always_latch`는 의도적으로 래치를 기술한다는 표시입니다. gate의 상승 때 한 번만 복사하는 플립플롭이 아닙니다. gate와 d의 변화에 따라 본문이 평가됩니다.

이제 조합논리를 만들려다 `always_comb if (en) y = a;`라고 썼다고 합시다. en=0일 때 y가 무엇인지 지정하지 않았습니다. 이전 y를 유지하는 의미가 되어 래치가 필요하거나 도구가 오류/경고를 냅니다. `always_comb`라는 이름만 붙인다고 할당 누락이 고쳐지지는 않습니다.

저장을 원하지 않으면 모든 경로에 값을 줍니다. 예를 들어 `always_comb if (en) y=a; else y='0;`은 en=0일 때 0을 고르는 조합 회로입니다. `else y=y;`는 이전 출력 의존성을 남기므로 올바른 누락 수정이 아닙니다. 조합·래치·플립플롭은 선언 자료형이 아니라 사건과 할당의 의미로 판단합니다.

<svg viewBox="0 0 450 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-10-study-t c4-10-study-d">
<title id="c4-10-study-t">투명 구간과 유지 구간의 한 비트 시간도</title>
<desc id="c4-10-study-d">hold2의 bit0를 나타낸 이상적 시간도입니다. 시작 전에 q[0]=0으로 저장되었다고 가정합니다. gate=1인 5ns부터 15ns 사이에는 d 변화를 따라가고,15ns 이후 gate=0에서는 d가 바뀌어도 0을 유지합니다.</desc>
<path d="M110 20 V215" fill="none" stroke="var(--border)" stroke-dasharray="4 4"/><path d="M185 20 V215" fill="none" stroke="var(--border)" stroke-dasharray="4 4"/><path d="M260 20 V215" fill="none" stroke="var(--border)" stroke-dasharray="4 4"/><path d="M335 20 V215" fill="none" stroke="var(--border)" stroke-dasharray="4 4"/><path d="M410 20 V215" fill="none" stroke="var(--border)" stroke-dasharray="4 4"/><text x="15" y="45" font-size="15" text-anchor="start" fill="var(--ink)">gate</text><path d="M110.0 60 L147.5 60 L147.5 60 L185.0 60 L185.0 35 L222.5 35 L222.5 35 L260.0 35 L260.0 35 L297.5 35 L297.5 35 L335.0 35 L335.0 60 L372.5 60 L372.5 60 L410.0 60" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="15" y="110" font-size="15" text-anchor="start" fill="var(--ink)">d[0]</text><path d="M110.0 125 L147.5 125 L147.5 100 L185.0 100 L185.0 100 L222.5 100 L222.5 125 L260.0 125 L260.0 100 L297.5 100 L297.5 125 L335.0 125 L335.0 125 L372.5 125 L372.5 100 L410.0 100" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="15" y="175" font-size="15" text-anchor="start" fill="var(--ink)">q[0]</text><path d="M110.0 190 L147.5 190 L147.5 190 L185.0 190 L185.0 165 L222.5 165 L222.5 190 L260.0 190 L260.0 165 L297.5 165 L297.5 190 L335.0 190 L335.0 190 L372.5 190 L372.5 190 L410.0 190" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="110" y="243" font-size="14" text-anchor="middle" fill="var(--ink)">0</text><text x="185" y="243" font-size="14" text-anchor="middle" fill="var(--ink)">5</text><text x="260" y="243" font-size="14" text-anchor="middle" fill="var(--ink)">10</text><text x="335" y="243" font-size="14" text-anchor="middle" fill="var(--ink)">15</text><text x="410" y="243" font-size="14" text-anchor="middle" fill="var(--ink)">20ns</text>
</svg>
<p class="diagram-caption">그림 4-10. hold2의 bit0를 나타낸 이상적 시간도입니다. 시작 전에 q[0]=0으로 저장되었다고 가정합니다. gate=1인 5ns부터 15ns 사이에는 d 변화를 따라가고,15ns 이후 gate=0에서는 d가 바뀌어도 0을 유지합니다.</p>

## 할당하지 않은 조건이 왜 저장을 요구하는가

조합논리라면 입력 하나의 조합에 출력 하나가 대응해야 합니다. 그런데 `if(en) y=a;`만 있으면 en=0일 때 y를 결정할 현재 입력 함수가 없습니다. 시뮬레이션의 절차 변수는 새 할당이 없으면 기존 값을 남깁니다. 그러므로 같은 en=0,a=00에서도 과거에 무엇을 넣었는지에 따라 y가 달라질 수 있습니다. 이것이 저장 동작입니다.

래치는 이 동작을 의도적으로 사용합니다. gate=1일 때는 현재 d를 계속 전달하고 gate=0일 때 이전 값을 남깁니다. 반면 MUX는 en=0에서도 다른 입력, 예를 들어 0을 즉시 고르므로 과거를 필요로 하지 않습니다. 두 회로의 차이는 else라는 글자의 유무 자체보다 닫힌 구간에 ‘기억’이 필요한지입니다.

의도한 조합 회로에서 누락을 고치려면 출력의 기본값을 정하고 모든 경로를 검사합니다. `y=y`는 기억 의존성을 그대로 남기므로 해결이 아닙니다. 여러 출력 중 하나만 빠져도 그 출력에 저장이 생길 수 있어 출력별로 경로를 따로 확인해야 합니다.

## 따라 풀기

처음 gate=1,d=01이면 평가 후 q=01입니다. gate가 계속 1일 때 d=10으로 바뀌면 q=10입니다. gate=0으로 내린 뒤 d=11로 바꿔도 q=10입니다. 다시 gate=1이면 q=11로 따라갑니다. 두 번째 d 변화가 상승 에지 없이 통과했다는 점이 플립플롭과의 차이입니다.

### 조건을 바꾸어 한 번 더 풀기

gate=1,d=10에서 시작해 q=10이 되었다고 합시다. 다음 d와 gate 변화를 추적합니다.

| 사건 | gate | d | 래치 q | en?d:00인 MUX 출력 |
| --- | --- | --- | --- | --- |
| 열린 상태 | 1 | 10 | 10 | 10 |
| gate 닫기 | 0 | 10 | 10 | 00 |
| 닫힌 중 입력 변경 | 0 | 01 | 10 | 00 |
| 다시 열기 | 1 | 01 | 01 | 01 |

MUX의 en은 표의 gate와 같은 제어값입니다. 세 번째 행에서 같은 현재 입력에도 래치는 직전 저장 이력을 보여줍니다. 플립플롭이었다면 gate 대신 별도 클록 상승 에지에서만 복사한다는 또 다른 계약이 필요합니다.

## 헷갈리기 쉬운 점

플립플롭에서 enable=0일 때 할당을 생략하는 것은 의도한 유지입니다. 조합 블록에서 같은 생략을 하면 저장이 섞입니다. 처음부터 gate=0이었다면 아직 저장한 값이 없어 q가 X일 수 있습니다. 의도하지 않은 래치 경고는 무시하지 말고 입력별 할당 경로를 확인합니다.

## 직접 확인하기

1. gate=1인 동안 d가 두 번 바뀌면 q는 몇 번 따라갈 수 있나요?
2. always_comb에서 else를 빠뜨려도 자동으로 0이 되나요?
3. logic q 선언만 보고 래치인지 플립플롭인지 알 수 있나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 두 번 모두 따라갈 수 있습니다. 입력은 모델이 반영할 만큼 유지된다고 가정합니다.</p>
<p>2. 아닙니다. 미할당 경로는 이전 값 유지 의미를 만들 수 있습니다.</p>
<p>3. 알 수 없습니다. always_latch·always_ff의 사건 조건과 실제 할당을 봐야 합니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

조합 블록에서 y는 기본 00, valid는 기본 0이고 en=1일 때 y=a,valid=1이어야 합니다. 기본 할당 두 개와 조건부 덮어쓰기를 문장 순서로 적으세요. valid의 기본값만 빠지면 어떤 입력열에서 오류가 보일까요?

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>always_comb의 begin/end 안에서 먼저 y=2'b00; valid=1'b0;를 쓰고, if(en) begin y=a; valid=1'b1; end로 덮어씁니다. 두 출력 모두 모든 입력에서 값이 정해집니다.</p>
<p>valid 기본값이 없으면 en=1로 valid를 1로 만든 뒤 en=0으로 바꿀 때 valid가 1을 유지할 수 있습니다. 처음 en=0만 보는 검사보다 1→0 전환이 누락을 드러냅니다.</p>
</details>

## 다음으로 이어가기

다음에는 always_comb의 모든 경로를 채우며 case와 if를 사용합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.4.5–4.5, 인쇄 pp. 196–198 / PDF pp. 217–219. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
