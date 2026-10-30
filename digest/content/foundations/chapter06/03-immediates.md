## 이번 레슨의 목표

12비트 즉시값을 부호 확장하고 LUI·ADDI로 임의의 32비트 상수를 구성합니다.

## 앞에서 배운 내용

레슨2의 add는 두 레지스터를 읽었습니다. 상수 1을 매번 별도 레지스터에 둘 필요를 줄여 봅니다.

## 작은 상수를 명령어에 담기

즉시값(immediate)은 명령어 비트 안에 들어 있는 상수입니다. `addi rd,rs1,imm`은 rs1에 12비트 2의 보수 즉시값을 32비트로 부호 확장하여 더합니다. 범위는 −2048부터 2047입니다. `addi t0,zero,-12`는 상수를 만드는 예이고 `addi t0,t0,1`은 기존 값의 증가입니다.

12비트 0xFFF는 +4095가 아니라 −1입니다. 부호 확장하면 0xFFFFFFFF입니다. 숫자를 16진수로 썼다고 양수 즉시값이 되지 않습니다. 어셈블러의 입력 허용 표기 차이를 피하려고 음수는 `-1`처럼 씁니다.

## 큰 상수의 아래 12비트가 음수일 때

상위 즉시값 적재(load upper immediate), `lui rd,U`는 20비트 U를 비트31:12에 넣고 아래 12비트를 0으로 만듭니다. 그 뒤 addi로 아래 부분을 더합니다. 원하는 32비트 패턴 C에 대해 L=C의 하위12비트, low=L(단 L≥2048이면 L−4096), U=((C+0x800)≫12)의 하위20비트로 잡습니다.

0x800을 더하는 이유는 low를 음수로 읽을 때 상위 부분에 4096을 미리 더해 두기 위해서입니다. 이는 비트 이어 붙이기가 아니라 부호 있는 덧셈입니다. `li` 의사명령어의 상수 조립도 이 원리를 사용합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-3-t c6-3-d">
<title id="c6-3-t">하위 12비트의 부호 때문에 상위 부분을 한 단위 보정한다.</title>
<desc id="c6-3-d">목표|0x12345ABC / LUI 결과|0x12346000 / ADDI −1348|0x12345ABC</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">목표</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">0x12345ABC</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">LUI 결과</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">0x12346000</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">ADDI −1348</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">0x12345ABC</text>
</svg>
<p class="diagram-caption">그림 6-3. 하위 12비트의 부호 때문에 상위 부분을 한 단위 보정한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

목표는 0x12345ABC입니다. 하위 0xABC=2748은 12비트 signed에서 2748−4096=−1348입니다. 상위 0x12345를 그대로 쓰면 목표보다 0x1000 작아집니다. 따라서 다음과 같이 만듭니다.

```asm
lui  t0, 0x12346
addi t0, t0, -1348
```

0x12346000−0x544=0x12345ABC입니다. 조건을 바꿔 0x12345678을 만들면 아래 0x678=1656은 양수이므로 U=0x12345를 그대로 씁니다. 경계 0x00000800은 `lui t0,1; addi t0,t0,-2048`에 해당하는 두 명령어로 구성합니다.

## 헷갈리기 쉬운 점

addi에 2048을 그대로 넣을 수 없습니다. LUI는 메모리를 읽지 않습니다. 모든 산술 결과는 RV32의 하위 32비트로 제한하며 C 언어 signed overflow의 규칙을 이와 동일하게 가정하지 않습니다.

## 직접 확인하기

1. 12비트 0x800의 signed 값은?
2. 0x000017FF를 조립할 U와 low는?
3. 0x00001800이면?

<details>
<summary>정답과 해설 보기</summary>
<p>1. −2048이며 32비트 부호 확장 결과는 0xFFFFF800입니다.</p>
<p>2. U=1, low=2047입니다. 0x1000+0x7FF=0x17FF입니다.</p>
<p>3. U=2, low=−2048입니다. 0x2000−0x800=0x1800입니다.</p>
</details>

## 다음으로 이어가기

명령어 내부의 상수와 달리 큰 데이터는 메모리 주소를 통해 가져옵니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.2.2, 인쇄 pp. 304–306 / PDF pp. 325–327. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
