## 이번 레슨의 목표

[선택 심화] 비교·부분 폭 적재의 signed 차이를 설명하고 모듈러 덧셈 뒤 넘침을 검사합니다.

## 앞에서 배운 내용

레슨5의 시프트, 레슨7의 분기, 레슨11의 부분 폭 load를 같은 해석 문제로 연결합니다.

## 데이터에 타입 꼬리표가 붙어 있지 않다

32비트0x80000000은 unsigned로2147483648, signed로−2147483648입니다. `slt rd,rs1,rs2`는 signed로 작으면1,아니면0을 쓰고 `sltu`는 unsigned로 비교합니다. 분기의 blt·bge와 bltu·bgeu도 같은 차이입니다. equality는 패턴이 같은지를 보므로 별도의 unsigned BEQ가 필요 없습니다.

`sltiu`의 u는 비교 해석을 뜻하며 즉시값의 확장 규칙을0 확장으로 바꾸지 않습니다. 먼저12비트 signed 즉시값을32비트로 부호 확장한 다음 unsigned로 비교합니다. 예를 들어 즉시값−1은 비교 시4294967295입니다.

## ADD 자체와 넘침 검사는 분리한다

RV32I ADD는 signed 여부와 관계없이 하위32비트를 저장합니다. unsigned 합에서 결과가 한 입력보다 작으면 carry로 범위를 넘었습니다.

```asm
add  t0, a0, a1
bltu t0, a0, unsigned_overflow
```

signed 합은 두 입력의 부호가 같고 결과의 부호가 달라졌을 때 overflow입니다. 하드웨어 플래그에 의존하지 않고 비교·논리 명령어 조합으로 검사할 수 있습니다. unsigned carry와 signed overflow는 서로 다른 조건입니다. LH·LB의 부호 확장과 LHU·LBU의0 확장도 명령어가 정하는 해석입니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-26-t c6-26-d">
<title id="c6-26-t">같은 ADD 결과에서도 두 종류의 범위 초과 판단은 다를 수 있다.</title>
<desc id="c6-26-d">0x7FFFFFFF|+ 0x00000001 / 결과|0x80000000 / unsigned carry=0|signed overflow=1</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">0x7FFFFFFF</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">+ 0x00000001</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">결과</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">0x80000000</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">unsigned carry=0</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">signed overflow=1</text>
</svg>
<p class="diagram-caption">그림 6-26. 같은 ADD 결과에서도 두 종류의 범위 초과 판단은 다를 수 있다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

a0=0x7FFFFFFF,a1=1입니다. 결과 t0=0x80000000이고 unsigned로2147483648은 a0보다 크므로 위 bltu는 선택되지 않습니다. signed로는 양수+양수가 음수 패턴이 되어 overflow입니다.

a0=0xFFFFFFFF,a1=1로 바꾸면 t0=0입니다. unsigned로0<4294967295라 carry를 검출합니다. signed로는−1+1=0이라 overflow가 없습니다. 별도로 s1=7에서 `sltiu t1,s1,-1`은7<0xFFFFFFFF라1을 씁니다.

## 헷갈리기 쉬운 점

t0의 부호 비트만으로 signed overflow를 알 수 없습니다. 음수의 정상 합도 최상위 비트가1입니다. 이 ISA 결과를 C의 signed overflow도 항상 wrap한다는 설명으로 옮기지 않습니다. 언어 수준의 정의되지 않은 동작과 하드웨어 명령어 의미는 다릅니다.

## 직접 확인하기

1. 0xFFFFFFFF<1을 SLT·SLTU로 비교한 결과는?
2. 0x80000000+0x80000000의 결과와 두 넘침은?
3. sltiu의 즉시값−2가 비교하는 unsigned 값은?

<details>
<summary>정답과 해설 보기</summary>
<p>1. SLT는1,SLTU는0입니다.</p>
<p>2. 결과0,unsigned carry=1,signed overflow=1입니다. 두 음수의 합이0이 됐습니다.</p>
<p>3. 부호 확장한0xFFFFFFFE,즉4294967294입니다.</p>
</details>

## 다음으로 이어가기

다음에는 기본32비트 정수 모델을 부동소수점과 짧은 명령어로 확장합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.6.3, 인쇄 pp. 360–361 / PDF pp. 381–382. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
