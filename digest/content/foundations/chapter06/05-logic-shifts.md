## 이번 레슨의 목표

AND·OR·XOR와 논리·산술 시프트로 비트 필드를 추출하고 signed 반올림 차이를 설명합니다.

## 앞에서 배운 내용

5장 시프터와 ALU를 프로그램의 명령어로 사용합니다. 레슨3의 즉시값 부호 확장도 그대로 적용됩니다.

## 비트를 고르고 바꾸기

`and`, `or`, `xor`는 32개 비트에 각각 AND·OR·XOR를 적용합니다. `andi`, `ori`, `xori`는 두 번째 소스 대신 12비트 signed 즉시값을 부호 확장해 사용합니다. AND의 마스크가 0인 자리는 지우고 1인 자리는 유지합니다. OR의 마스크가 1인 자리는 설정하고 XOR의 1인 자리는 뒤집습니다.

예를 들어 `andi t0,t0,-9`는 0xFFFFFFF7과 AND하므로 비트3만 지웁니다. `xori t0,t0,-1`은 전체 반전입니다. 0xFF는 +255여서 아래8비트만 보존하지만 0xFFF를 12비트 패턴으로 해석하면 −1이라 전체32비트를 보존합니다.

## 이동한 뒤 필요 없는 비트를 지우기

`slli`는 왼쪽 빈자리를 0으로, `srli`는 오른쪽 이동의 상위 빈자리를 0으로, `srai`는 원래 부호 비트로 채웁니다. RV32 즉시 시프트량은 0부터31입니다. 레지스터 시프트 sll·srl·sra는 rs2의 하위5비트만 사용합니다.

필드15:8을 추출하려면 먼저 오른쪽으로8 이동하고 아래8비트만 남깁니다. 시프트만 하면 원래 상위 비트도 아래로 내려옵니다.

```asm
srli t0, s0, 8
andi t0, t0, 255
```

산술 오른쪽 시프트는 signed 값을 2의 거듭제곱으로 나누어 음의 무한대 방향으로 내린 결과입니다. signed 나눗셈의 0 방향 절삭과 음수 홀수에서 다를 수 있습니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-5-t c6-5-d">
<title id="c6-5-t">비트15:8을 아래로 이동한 뒤 마스크로 남긴다.</title>
<desc id="c6-5-d">s0|0xA1B2C3D4 / SRLI 8|0x00A1B2C3 / ANDI 255|0x000000C3</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">s0</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">0xA1B2C3D4</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">SRLI 8</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">0x00A1B2C3</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">ANDI 255</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">0x000000C3</text>
</svg>
<p class="diagram-caption">그림 6-5. 비트15:8을 아래로 이동한 뒤 마스크로 남긴다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

s0=0xA1B2C3D4일 때 8비트 이동 후 0x00A1B2C3, 0xFF와 AND하면 0xC3입니다. 원래 바이트를 상위부터 A1·B2·C3·D4로 나누면 15:8이 C3라 검산됩니다.

별도 입력 t1=0xFFFFFFF9(−7)을 1비트 오른쪽 이동하면 srli 결과는 0x7FFFFFFC, srai 결과는 0xFFFFFFFC(−4)입니다. M 확장의 div로 −7/2를 계산하면 −3이므로 산술 시프트와 항상 같지는 않습니다.

## 헷갈리기 쉬운 점

논리 연산은 C의 &&·|| 같은 참/거짓 단락 평가와 다릅니다. 왼쪽 시프트의 상위 비트는 버려지며 RV32I 기본 집합에 회전 명령어가 있다고 가정하지 않습니다. sll에서 시프트량 레지스터가 32이면 하위5비트는 0입니다.

## 직접 확인하기

1. s0=0x1234ABCD에서 위 코드의 결과는?
2. ori t0,t0,32의 효과는?
3. −3을 srai로 1비트 이동한 signed 결과는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0xAB입니다. 오른쪽8 이동 후 아래8비트만 남깁니다.</p>
<p>2. 비트5를 1로 만들고 나머지는 유지합니다.</p>
<p>3. −2입니다. −1.5를 음의 무한대 방향으로 내립니다.</p>
</details>

## 다음으로 이어가기

다음 선택 레슨에서는 기본 RV32I 바깥의 곱셈·나눗셈을 구분합니다. 핵심 과정은 레슨7 분기로 이어가도 됩니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.1–6.3.2, 인쇄 pp. 308–310 / PDF pp. 329–331. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
