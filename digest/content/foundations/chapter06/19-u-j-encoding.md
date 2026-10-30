## 이번 레슨의 목표

U·J 형식의 즉시값 배치를 계산하고 JAL의 목표 변위와 링크 주소를 구별합니다.

## 앞에서 배운 내용

레슨3의 LUI, 레슨12의 JAL을 실제 비트 형식으로 연결합니다. B와 마찬가지로 J도 비트0을 생략합니다.

## U 형식: 상위20비트를 직접 지정

U 형식은 instr[31:12]에20비트 U,11:7에 rd,6:0에 opcode를 둡니다. LUI의 opcode는0x37,AUIPC는0x17입니다. LUI 결과는 U<<12,AUIPC 결과는 그 명령어의 PC+(U<<12)의 하위32비트입니다. AUIPC 자체는 PC를 점프시키지 않습니다.

## J 형식: 점프 거리21비트

JAL은 opcode=0x6F,rd=링크 목적지입니다. signed21비트 바이트 변위 D는 아래처럼 저장합니다.

| 명령어 위치 | 담는 비트 |
| --- | --- |
| instr[31] | D[20]: 부호 |
| instr[30:21] | D[10:1] |
| instr[20] | D[11] |
| instr[19:12] | D[19:12] |
| 저장하지 않음 | D[0]=0 |

변위 범위는−1048576부터1048574까지의 짝수입니다. 실행 목표는 현재 PC+D이고 링크는 현재 PC+4입니다. rd=zero면 같은 J 인코딩으로 링크만 버립니다. JALR은 이름이 비슷해도 I 형식이고 목표는 레지스터+12비트 오프셋입니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-19-t c6-19-d">
<title id="c6-19-t">JAL의 변위 비트 순서와 목적지 위치를 표시한다.</title>
<desc id="c6-19-d">D20|31 / D10:1|30:21 / D11|20 / D19:12|19:12 / rd|11:7 / 0x6F|6:0</desc>
<rect x="12.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="50.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">D20</text>
<text x="50.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">31</text>
<rect x="88.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="126.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">D10:1</text>
<text x="126.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">30:21</text>
<rect x="164.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="202.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">D11</text>
<text x="202.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">20</text>
<rect x="240.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="278.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">D19:12</text>
<text x="278.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">19:12</text>
<rect x="316.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="354.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">rd</text>
<text x="354.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">11:7</text>
<rect x="392.0" y="55" width="76.0" height="65" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="430.0" y="79" text-anchor="middle" font-size="13" fill="var(--ink)">0x6F</text>
<text x="430.0" y="100" text-anchor="middle" font-size="13" fill="var(--ink)">6:0</text>
<text x="15" y="38" font-size="13" fill="var(--ink)">상위 비트 → 하위 비트</text>
</svg>
<p class="diagram-caption">그림 6-19. JAL의 변위 비트 순서와 목적지 위치를 표시한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

`lui x5,0x2468A`는0x2468A000|(5<<7)|0x37=0x2468A2B7입니다. 실행 뒤 x5=0x2468A000이며 인코딩 끝의0x2B7은 결과값 일부가 아닙니다.

PC=0x100에서0x114로 `jal ra,L`을 조립합니다. D=20=0x14, D10:1=10이며 나머지 변위 필드는0입니다. (10<<21)|(1<<7)|0x6F=0x014000EF입니다. 실행하면 PC=0x114,ra=0x104입니다. 같은 변위에 rd=0이면0x0140006F로, 목표는 같고 링크가 저장되지 않습니다.

## 헷갈리기 쉬운 점

U 형식에 쓴0x2468A는 실행 때12비트 이동하므로 결과를0x0002468A로 읽지 않습니다. JAL의 저장하지 않는 비트0을 복원한 뒤 추가로2배하면 변위를 두 번 이동한 오류입니다.

## 직접 확인하기

1. PC=0x800에서 auipc x5,1의 결과는?
2. 0x200에서0x1F0으로 JAL하면 변위와 링크는?
3. JALR도21비트 PC 상대 변위를 쓰나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. x5=0x1800입니다. PC는 정상적으로0x804로 진행합니다.</p>
<p>2. 변위−16, rd에 쓰는 링크는0x204입니다.</p>
<p>3. 아닙니다. I 형식의12비트 signed 오프셋과 레지스터를 씁니다.</p>
</details>

## 다음으로 이어가기

이제 기계어를 거꾸로 읽고 각 명령어가 어떤 주소 계산을 하는지 연결합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.4.4–6.4.5, 인쇄 pp. 338–341 / PDF pp. 359–362. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
