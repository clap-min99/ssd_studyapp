## 이번 레슨의 목표

반복문의 초기화·조건·본문·갱신을 분리하고 0회·마지막 반복·종료 상태를 추적합니다.

## 앞에서 배운 내용

레슨8에서는 두 경로가 합쳐졌습니다. 이번에는 조건 위치로 되돌아가는 간선을 만듭니다.

## 종료 검사는 본문보다 한 번 더 할 수 있다

다음은0부터3까지의 합을 구하는 자체 예제입니다. s0은 i, s1은 sum, t0은 반복 상한4입니다.

```asm
addi s0, zero, 0
addi s1, zero, 0
addi t0, zero, 4
sum_loop:
bge  s0, t0, sum_done
add  s1, s1, s0
addi s0, s0, 1
jal  zero, sum_loop
sum_done:
```

첫 세 명령어는 한 번만 실행합니다. 반복에서는 먼저 `i>=4`로 종료할지 검사하고, 아니면 합산 후 i를 증가시킵니다. 마지막 i=4에서는 조건 검사만 하고 본문을 실행하지 않습니다. 조건의 참·거짓을 본문 실행 여부와 연결해야 합니다.

## While와 Do/While의 차이

while은 본문 앞 검사이므로 처음부터 조건이 거짓이면0회 실행합니다. do/while은 본문 뒤 검사이므로 최소1회 실행합니다. for의 초기화·검사·갱신도 위 네 위치로 풀 수 있습니다. 반복마다 무엇이 유지되는지를 나타내는 반복 불변식(loop invariant)은 검산에 유용합니다. 위 예제에서는 검사 시점에 sum=0부터 i−1까지의 합입니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-9-t c6-9-d">
<title id="c6-9-t">종료 검사로 돌아가는 경로가 반복을 만든다.</title>
<desc id="c6-9-d">검사 i&lt;4|아니면 종료 / sum ← sum+i|본문 / i ← i+1|검사로 복귀</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">검사 i&lt;4</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">아니면 종료</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">sum ← sum+i</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">본문</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">i ← i+1</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">검사로 복귀</text>
</svg>
<p class="diagram-caption">그림 6-9. 종료 검사로 돌아가는 경로가 반복을 만든다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

검사 시점의 (i,sum)은 (0,0)→(1,0)→(2,1)→(3,3)→(4,6)입니다. i=4에서 종료하므로 본문4회, bge 검사5회입니다. 합은4×3/2=6으로 독립 검산합니다.

상한을0으로 바꾸면 첫 검사에서0≥0이라 본문을 실행하지 않고 (i,sum)=(0,0)입니다. i 증가를 빼면 i=0에서 영원히 반복할 수 있습니다. 종료 조건뿐 아니라 상태가 그 조건을 향해 움직이는지도 확인합니다.

## 헷갈리기 쉬운 점

레이블이 반복 횟수를 정하지 않습니다. 값의 변화와 분기가 정합니다. signed i가 범위를 넘어 wrap하면 수학적 증가 모델이 깨질 수 있으므로 이 예제는 작은 비음수 범위로 한정합니다.

## 직접 확인하기

1. 상한3이면 최종 i,sum은?
2. sum=0 초기화를 레이블 바로 아래로 옮기면?
3. 상한0의 while과 무조건 본문 뒤 검사 do/while이 같은가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 3,3입니다. 0+1+2만 더합니다.</p>
<p>2. 매 반복 합을 지워 누적하지 못합니다. 상한4에서는 최종 sum=3입니다.</p>
<p>3. 아닙니다. while은0회, do/while은 최소1회라 본문의 효과가 달라집니다.</p>
</details>

## 다음으로 이어가기

같은 반복 구조에 주소 계산을 넣으면 배열 원소를 차례로 처리할 수 있습니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.5, 인쇄 pp. 315–317 / PDF pp. 336–338. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
