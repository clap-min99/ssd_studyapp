## 이번 레슨의 목표

S 형식의 분리된 즉시값과 B 형식의 재배열된 분기 변위를 직접 조립·복원합니다.

## 앞에서 배운 내용

레슨17에서 필드 위치를 익혔습니다. 저장은 목적지 레지스터 대신 메모리를 바꾸고 분기는 PC를 바꿉니다.

## S 형식: 저장 데이터는 rs2

S 형식은 instr[31:25]=imm[11:5],instr[24:20]=rs2,instr[19:15]=rs1,instr[14:12]=funct3,instr[11:7]=imm[4:0],instr[6:0]=opcode입니다. SW는 opcode=0x23,funct3=2입니다. `sw x9,12(x8)`에서 rs1=8,rs2=9,imm=12입니다. rd가 없으므로 비트11:7을 목적지로 읽지 않습니다.

## B 형식: 바이트 변위의 비트0은 생략

분기는 opcode=0x63이며 BEQ의 funct3=0,BNE는1입니다. signed13비트 변위 D의 배치는 다음과 같습니다.

| 명령어의 위치 | 담는 변위 비트 |
| --- | --- |
| instr[31] | D[12]: 부호 |
| instr[30:25] | D[10:5] |
| instr[11:8] | D[4:1] |
| instr[7] | D[11] |
| 저장하지 않음 | D[0]=0 |

rs1·rs2·funct3·opcode는 S와 같은 위치입니다. 변위는−4096부터4094까지 짝수입니다. C 없는 이 장의 실제 목표는4바이트 정렬도 만족해야 합니다. 인코딩 가능 범위와 정상 실행 가능한 정렬을 구별합니다.

즉시값이 흩어진 이유는 다른 형식과 레지스터·즉시값 자리 및 부호 위치를 최대한 공유하려는 절충입니다. D를 먼저 완성한 뒤 해당 비트를 골라 넣고, 마지막에 다시 복원합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-18-t c6-18-d">
<title id="c6-18-t">B 형식은 D[11]을 낮은 필드에 두며 비트0은0으로 복원한다.</title>
<desc id="c6-18-d">D12,10:5|31:25 / rs2|24:20 / rs1|19:15 / funct3|14:12 / D4:1,11|11:7 / opcode|6:0</desc>
<rect x="12.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="50.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">D12,10:5</text>
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
<text x="354.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">D4:1,11</text>
<text x="354.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">11:7</text>
<rect x="392.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="430.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">opcode</text>
<text x="430.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">6:0</text>
<text x="15" y="38" font-size="13" fill="var(--ink)">상위 비트 → 하위 비트</text>
</svg>
<p class="diagram-caption">그림 6-18. B 형식은 D[11]을 낮은 필드에 두며 비트0은0으로 복원한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

SW부터 조립합니다. imm12는 상위7비트0,하위5비트12입니다. rs2=9,rs1=8,funct3=2이므로 0x00900000+0x00040000+0x2000+0x600+0x23=0x00942623입니다.

PC=0x220에서0x210으로 가는 `beq x5,x6,L`은 D=−16입니다. 13비트 패턴은8192−16=8176=0x1FF0. D12=1,D11=1,D10:5=63,D4:1=8입니다. instr 상위7비트=0x7F,낮은5비트=0x11,rs2=6,rs1=5를 채우면0xFE6288E3입니다. 복원한0x1FF0에서8192를 빼−16,0x220−16=0x210으로 돌아옵니다.

## 헷갈리기 쉬운 점

분기 변위를 먼저4로 나누지 않습니다. 표가 바이트 변위의 비트를 직접 고릅니다. 저장의 오프셋도 바이트 단위지만 S는12비트 전체를 인코딩하고 B는13비트 중 비트0을 생략합니다.

## 직접 확인하기

1. SW의 비트11:7은 무엇인가요?
2. 0x500에서0x510으로 가는 분기 변위는?
3. 분기 변위+4096은 가능한가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 목적지 레지스터가 아니라 즉시값의 하위5비트입니다.</p>
<p>2. +16바이트입니다. PC+4를 기준으로12라고 계산하면 틀립니다.</p>
<p>3. 아닙니다. signed13비트에서+4096은 양수 범위를 벗어납니다.</p>
</details>

## 다음으로 이어가기

큰 상수와 더 먼 점프에는20비트 즉시값 영역을 가진 U·J 형식을 사용합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.4.3, 인쇄 pp. 336–338 / PDF pp. 357–359. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
