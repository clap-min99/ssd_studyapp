## 이번 레슨의 목표

재귀 단계마다 별도 프레임을 만들고 기저 조건부터 역순으로 반환값을 계산합니다.

## 앞에서 배운 내용

레슨14에서 원래 인자와 ra를 저장했습니다. 재귀(recursion)는 같은 코드의 여러 호출이 각자의 인자·복귀 상태를 가지는 경우입니다.

## 같은 코드 주소와 다른 데이터 프레임

곱셈 확장 없이 핵심 RV32I만 사용하도록 자체 예제 `sum_down(n)=n+sum_down(n−1)`, `sum_down(0)=0`을 사용합니다. 입력은 작은 비음수 정수, 스택 공간은 충분하다고 가정합니다.

```asm
sum_down:
addi sp, sp, -16
sw   ra, 12(sp)
sw   a0, 8(sp)
beq  a0, zero, recur_return
addi a0, a0, -1
jal  ra, sum_down
lw   t0, 8(sp)
add  a0, a0, t0
recur_return:
lw   ra, 12(sp)
addi sp, sp, 16
jalr zero, 0(ra)
```

기저 조건(base case)은 a0=0일 때입니다. 이때 a0는 이미 반환값0이므로 바로 복원부로 갑니다. n>0은 호출 전에 n을 저장하고, n−1 결과가 돌아온 뒤 그 n을 더합니다. 모든 경로에서 프레임을 해제하고 ra를 복원합니다.

프레임마다 실행 코드의 주소는 같지만 sp가 달라 저장 위치는 다릅니다. 안쪽 호출이 바깥 인자와 ra를 덮지 않는 이유입니다. 재귀의 깊이가 커지면 스택 소비도 커지므로 종료 여부와 공간을 함께 확인합니다. 책의 factorial 재귀는 같은 원리에 M 확장 곱셈을 더한 예입니다.

## 선택 보충: 추가 인자와 지역 변수

작은32비트 정수 인자가8개를 넘으면 첫8개는 a0–a7,9번째부터는 호출자가 준비한 스택 공간을 사용합니다. 피호출자 진입 시점의 sp를 S라고 하면9번째 인자는0(S)에 있습니다. 피호출자가 자기 프레임16바이트를 잡아 sp=S−16으로 바꾸면 같은 인자의 위치는16(sp)입니다. 프레임을 잡았다고 인자가 함께 이동하지는 않습니다. 크기가 큰 인자·가변 인자·정렬 규칙 전체는 여기서 다루지 않습니다.

지역 배열과 레지스터에 담지 못한 변수도 프레임 안의 공간을 차지합니다. 예를 들어32비트 지역 원소3개에12바이트가 필요하고, 저장한 ra·기타 레지스터와 정렬 여유를 더해 전체 프레임 크기를 정합니다. 선택적인 프레임 포인터 fp는 s0(x8)을 사용해 기준 주소를 고정할 수 있으며 s0의 보존 책임도 따라옵니다. ‘지역 변수 하나당 반드시 s 레지스터 하나’ 또는 ‘모든 함수에 fp가 필수’는 아닙니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-15-t c6-15-d">
<title id="c6-15-t">n=2에서 n=0까지 호출하면16바이트 프레임 세 개가 동시에 존재한다.</title>
<desc id="c6-15-d">진입 전 sp=0x3000 / n=2 프레임: sp=0x2FF0 / n=1 프레임: sp=0x2FE0 / n=0 프레임: sp=0x2FD0</desc>
<rect x="75" y="18" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="41" text-anchor="middle" font-size="14" fill="var(--ink)">진입 전 sp=0x3000</text>
<rect x="75" y="56" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="79" text-anchor="middle" font-size="14" fill="var(--ink)">n=2 프레임: sp=0x2FF0</text>
<rect x="75" y="94" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="117" text-anchor="middle" font-size="14" fill="var(--ink)">n=1 프레임: sp=0x2FE0</text>
<rect x="75" y="132" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="155" text-anchor="middle" font-size="14" fill="var(--ink)">n=0 프레임: sp=0x2FD0</text>
</svg>
<p class="diagram-caption">그림 6-15. n=2에서 n=0까지 호출하면16바이트 프레임 세 개가 동시에 존재한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

n=2면 n=2,1,0 순서로 내려갑니다. sp는0x3000→0x2FF0→0x2FE0→0x2FD0입니다. 최하위 호출이0을 반환하고 프레임을 해제합니다. n=1 프레임이 저장한1을 더해1, n=2 프레임이 저장한2를 더해3을 반환합니다. sp는 역순으로0x3000까지 복구됩니다. 최대 동시 점유는3×16=48바이트입니다.

n=3이면 호출4개로64바이트를 사용하고 결과는0+1+2+3=6입니다. 호출 수와 ‘다시 자기 자신을 부른 횟수’는 각각4회와3회로 다릅니다.

## 헷갈리기 쉬운 점

이 코드는 음수 입력을 허용하지 않습니다. −1이면0으로 접근하는 대신 감소하여 계약 밖 실행이 됩니다. 종료 조건이 있는 것만으로 모든 입력의 종료를 보장하지 않습니다. 반복문으로도 같은 합을 구할 수 있으며 재귀가 자동으로 빠른 것은 아닙니다.

## 직접 확인하기

1. n=0이면 프레임은 몇 개인가요?
2. n=4의 결과와 최대 스택 점유는?
3. 원래 n을 a0로 복원하면 왜 안 되나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 이 코드에서는1개입니다. 검사 전에16바이트를 잡고 반환 전에 해제합니다.</p>
<p>2. 10과80바이트입니다. n=4,3,2,1,0의 다섯 프레임입니다.</p>
<p>3. 재귀 반환값이 든 a0를 덮습니다. t0로 읽어 두 값을 더해야 합니다.</p>
</details>

## 다음으로 이어가기

사람에게 편한 ret·mv·li가 실제로 어떤 명령어로 바뀌는지 정리합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.7, 인쇄 pp. 327–330 / PDF pp. 348–351. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 재귀 합 예제는 RV32I만 사용하는 자체 대체 예제입니다.
