## 이번 레슨의 목표

중첩 호출 전후에 원래 인자와 복귀 주소를 보존하고 반환값을 덮지 않게 복원합니다.

## 앞에서 배운 내용

레슨13의 스택과 보존 책임을 사용합니다. 다른 함수를 부르는 비리프 함수(nonleaf function)는 두 역할을 모두 가집니다.

## 호출을 건너 살아 있는 값을 찾기

자체 함수 `outer(n)=twice(n)+n`, `twice(n)=n+n`을 만듭니다. outer는 twice 호출 뒤 원래 n과 원래 호출자로 돌아갈 주소가 필요합니다. a0와 ra는 다음 호출에서 바뀔 수 있으므로 저장합니다. 아래는 독립된 두 함수 정의입니다.

```asm
outer:
addi sp, sp, -16
sw   ra, 12(sp)
sw   a0, 8(sp)
jal  ra, twice
lw   t0, 8(sp)
add  a0, a0, t0
lw   ra, 12(sp)
addi sp, sp, 16
jalr zero, 0(ra)

twice:
add  a0, a0, a0
jalr zero, 0(ra)
```

호출 전 a0를 저장한 이유는 원래 n이 필요하기 때문입니다. 호출 후 원래 n은 t0로 복원합니다. a0로 복원하면 방금 받은 twice의 결과를 잃습니다. t0은 복원 뒤 다른 호출 없이 바로 사용하므로 추가 보존이 필요 없습니다.

## 같은 ra에 서로 다른 복귀 위치가 들어간다

outer 진입 때 ra는 outer의 호출자로 돌아갈 위치입니다. jal twice가 실행되면 ra는 outer 내부의 `lw t0,8(sp)` 위치로 바뀝니다. twice는 그 값으로 돌아오고 outer는 메모리에서 더 바깥의 복귀 주소를 복원합니다. 소스 코드에서 함수 이름만 따라가면 이 두 주소의 차이를 놓치기 쉽습니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-14-t c6-14-d">
<title id="c6-14-t">외부 복귀 주소는 메모리에 남기고 ra는 내부 호출의 복귀에 사용한다.</title>
<desc id="c6-14-d">호출자 → outer|ra=A 저장 / outer → twice|ra=B 덮어쓰기 / twice → B|A 복원 → 호출자</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">호출자 → outer</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">ra=A 저장</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">outer → twice</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">ra=B 덮어쓰기</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">twice → B</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">A 복원 → 호출자</text>
</svg>
<p class="diagram-caption">그림 6-14. 외부 복귀 주소는 메모리에 남기고 ra는 내부 호출의 복귀에 사용한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

시작 a0=7,sp=0x2000,ra=0x304이며 outer를0x400에 배치했다고 가정합니다. 세 저장 준비 뒤 jal은0x40C에 있고 링크는0x410입니다. twice가 a0=14로 만들고0x410에 복귀합니다. 원래7을 t0로 읽고 더해 a0=21, ra=0x304와 sp=0x2000을 복원해 반환합니다.

입력을0으로 바꾸면 두 번 더해도0이지만 복귀 주소·프레임 복원 절차는 여전히 필요합니다. 저장 필요성은 숫자가 우연히 안 변한 한 번의 실행으로 판단하지 않습니다.

## 헷갈리기 쉬운 점

실제로 호출할 함수의 내부를 봤더라도 ABI상 허용된 변경을 전제로 코드를 작성합니다. 모든 임시 레지스터를 무조건 저장할 필요는 없고 호출 뒤 사용되는 값만 보존합니다. 프레임 크기16은 저장한 두 워드8바이트보다 클 수 있습니다.

## 직접 확인하기

1. outer에서 ra 저장을 빼면 무슨 문제가 생기나요?
2. lw a0,8(sp)로 원래 인자를 복원해도 되나요?
3. twice가 t0을 덮어도 현재 outer는 안전한가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. twice 호출이 ra를 내부 복귀 주소로 덮어 outer의 호출자로 정상 복귀할 수 없습니다.</p>
<p>2. 현재 코드에서는 안 됩니다. twice의 반환값을 덮어 2n+n 대신 n+n을 계산하게 됩니다.</p>
<p>3. 안전합니다. outer의 t0은 호출이 끝난 뒤 메모리에서 새로 읽어 즉시 사용합니다.</p>
</details>

## 다음으로 이어가기

비리프 함수가 자기 자신을 호출해도 프레임마다 별도 데이터를 두면 같은 원리가 적용됩니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.7, 인쇄 pp. 326–327 / PDF pp. 347–348. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
