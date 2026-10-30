## 이번 레슨의 목표

레지스터 번호와 ABI 별칭을 대응시키고 두 소스·한 목적지 명령어열을 추적합니다.

## 앞에서 배운 내용

레슨1에서 ISA를 상태 변화의 약속으로 보았습니다. 5장 레지스터 파일의 두 읽기·한 쓰기 포트와 연결합니다.

## 값이 들어 있는 장소와 그 이름

RV32I에는 32개의 32비트 정수 레지스터가 있습니다. x0은 항상 0을 읽고 쓰기를 버립니다. 나머지는 일반 정수 데이터를 저장합니다. 아래 이름은 별도 저장소가 아니라 같은 레지스터의 별칭입니다.

| 번호 | 별칭 | 이 장에서 쓰는 역할 |
| --- | --- | --- |
| x0 / x1 / x2 | zero / ra / sp | 상수 0 / 복귀 주소 / 스택 포인터 |
| x3 / x4 | gp / tp | 전역·스레드 포인터: 임의 임시값으로 사용하지 않음 |
| x5–x7 / x28–x31 | t0–t2 / t3–t6 | 임시값 |
| x8–x9 / x18–x27 | s0–s1 / s2–s11 | 호출 뒤 보존할 값 |
| x10–x17 | a0–a7 | 인자, a0·a1은 반환에도 사용 |

`add rd,rs1,rs2`는 `R[rd] ← (R[rs1]+R[rs2]) mod 2³²`, `sub`는 같은 위치 순서로 뺄셈합니다. R[x]는 레지스터에 들어 있는 값입니다. 두 입력을 읽은 결과를 목적지에 쓰므로 `add t0,t0,t1`처럼 소스와 목적지가 같아도 됩니다.

## 복잡한 식에는 중간값이 필요하다

`result=(p-q)+(r+s)`에서 먼저 두 괄호를 계산하고 마지막에 합칩니다. 변수 p,q,r,s가 a0,a1,a2,a3에 있다고 정한 자체 예제입니다.

```asm
sub t0, a0, a1
add t1, a2, a3
add a0, t0, t1
```

마지막 명령어가 a0을 덮지만 원래 p는 이미 첫 명령어에서 사용했습니다. 반대로 첫 단계에서 a2를 덮으면 두 번째 식의 r을 잃을 수 있습니다. 레지스터 배치는 이후에도 필요한 값을 기준으로 정합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-2-t c6-2-d">
<title id="c6-2-t">두 부분식의 결과를 마지막 덧셈의 소스로 사용한다.</title>
<desc id="c6-2-d">a0−a1|t0=13 / a2+a3|t1=12 / t0+t1|a0=25</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">a0−a1</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">t0=13</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">a2+a3</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">t1=12</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">t0+t1</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">a0=25</text>
</svg>
<p class="diagram-caption">그림 6-2. 두 부분식의 결과를 마지막 덧셈의 소스로 사용한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

p=20,q=7,r=3,s=9입니다. 첫 명령어 후 t0=13, 둘째 후 t1=12, 셋째 후 a0=25입니다. 원래 식으로 (20−7)+(3+9)=25라 검산합니다. a1,a2,a3은 바뀌지 않습니다.

이어 `add zero,a0,a1`을 실행하면 합 32가 계산되어도 x0은 계속 0입니다. `sub t0,zero,a1`은 0−7의 하위 32비트인 0xFFFFFFF9를 저장하며 signed 해석은 −7입니다.

## 헷갈리기 쉬운 점

레지스터 이름이 signed 타입을 정하지 않습니다. 동일한 32비트 패턴을 어느 명령어로 해석하느냐가 중요합니다. RV32I add·sub는 오버플로 예외나 영구적인 조건 플래그를 자동으로 만들지 않습니다.

## 직접 확인하기

1. s1은 x1인가요?
2. t0=6,t1=4에서 sub t0,t1,t0의 결과는?
3. a0=5에서 add zero,a0,a0 후 zero는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 아닙니다. s1은 x9이고 x1은 ra입니다.</p>
<p>2. 4−6=−2, 패턴은 0xFFFFFFFE입니다. 소스는 쓰기 전 값을 읽습니다.</p>
<p>3. 계속 0입니다. 계산 결과 쓰기를 버립니다.</p>
</details>

## 다음으로 이어가기

레지스터만으로 계산했으니 다음에는 명령어 안에 작은 상수를 직접 넣습니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.2.1–6.2.2, 인쇄 pp. 301–305 / PDF pp. 322–326. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
