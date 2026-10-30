## 이번 레슨의 목표

opcode로 형식을 고른 뒤 즉시값을 복원하고 주소 지정 방식과 실행 효과를 판별합니다.

## 앞에서 배운 내용

레슨17–19에서 R·I·S·B·U·J 여섯 배치를 만들었습니다. 이번에는 비트열에서 의미를 복원합니다.

## 먼저 형식을 알아야 같은 비트를 올바르게 읽는다

명령어 W의 opcode는 W AND 0x7F,rd는(W>>7) AND31,rs1은(W>>15) AND31,rs2는(W>>20) AND31입니다. 다만 그 형식에 실제로 존재하는 필드만 의미가 있습니다. I의 비트24:20을 rs2로 해석하면 즉시값 일부를 레지스터로 오독합니다.

I는 W[31:20],S는 {W[31:25],W[11:7]},B는 {W[31],W[7],W[30:25],W[11:8],0},J는 {W[31],W[19:12],W[20],W[30:21],0}을 이어 붙인 뒤 정해진 폭으로 부호 해석합니다. U는 {W[31:12],12개의0}입니다. 일반 즉시값의 부호 비트가 instr31에 모여 있어 부호 확장 회로를 공유하기 좋습니다. 시프트 즉시값의 동작 구분 비트는 별도로 해석합니다.

## 형식과 주소 지정 방식은 같은 분류가 아니다

| 방식 | 예 | 읽거나 만드는 대상 |
| --- | --- | --- |
| 레지스터 | add | 레지스터의 값 |
| 즉시값 | addi | 레지스터+명령어 내부 상수 |
| 베이스 주소 | lw·sw | rs1+오프셋의 메모리 |
| PC 상대 | branch·jal·auipc | 현재 PC+변위 또는 상위 즉시값 |

JALR은 베이스 주소 방식으로 다음 PC를 만들지만 메모리 내용을 읽는 명령어는 아닙니다. LW와 ADDI는 같은 I 형식이지만 실행 효과가 다릅니다. 명령어 형식은 비트 배치, 주소 지정 방식은 피연산자·목표를 지정하는 규칙입니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-20-t c6-20-d">
<title id="c6-20-t">분리한 필드를 명령어 의미에 맞춰 해석해야 실행 효과를 알 수 있다.</title>
<desc id="c6-20-d">0xFEC30293|opcode=0x13 / rd=5,rs1=6|imm=0xFEC / ADDI x5,x6,−20|메모리 읽기 없음</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">0xFEC30293</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">opcode=0x13</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">rd=5,rs1=6</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">imm=0xFEC</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">ADDI x5,x6,−20</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">메모리 읽기 없음</text>
</svg>
<p class="diagram-caption">그림 6-20. 분리한 필드를 명령어 의미에 맞춰 해석해야 실행 효과를 알 수 있다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

0xFEC30293을 해독합니다. 하위7비트=0x13이므로 정수 즉시 연산입니다. funct3=0이라 ADDI,rd=5,rs1=6,imm=0xFEC입니다. 최상위가1인12비트 수이므로4076−4096=−20입니다. 따라서 `addi x5,x6,-20`입니다. x6=100이면 x5=80입니다.

0x00942623은 opcode=0x23,funct3=2로 SW입니다. rs1=8,rs2=9,나눈 즉시값을 합치면12입니다. `sw x9,12(x8)`이며 x8=0x600이면 주소0x60C에 x9의 값을 씁니다. 두 명령어 모두 덧셈을 사용하지만 하나는 결과값, 다른 하나는 주소를 만듭니다.

## 헷갈리기 쉬운 점

모르는 opcode를 가장 비슷한 명령어로 추측하지 않습니다. 확장 집합과 유효 funct 필드도 확인해야 합니다. 디스어셈블러가 mv·ret 등 별칭을 출력해도 같은 기계어에 대한 다른 표기일 수 있습니다.

## 직접 확인하기

1. 0xFEC30293의 비트24:20을 rs2로 사용하면 안 되는 이유는?
2. LW가 I 형식이면 반드시 즉시값 덧셈만 하나요?
3. AUIPC는 PC를 목표로 점프시키나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. I 형식에서는 그 위치가 즉시값의 일부이기 때문입니다.</p>
<p>2. 아닙니다. 주소를 계산한 뒤 메모리 워드를 읽습니다.</p>
<p>3. 아닙니다. PC 상대 주소값을 rd에 만들고 다음 명령어로 진행합니다.</p>
</details>

## 다음으로 이어가기

기계어도 메모리에 저장되는 값이라는 관점에서 저장 프로그램과 실행 상태를 정리합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.4.5–6.4.7, 인쇄 pp. 340–343 / PDF pp. 361–364. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
