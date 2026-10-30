## 이번 레슨의 목표

[선택 심화] M 확장과 RV32I를 구별하고 곱의 상위·하위32비트를 signed 해석에 따라 계산합니다.

## 앞에서 배운 내용

5장 곱셈기에서 N×N비트의 전체 곱이 2N비트임을 배웠습니다. 이 레슨은 RV32IM을 가정하며 건너뛰어도 분기 학습에 지장이 없습니다.

## 낮은 절반과 높은 절반은 다른 정보다

`mul rd,rs1,rs2`는 32×32비트 곱의 하위32비트를 씁니다. signed·unsigned 해석이 달라도 하위32비트는 같습니다. 2의 보수 음수와 그 unsigned 해석은 2³²의 배수만큼 다르므로 곱의 차이도 2³²의 배수이기 때문입니다.

상위32비트는 `mulh`(signed×signed), `mulhu`(unsigned×unsigned), `mulhsu`(signed rs1×unsigned rs2)로 고릅니다. 전체 곱을 보존하려면 소스를 덮지 않는 두 목적지에 높은 부분과 낮은 부분을 따로 씁니다.

```asm
mulh t0, a0, a1
mul  t1, a0, a1
```

결과는 64비트 연결 `{t0,t1}`입니다. 첫 명령어의 목적지가 a0이면 둘째 명령어가 이미 바뀐 소스를 읽는 문제가 생깁니다.

## 나눗셈에서 해석과 예외 조건 정하기

M 확장의 `div`·`rem`은 signed 몫·나머지, `divu`·`remu`는 unsigned 몫·나머지입니다. 정상 signed 나눗셈은 몫을 0 방향으로 절삭하고, 0이 아닌 나머지의 부호는 피제수와 같습니다. 피제수=제수×몫+나머지로 검산합니다. 0으로 나누기는 ISA에서 몫을 모든 비트1, 나머지를 피제수로 정하며 자동 나눗셈 예외를 일으키지 않습니다. signed 최솟값/−1도 결과 규칙이 따로 있습니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-6-t c6-6-d">
<title id="c6-6-t">64비트 곱은 상위와 하위의 두 32비트 값으로 나뉜다.</title>
<desc id="c6-6-d">상위31:0|mulh / mulhu / 하위31:0|mul</desc>
<rect x="12.0" y="55" width="228.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="126.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">상위31:0</text>
<text x="126.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">mulh / mulhu</text>
<rect x="240.0" y="55" width="228.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="354.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">하위31:0</text>
<text x="354.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">mul</text>
<text x="15" y="38" font-size="13" fill="var(--ink)">상위 비트 → 하위 비트</text>
</svg>
<p class="diagram-caption">그림 6-6. 64비트 곱은 상위와 하위의 두 32비트 값으로 나뉜다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

a0=0xFFFFFFFF, a1=2입니다. signed로는 −1×2=−2이므로 전체 패턴 0xFFFFFFFFFFFFFFFE, mulh=0xFFFFFFFF, mul=0xFFFFFFFE입니다. unsigned로는 (2³²−1)×2=0x00000001FFFFFFFE이므로 mulhu=1, mul은 여전히 0xFFFFFFFE입니다.

별도로 −17/5의 div 결과는 −3, rem 결과는 −2입니다. 5×(−3)+(−2)=−17이며 |나머지|<5입니다. srai로 2의 거듭제곱을 나누는 경우와 절삭 방향을 섞지 않습니다.

## 헷갈리기 쉬운 점

M 확장 없이 mul을 기본 명령어로 실행할 수 있다고 가정하지 않습니다. signed 최솟값 −2³¹을 −1로 나누면 div는 최솟값 패턴, rem은0을 반환합니다. 언어 차원의 오류 정책은 이 ISA 동작과 별도입니다.

## 직접 확인하기

1. 0xFFFFFFFF 두 개를 unsigned로 곱한 상위·하위는?
2. 같은 두 패턴을 signed로 곱하면?
3. 17을 −5로 나눈 signed 몫·나머지는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0xFFFFFFFE와 1입니다. 전체 곱은 0xFFFFFFFE00000001입니다.</p>
<p>2. −1×−1=1이므로 상위0, 하위1입니다.</p>
<p>3. −3과2입니다. (−5)×(−3)+2=17입니다.</p>
</details>

## 다음으로 이어가기

핵심 과정으로 돌아와 계산 결과에 따라 실행 경로를 바꾸는 분기를 배웁니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.2, 6.6.3, 인쇄 pp. 310–311, 360–361 / PDF pp. 331–332, 381–382. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 나눗셈 경계 동작은 공식 [M 확장 명세](https://docs.riscv.org/reference/isa/unpriv/m-st-ext.html)로 보충합니다.
