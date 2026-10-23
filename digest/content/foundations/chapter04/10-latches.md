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

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-10-t c4-10-d">
<title id="c4-10-t">래치와 할당 누락: 의도한 기억과 뜻밖의 기억</title>
<desc id="c4-10-d">의도한 래치의 두 동작과 조합 회로의 완전 할당 조건을 비교한 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">gate=1</text><text x="75" y="91">d가 q로 통과</text><text x="223" y="63">gate=0</text><text x="223" y="91">이전 q 유지</text><text x="371" y="63">조합 회로</text><text x="371" y="91">모든 조건 값 지정</text></g>
</svg>
<p class="diagram-caption">그림 4-10. 의도한 래치의 두 동작과 조합 회로의 완전 할당 조건을 비교한 개념도입니다.</p>

## 따라 풀기

처음 gate=1,d=01이면 평가 후 q=01입니다. gate가 계속 1일 때 d=10으로 바뀌면 q=10입니다. gate=0으로 내린 뒤 d=11로 바꿔도 q=10입니다. 다시 gate=1이면 q=11로 따라갑니다. 두 번째 d 변화가 상승 에지 없이 통과했다는 점이 플립플롭과의 차이입니다.

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

## 다음으로 이어가기

다음에는 always_comb의 모든 경로를 채우며 case와 if를 사용합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.4.5–4.5, 인쇄 pp. 196–198 / PDF pp. 217–219. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
