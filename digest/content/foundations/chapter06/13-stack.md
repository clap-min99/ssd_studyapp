## 이번 레슨의 목표

스택 프레임의 할당·저장·복원·해제를 추적하고 caller-saved와 callee-saved를 구별합니다.

## 앞에서 배운 내용

레슨12의 함수가 기존 s0을 임시 계산에 쓰려면 호출자의 값을 지킬 방법이 필요합니다.

## 스택은 주소로 관리하는 임시 메모리다

스택(stack)은 나중에 할당한 공간을 먼저 해제하는 LIFO 영역입니다. 스택 포인터 sp=x2가 현재 프레임의 낮은 주소를 가리키고 공간을 잡을 때 sp를 줄입니다. 이 장의 자체 예제는 표준 정수 ABI의16바이트 정렬을 유지하여16의 배수만큼 할당합니다. 책 앞부분의4·8·12바이트 단순화 예제와 구별합니다.

```asm
use_saved:
addi sp, sp, -16
sw   s0, 12(sp)
add  s0, a0, a1
addi a0, s0, 2
lw   s0, 12(sp)
addi sp, sp, 16
jalr zero, 0(ra)
```

저장 위치는 새 sp 기준입니다. 원래 s0을 저장한 다음에 s0을 덮고, 반환 전에 복원한 뒤 프레임을 해제합니다. sp를 복구했다고 메모리 바이트가 자동으로0이 되지는 않습니다. 해제한 공간의 내용에 의존해서는 안 됩니다.

## 누가 보존할 책임을 지는가

| 분류 | 레지스터 | 책임 |
| --- | --- | --- |
| callee-saved | s0–s11, sp | 피호출자가 바꾸면 반환 전에 복원 |
| caller-saved | t0–t6, a0–a7, ra | 호출자가 호출 뒤 필요한 값을 보존 |
| 예약 용도 | gp, tp | 일반 임시값으로 수정하지 않음 |

책의 보존 표는 ra를 보존 그룹에 넣어 설명하지만 표준 ABI에서 ra는 caller-saved입니다. 다른 함수를 부르는 현재 함수는 자신의 복귀에 필요한 ra를 그 호출 전에 보관합니다. 그래서 중첩 함수의 시작에서 ra를 저장하는 코드가 흔합니다. ‘모든 피호출자가 들어온 ra를 반드시 같은 값으로 돌려준다’는 보장으로 읽지 않습니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-13-t c6-13-d">
<title id="c6-13-t">sp=0x1000에서16바이트를 할당해 s0을 프레임 내부에 보관한다.</title>
<desc id="c6-13-d">옛 sp: 0x1000 / 0x0FFC: 저장한 옛 s0 / 0x0FF0–0x0FFB: 여유 공간 / 새 sp: 0x0FF0 (16바이트 정렬)</desc>
<rect x="75" y="18" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="41" text-anchor="middle" font-size="14" fill="var(--ink)">옛 sp: 0x1000</text>
<rect x="75" y="56" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="79" text-anchor="middle" font-size="14" fill="var(--ink)">0x0FFC: 저장한 옛 s0</text>
<rect x="75" y="94" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="117" text-anchor="middle" font-size="14" fill="var(--ink)">0x0FF0–0x0FFB: 여유 공간</text>
<rect x="75" y="132" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="155" text-anchor="middle" font-size="14" fill="var(--ink)">새 sp: 0x0FF0 (16바이트 정렬)</text>
</svg>
<p class="diagram-caption">그림 6-13. sp=0x1000에서16바이트를 할당해 s0을 프레임 내부에 보관한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

시작 sp=0x1000,s0=77,a0=4,a1=9입니다. 할당 뒤 sp=0xFF0, 저장 주소는0xFF0+12=0xFFC입니다. s0=13,a0=15로 계산한 뒤0xFFC에서77을 다시 읽습니다. sp를16 늘려0x1000으로 복구하고 반환합니다. 반환값15와 보존값 s0=77을 동시에 얻었습니다.

함수가 t0만 바꾸고 다른 함수를 부르지 않았다면 t0 보존은 필요하지 않습니다. 반대로 호출자가 t0에 중요한 값77을 두었다면 호출 전에 자기 프레임에 보관해야 합니다.

## 헷갈리기 쉬운 점

callee-saved는 호출 때 자동 저장된다는 뜻이 아닙니다. 코드가 책임을 수행해야 합니다. 표준 ABI에서는 sp 아래의 미할당 공간에 저장한 값이 호출을 건너 안전하다고 가정하지 않습니다. 프레임을 잡은 뒤 범위 안에 씁니다.

## 직접 확인하기

1. sp=0x2000에서32바이트 할당 후 sp는?
2. 리프 함수가 t0을 바꾸면 반드시 저장해야 하나요?
3. s1을 덮는 함수가 복원하지 않고 반환하면?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0x1FE0입니다. 반환 때32를 더해 복구합니다.</p>
<p>2. 아닙니다. t0은 caller-saved입니다.</p>
<p>3. 호출자의 s1이 유지된다는 ABI 약속을 어겨 호출자 계산이 깨질 수 있습니다.</p>
</details>

## 다음으로 이어가기

같은 함수가 호출자이면서 피호출자인 중첩 호출을 추적합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.7, 6.5.1, 인쇄 pp. 322–326, 346 / PDF pp. 343–347, 367. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 책과 구별한 ra 분류·정렬은 공식 [RISC-V psABI의 정수 호출 규약](https://riscv-non-isa.github.io/riscv-elf-psabi-doc/#_integer_calling_convention)을 따릅니다.
