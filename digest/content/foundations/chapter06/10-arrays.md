## 이번 레슨의 목표

배열의 베이스 주소·원소 크기·인덱스로 실효 주소를 만들고 포인터 순회와 비교합니다.

## 앞에서 배운 내용

레슨4의 주소 단위는 바이트, 레슨9의 i는 원소 번호입니다. 두 단위를 변환해야 합니다.

## 주소 = 베이스 + 인덱스×원소 크기

32비트 원소의 배열 A에서 A[i] 주소는 base+4i입니다. shift-left2로 i를4배한 후 베이스에 더합니다. 다음 자체 예제는 비음수 길이 a1, 베이스 a0의 배열을 읽어 t0에 합산합니다. 접근 가능한 메모리와 주소 계산 범위를 가정합니다.

```asm
addi t0, zero, 0
addi t1, zero, 0
array_loop:
bge  t1, a1, array_done
slli t2, t1, 2
add  t2, a0, t2
lw   t3, 0(t2)
add  t0, t0, t3
addi t1, t1, 1
jal  zero, array_loop
array_done:
```

베이스와 크기를 혼동해 i만 더하면 i=1에서 두 번째 바이트를 가리킵니다. load가 워드를 읽어 준다고 주소까지4배해 주지는 않습니다. 저장은 같은 주소를 다시 계산하거나 보존한 뒤 `sw`로 수행합니다.

## 포인터 순회는 무엇이 달라질까

포인터 p를 base에서 시작해 매번 `addi p,p,4`로 바꾸는 구현도 가능합니다. 그러면 반복 내 시프트·베이스 덧셈을 줄일 수 있지만 원래 베이스가 필요하면 따로 보존합니다. 두 방식 모두 마지막 유효 원소는 i=length−1이며, 종료 후 한 칸 뒤 포인터는 주소로 보관만 하고 역참조하지 않습니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-10-t c6-10-d">
<title id="c6-10-t">베이스0x600의 32비트 배열은 인덱스가1 늘 때 주소가4 늘어난다.</title>
<desc id="c6-10-d">A[0]: 0x600 → 5 / A[1]: 0x604 → 8 / A[2]: 0x608 → 2 / 종료 i=3: 0x60C는 읽지 않음</desc>
<rect x="75" y="18" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="41" text-anchor="middle" font-size="14" fill="var(--ink)">A[0]: 0x600 → 5</text>
<rect x="75" y="56" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="79" text-anchor="middle" font-size="14" fill="var(--ink)">A[1]: 0x604 → 8</text>
<rect x="75" y="94" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="117" text-anchor="middle" font-size="14" fill="var(--ink)">A[2]: 0x608 → 2</text>
<rect x="75" y="132" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="155" text-anchor="middle" font-size="14" fill="var(--ink)">종료 i=3: 0x60C는 읽지 않음</text>
</svg>
<p class="diagram-caption">그림 6-10. 베이스0x600의 32비트 배열은 인덱스가1 늘 때 주소가4 늘어난다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

a0=0x600,a1=3이고 배열은[5,8,2]입니다. i=0이면 t2=0+0x600, 합5. i=1이면 t2=4+0x600, 합13. i=2이면 t2=8+0x600, 합15입니다. i=3에서 종료하여0x60C는 읽지 않습니다. 세 값의 수학적 합5+8+2=15와 같습니다.

포인터 구현의 읽기 주소열도0x600,0x604,0x608이어야 합니다. 길이0이면 첫 검사로 종료하여 메모리 읽기0회, 결과0입니다. 이 경계가 같아야 두 구현이 동등하다고 할 수 있습니다.

## 헷갈리기 쉬운 점

RISC-V 명령어가 배열 길이를 자동 검사하지 않습니다. i≤length로 잘못 쓰면 배열 밖 한 워드를 읽습니다. C의 포인터와 인덱스 표현을 설명하기 위한 예이며 signed C 덧셈의 범위 초과까지 정의하는 것은 아닙니다.

## 직접 확인하기

1. base=0x800에서 A[7]의 주소는?
2. 16비트 원소 배열 A[7]이면 같은 베이스에서?
3. 포인터를1씩 증가하면서 lw하면 되나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0x800+28=0x81C입니다.</p>
<p>2. 14바이트를 더한0x80E입니다. 원소 크기가 달라졌습니다.</p>
<p>3. 워드 원소 순회에는4씩 증가해야 합니다. 1씩 증가는 바이트 순회입니다.</p>
</details>

## 다음으로 이어가기

다음에는 원소 크기1바이트와 종료 문자를 사용하는 문자열을 다룹니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.6, 인쇄 pp. 317–319 / PDF pp. 338–340. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
