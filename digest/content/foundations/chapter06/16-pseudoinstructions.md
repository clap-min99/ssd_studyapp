## 이번 레슨의 목표

의사명령어의 확장을 설명하고 소스 줄 수와 실행 명령어 수가 달라지는 이유를 계산합니다.

## 앞에서 배운 내용

레슨12의 ret는 jalr, 레슨3의 큰 상수는 lui와 addi로 구현할 수 있었습니다.

## 편한 이름이 독립된 명령어라는 뜻은 아니다

의사명령어(pseudoinstruction)는 어셈블러가 실제 명령어 하나 이상으로 바꾸는 표기입니다. 기본 ISA에 별도의 mv 연산 회로가 있어야 한다는 뜻은 아닙니다.

| 표기 예 | 기본 명령어의 한 구현 |
| --- | --- |
| mv t0,t1 | addi t0,t1,0 |
| not t0,t1 | xori t0,t1,-1 |
| nop | addi zero,zero,0 |
| j L | jal zero,L |
| ret | jalr zero,0(ra) |
| bgt t0,t1,L | blt t1,t0,L |

`li t0,7`은 addi 하나로 가능하지만 큰 상수는 lui·addi 조합이 필요할 수 있습니다. `la`는 심볼의 주소를 구성하고 `lw`는 그 주소의 내용을 읽습니다. 둘을 교환할 수 없습니다.

## 멀리 있는 함수 호출

`call symbol`은 보통 AUIPC·JALR 조합과 재배치 정보를 사용하여 목표 주소를 만듭니다. AUIPC는 그 명령어의 PC에 상위 즉시값을 더합니다. 최종 배치에서 가까운 호출이면 링커가 JAL 하나로 줄일 수도 있습니다. 따라서 소스의 한 줄을 무조건4바이트로 세지 말고 최종 기계어를 확인합니다. 코드 크기 변화는 뒤의 레이블 주소에도 영향을 줍니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-16-t c6-16-d">
<title id="c6-16-t">같은 LI 표기도 상수 크기에 따라 명령어 수가 달라진다.</title>
<desc id="c6-16-d">li t0,7|1개 ADDI / li t1,0x12345ABC|LUI + ADDI / C 확장 없음|총12바이트</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">li t0,7</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">1개 ADDI</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">li t1,0x12345ABC</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">LUI + ADDI</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">C 확장 없음</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">총12바이트</text>
</svg>
<p class="diagram-caption">그림 6-16. 같은 LI 표기도 상수 크기에 따라 명령어 수가 달라진다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

C 확장·링커 완화를 끈 교육 모델에서 `li t0,7`, `li t1,0x12345ABC`, `mv t2,t0`, `ret`를 차례로 셉니다. 각각1+2+1+1=5개 명령어,20바이트입니다. 큰 li는 레슨3의 U=0x12346,low=−1348로 구성합니다.

명시적 원거리 호출도 계산해 봅니다. PC=0x1000에서 `auipc ra,2`면 ra=0x3000입니다. 다음0x1004의 `jalr ra,32(ra)`는 옛 ra를 사용해0x3020으로 가고 새 ra=0x1008을 저장합니다. 목표 계산용 ra와 링크로 갱신한 ra를 구별합니다.

## 헷갈리기 쉬운 점

nop은 아무 명령어도 없다는 뜻이 아닙니다. 정상 실행하면 PC가 진행합니다. nop 한 개의 시간이 언제나 일정하다고 가정해 정밀 지연을 만들지 않습니다. 의사명령어 확장과 최적화는 도구·ISA 옵션·링크 결과에 따라 달라질 수 있습니다.

## 직접 확인하기

1. mv가 원래 소스 값을 지우나요?
2. bgt a0,a1,L을 blt로 바꾸면?
3. la t0,A와 lw t0,0(t1)의 차이는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 아닙니다. addi의0 덧셈으로 목적지에 복사하며 소스를 유지합니다.</p>
<p>2. blt a1,a0,L입니다. 소스 순서를 뒤집습니다.</p>
<p>3. la는 A의 주소, lw는 t1이 가리키는 메모리의 워드 내용을 얻습니다.</p>
</details>

## 다음으로 이어가기

이제 실제 명령어의32비트 안에 연산·레지스터·즉시값을 어떻게 담는지 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.8, 인쇄 pp. 330–332 / PDF pp. 351–353. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
