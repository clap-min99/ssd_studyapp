## 이번 레슨의 목표

2단 SOP와 다단 논리를 비교하고, 드모르간 법칙으로 NAND 회로의 기능을 추적할 수 있으면 됩니다.

## 앞에서 배운 내용

SOP는 입력 리터럴에서 AND 단계를 거쳐 OR 단계로 진행합니다. 보수 입력을 만드는 인버터를 별도로 세는 관례에서 이것을 2단 논리(two-level logic)라고 합니다. 실제 입력에서 출력까지의 지연에는 인버터도 포함됩니다.

## SOP에서 가장 짧아도 다른 구조가 더 작을 수 있다

세 입력 XOR의 SOP는 `¬A·¬B·C+¬A·B·¬C+A·¬B·¬C+A·B·C`입니다. 1이 홀수 개일 때만 켜지므로 네 최소항이 필요하고 SOP 안에서 더 크게 결합할 수 없습니다. 하지만 XOR 게이트를 사용할 수 있으면 `P=A⊕B`, `Y=P⊕C`로 두 개만 연결할 수 있습니다.

여덟 입력 XOR도 같은 원리입니다. 모든 SOP 최소항을 나열하면 128개지만, 두 입력 XOR 트리는 7개 요소로 만들 수 있습니다. 균형 트리는 입력에서 출력까지 3단계, 일렬 연결은 최장 7단계입니다. 이는 **XOR를 사용할 수 있다는 가정 아래의 요소 수·깊이 비교**이며 소자 수나 실제 지연이 그 숫자와 같다는 뜻은 아닙니다.

<svg viewBox="0 0 440 205" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c2-multi-title c2-multi-desc">
<title id="c2-multi-title">NAND 세 개로 곱의 합을 구현하기</title>
<desc id="c2-multi-desc">위 NAND의 출력 n0는 A와 B의 AND 결과를 반전한 값이고, 아래 NAND의 출력 n1은 C와 D의 AND 결과를 반전한 값입니다. 두 출력을 마지막 NAND에 넣으면 Y는 A AND B OR C AND D가 됩니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="35" y="25" width="155" height="55" rx="5"/><rect x="35" y="115" width="155" height="55" rx="5"/><rect x="285" y="70" width="100" height="55" rx="5"/></g><path d="M190 52 H230 V85 H285 M190 142 H245 V110 H285 M385 97 H415" fill="none" stroke="var(--ink)" stroke-width="2"/><g fill="var(--ink)" font-family="sans-serif" font-size="13" text-anchor="middle"><text x="112" y="57">n0 = ¬(A·B)</text><text x="112" y="147">n1 = ¬(C·D)</text><text x="335" y="102">¬(n0·n1)</text><text x="426" y="102">Y</text><text x="220" y="194">Y = A·B+C·D</text></g>
</svg>
<p class="diagram-caption">그림 2-5. 블록 안의 식으로 반전 범위를 표시한 NAND 기능도입니다.</p>

## 따라 풀기

그림의 출력을 중간식부터 계산합니다.

`Y=¬(n0·n1)=¬n0+¬n1=¬(¬(A·B))+¬(¬(C·D))=A·B+C·D`

여기서 마지막 NAND의 출력 반전을 입력 쪽으로 옮기면 OR 몸체와 두 입력 반전으로 바뀝니다. 앞 NAND의 출력 반전과 뒤 게이트의 입력 반전이 같은 연결에서 두 번 겹치므로 상쇄됩니다. 이것이 **버블 푸싱(bubble pushing)** 입니다.

그림을 바꿀 때는 출력에서 입력 방향으로 작업하고, 부정을 게이트 너머로 옮길 때 AND↔OR를 바꾸며 **모든 입력의 부정**을 바꿉니다. 한 입력만 임의로 뒤집지 않습니다. 반전 한 쌍을 더하거나 없애도 기능은 유지되지만, 실제 게이트를 추가·삭제하면 지연과 부하는 달라질 수 있습니다.

## 기술과 목표에 따라 좋은 구현이 다르다

1장의 CMOS 선택 심화에서 NAND·NOR를 직접 만들 수 있다는 것을 배웠습니다. AND나 OR를 일일이 NAND/NOR와 인버터로 바꾸기보다, 경계의 반전을 함께 정리하면 불필요한 인버터를 줄일 수 있습니다. 반면 무조건 게이트 수만 줄이면 깊이가 늘거나 부하가 커질 수도 있습니다. 면적·지연·전력·사용 가능한 셀을 함께 비교합니다.

## 헷갈리기 쉬운 점

최소 SOP는 **그 표현 형식 안에서의 최소**입니다. 다단 회로·MUX·XOR 셀까지 허용하면 다른 구현이 유리할 수 있습니다. 반대로 버블 푸싱으로 도면만 동치 기호로 바꾼 경우에는 실제 하드웨어가 바뀐 것이 아닙니다. 도면 변환과 물리 회로 변경을 구분합니다.

## 직접 확인하기

1. `n0=¬(A·B)`, `Y=¬(n0·C)`를 AND·OR·NOT 식으로 정리해보세요.
2. 입력 8개의 균형 잡힌 두 입력 XOR 트리에 게이트가 7개라면, 모든 게이트의 지연을 같다고 가정할 때 최장 경로는 몇 단계인가요?
3. NAND 출력 반전을 입력으로 옮길 때 게이트 몸체와 입력 부정은 어떻게 바뀌나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. Y=¬n0+¬C=<strong>A·B+¬C</strong>입니다. 마지막 NAND의 두 입력 모두에 부정이 분배됩니다.</p>
<p>2. 8→4→2→1이므로 <strong>3단계</strong>입니다. 요소 총수와 경로 깊이를 구분합니다.</p>
<p>3. AND 몸체가 <strong>OR</strong>로 바뀌며 <strong>모든 입력에 반전</strong>이 생깁니다.</p>
</details>

## 다음으로 이어가기

지금까지 유효한 0·1의 논리를 다뤘습니다. 다음에는 회로가 값을 구동하지 않거나 서로 다른 값으로 싸울 때 시뮬레이터가 무엇을 표시하는지 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §2.5.1–2.5.2, 인쇄 pp. 67–71 / PDF pp. 89–93. NAND 추적 예제·도식·문제를 새로 구성했습니다.
