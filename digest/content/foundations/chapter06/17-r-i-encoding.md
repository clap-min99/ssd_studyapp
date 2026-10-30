## 이번 레슨의 목표

R·I 형식의 각 필드를 채워 기계어를 만들고 음수 즉시값의12비트 패턴을 검산합니다.

## 앞에서 배운 내용

레슨2의 레지스터 번호와 레슨3의 부호 확장을 사용합니다. 별칭보다 x번호로 바꾸면 인코딩이 분명해집니다.

## R 형식: 레지스터 셋과 연산 선택

명령어 비트는 오른쪽부터0번입니다. R 형식은 비트31:25 funct7,24:20 rs2,19:15 rs1,14:12 funct3,11:7 rd,6:0 opcode입니다. 폭의 합은7+5+5+3+5+7=32입니다. 레지스터32개를 고르려면5비트가 필요합니다.

ADD는 opcode=0x33,funct3=0,funct7=0입니다. SUB는 같은 opcode·funct3에 funct7=0x20을 씁니다. opcode만 보고 ADD인지 SUB인지 정할 수 없습니다. 조립식은 `(funct7<<25)|(rs2<<20)|(rs1<<15)|(funct3<<12)|(rd<<7)|opcode`입니다. 각 필드의 자리가 겹치지 않으므로 OR로 합칩니다.

## I 형식: 한 소스와 즉시값

I 형식은 비트31:20에 imm[11:0]를 넣고 나머지 rs1·funct3·rd·opcode 자리는 유지합니다. ADDI는 opcode=0x13,funct3=0입니다. LW는 opcode=0x03,funct3=2이며, 같은 I 형식이어도 메모리 읽기를 수행합니다.

일반 I 즉시값은12비트 2의 보수입니다. 음수−20의 패턴은4096−20=4076=0xFEC입니다. 시프트 즉시 명령어는 예외로 상위7비트가 동작 구분, 아래5비트가 시프트량입니다. srai에서 상위7비트를 음수 상수의 일부로 읽으면 안 됩니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-17-t c6-17-d">
<title id="c6-17-t">R 형식의 필드 순서와 폭: ADD·SUB는 funct7로도 구분한다.</title>
<desc id="c6-17-d">funct7|31:25 / rs2|24:20 / rs1|19:15 / funct3|14:12 / rd|11:7 / opcode|6:0</desc>
<rect x="12.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="50.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">funct7</text>
<text x="50.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">31:25</text>
<rect x="88.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="126.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">rs2</text>
<text x="126.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">24:20</text>
<rect x="164.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="202.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">rs1</text>
<text x="202.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">19:15</text>
<rect x="240.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="278.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">funct3</text>
<text x="278.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">14:12</text>
<rect x="316.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="354.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">rd</text>
<text x="354.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">11:7</text>
<rect x="392.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="430.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">opcode</text>
<text x="430.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">6:0</text>
<text x="15" y="38" font-size="13" fill="var(--ink)">상위 비트 → 하위 비트</text>
</svg>
<p class="diagram-caption">그림 6-17. R 형식의 필드 순서와 폭: ADD·SUB는 funct7로도 구분한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

`add x10,x11,x12`를 조립합니다. rd=10,rs1=11,rs2=12입니다. 각 항은0x00C00000,0x00058000,0x00000500,0x33이므로 OR 결과는0x00C58533입니다. SUB로 바꾸면0x20<<25=0x40000000을 추가해0x40C58533입니다.

`addi x5,x6,-20`은 imm=0xFEC,rs1=6,rd=5입니다. (0xFEC<<20)=0xFEC00000, (6<<15)=0x30000, (5<<7)=0x280, opcode=0x13을 합쳐0xFEC30293입니다. 비트31:20을 꺼내0xFEC−4096=−20으로 돌아오는지 검산합니다.

## 헷갈리기 쉬운 점

기계어의 왼쪽부터 어셈블리 피연산자 순서대로 채우면 틀립니다. rd는 어셈블리에서 먼저 나오지만 비트11:7입니다. 기계어0x00C58533이라는 워드 표기와 메모리에 저장할 바이트 순서는 별도 문제입니다.

## 직접 확인하기

1. 레지스터 번호31의5비트 패턴은?
2. ADDI 즉시값−1의12비트 패턴은?
3. ADD와 SUB 인코딩은 어떤 비트가 다른가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 11111입니다. 32는 이 필드에 들어가지 않습니다.</p>
<p>2. 0xFFF입니다. 실행 때32비트로 부호 확장합니다.</p>
<p>3. 이 두 연산은 funct7의0과0x20 차이로 명령어 비트30이 다릅니다.</p>
</details>

## 다음으로 이어가기

저장과 분기는 두 레지스터가 모두 소스라 rd 자리를 즉시값에 재사용합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.4.1–6.4.2, 인쇄 pp. 332–336 / PDF pp. 353–357. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
