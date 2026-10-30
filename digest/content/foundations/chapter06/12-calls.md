## 이번 레슨의 목표

JAL·JALR의 다음 PC와 링크 값을 계산하고 인자·반환값의 전달 위치를 설명합니다.

## 앞에서 배운 내용

레슨7에서는 복귀 주소를 버리는 점프를 썼습니다. 함수는 실행을 마치고 호출 다음 명령어로 돌아와야 합니다.

## 이동하면서 돌아갈 주소를 남기기

`jal rd,label`은 rd에 현재 PC+4를 쓰고, PC를 레이블 주소로 바꿉니다. rd=ra(x1)이면 호출 다음 주소를 저장합니다. 인자를 a0–a7에 놓고 작은 정수 반환값을 a0에서 받는 약속은 호출 규약(calling convention), 즉 ABI의 일부입니다. ISA가 a0의 값을 자동 준비하는 것은 아닙니다.

```asm
# 호출자 일부: p=6, q=9를 전달
addi a0, zero, 6
addi a1, zero, 9
jal  ra, add_pair
# 이 위치에서 a0=15를 사용
```

아래 함수는 다른 함수를 호출하지 않는 리프 함수(leaf function)입니다. 명령어가 실제로 연속 배치되었다고 보면 호출자 후속 코드가 함수 본문으로 다시 흘러가지 않도록 별도 경로가 필요합니다. 여기 코드는 호출자 일부와 별도 함수 정의입니다.

```asm
add_pair:
add  a0, a0, a1
jalr zero, 0(ra)
```

## 레지스터로 목표 주소 지정하기

`jalr rd,imm(rs1)`은 옛 rs1+signed12비트 imm에서 최하위 비트를0으로 만든 주소로 가고 rd에 PC+4를 씁니다. 개념식은 `target=(old_R[rs1]+imm) AND 0xFFFFFFFE`입니다. `jalr zero,0(ra)`는 저장해 둔 복귀 주소로 가며 새 링크는 버립니다. `ret`·`jr ra`는 이 명령어의 의사명령어입니다.

jal은 PC 상대, jalr은 베이스 레지스터 상대입니다. jalr의 offset은 B·J 형식처럼2배하는 값이 아닙니다. C 확장이 없는 예제에서는 목표가4바이트 경계에도 맞아야 합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-12-t c6-12-d">
<title id="c6-12-t">호출의 링크 저장과 복귀의 PC 이동을 따로 읽는다.</title>
<desc id="c6-12-d">호출 PC=0x180|ra ← 0x184 / 함수0x240|a0 ← a0+a1 / JALR zero,0(ra)|PC ← 0x184</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">호출 PC=0x180</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">ra ← 0x184</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">함수0x240</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">a0 ← a0+a1</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">JALR zero,0(ra)</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">PC ← 0x184</text>
</svg>
<p class="diagram-caption">그림 6-12. 호출의 링크 저장과 복귀의 PC 이동을 따로 읽는다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

jal 주소가0x180, add_pair가0x240이고 입력 a0=6,a1=9입니다. jal 실행 후 ra=0x184,PC=0x240. add 후 a0=15,PC=0x244. 그곳의 jalr은 PC=0x184로 복귀하며 ra는 그대로0x184입니다. 링크를 저장하는 것과 반환값을 계산하는 것은 별개 작업입니다.

다른 예로 PC=0x300에서 `jalr t0,4(t1)`을 실행하고 옛 t1=0x501이면 합0x505의 비트0을 지워 목표0x504, t0=0x304입니다. 최하위 비트를 지워도 항상4바이트 정렬이 되는 것은 아닙니다.

## 헷갈리기 쉬운 점

ra는 하드웨어 전용 스택이 아닙니다. 다음 jal ra가 이전 값을 덮습니다. a0도 인자와 반환에 함께 쓰므로 호출 후 원래 인자가 필요하면 미리 보존해야 합니다. 함수가 자동으로 모든 레지스터를 원상복구하지 않습니다.

## 직접 확인하기

1. 0x200에서 jal ra,func 뒤 ra는?
2. jal zero,func가 일반 호출과 다른 점은?
3. t1=0x502에서 jalr zero,0(t1)의 정렬은?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0x204입니다. func의 주소가 아니라 호출 다음 주소입니다.</p>
<p>2. 복귀 주소를 x0에 버려 저장하지 않습니다.</p>
<p>3. 목표0x502입니다. 비트0은 이미0이지만4바이트 정렬이 아니므로 C 없는 이 모델에서 정상 점프할 수 없습니다.</p>
</details>

## 다음으로 이어가기

복귀 주소와 호출 뒤에도 필요한 값을 보관할 메모리 공간인 스택을 배웁니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.7, 인쇄 pp. 320–322 / PDF pp. 341–343. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. JALR의 비트0 처리와 정렬은 공식 [RV32I 명세](https://docs.riscv.org/reference/isa/unpriv/rv32.html)로 보충합니다.
