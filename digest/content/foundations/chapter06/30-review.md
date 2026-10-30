## 이번 레슨의 목표

배열을 읽는 함수의 실행을 PC·레지스터·메모리 변화로 검산하고7장 데이터 경로의 요구를 도출합니다.

## 앞에서 배운 내용

핵심 레슨1–5,7–21의 산술·메모리·분기·함수·인코딩을 함께 사용합니다. 선택 심화6,22–27,29는 필요할 때 돌아갑니다.

## 먼저 함수의 계약을 적는다

자체 함수 sum_words는 a0=4바이트 정렬된32비트 워드 배열 베이스,a1=작은 비음수 길이를 받아 a0에 합의 하위32비트를 반환합니다. 지정한 원소를 모두 읽을 수 있고 주소 계산이 유효하다고 가정합니다. 메모리와 s0–s11·sp를 바꾸지 않는 리프 함수입니다. 임시 레지스터는 보존하지 않습니다.

```asm
sum_words:
addi t0, zero, 0
addi t1, zero, 0
review_loop:
bge  t1, a1, review_done
slli t2, t1, 2
add  t2, a0, t2
lw   t3, 0(t2)
add  t0, t0, t3
addi t1, t1, 1
jal  zero, review_loop
review_done:
add  a0, t0, zero
jalr zero, 0(ra)
```

베이스 a0를 반복 중에 합으로 덮지 않는 이유는 다음 원소 주소에 계속 필요하기 때문입니다. 합을 t0에 모으고 읽기가 끝난 뒤에만 a0로 옮깁니다. 이 함수는 다른 함수를 부르지 않고 s 레지스터를 수정하지 않아 스택 프레임이 필요 없습니다.

## 프로그램의 약속을 회로의 일로 바꾸기

명령어 비트에서 rs1·rs2·rd를 골라 레지스터 파일을 읽고, 즉시값을 복원하고, ALU로 합이나 주소를 계산하며, 메모리 또는 레지스터에 결과를 씁니다. 분기에서는 비교 결과에 따라 PC+4와 목표를 고릅니다. 이것이7장에서 구현할 데이터 경로·제어의 요구입니다. 이 장은 내부 클록 수를 아직 정하지 않았습니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-30-t c6-30-d">
<title id="c6-30-t">같은 ALU 덧셈도 주소 계산과 값 누적에 서로 다르게 사용된다.</title>
<desc id="c6-30-d">t2 ← base+4i|주소 만들기 / t3 ← Mem[t2]|원소 읽기 / t0 ← t0+t3|합 누적</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">t2 ← base+4i</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">주소 만들기</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">t3 ← Mem[t2]</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">원소 읽기</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">t0 ← t0+t3</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">합 누적</text>
</svg>
<p class="diagram-caption">그림 6-30. 같은 ALU 덧셈도 주소 계산과 값 누적에 서로 다르게 사용된다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

a0=0xA00,a1=3,ra=0x184이고 세 워드는[4,−2,9]입니다. 주소열은0xA00,0xA04,0xA08,합 패턴은4→2→11입니다. 검사 시점 i=3에서 읽기를 끝내 a0=11로 옮기고0x184로 복귀합니다. 길이3의 분기 검사는4회이고 메모리 읽기는3회입니다. 입력 메모리는 유지됩니다.

길이0이면 LW를 한 번도 실행하지 않고 a0=0을 반환합니다. 마지막 a0은 원래 베이스가 아니라 반환값입니다. 호출자가 나중에 베이스를 다시 사용하려면 별도 위치에 보존해야 합니다. 합에 큰 값을 넣어 범위를 넘기면 계약대로 하위32비트를 반환하며 signed 오류 처리가 추가되지는 않습니다.

## 헷갈리기 쉬운 점

기능이 맞는 명령어열과 빠른 회로는 같은 검증 항목이 아닙니다.7장에서는 제어 신호·클록·메모리 지연을 추가로 정합니다.7장 콘텐츠는 아직 앱에 추가하지 않았습니다. 원문 연습문제·면접 질문 전체 풀이는 이 장 범위에 포함하지 않습니다.

## 직접 확인하기

1. 핵심: 네 번째 워드 A[3]의 주소는? (레슨4·10)
2. 핵심: 이 함수가 ra를 스택에 저장하지 않아도 되는 이유는? (레슨12–14)
3. 핵심: 기계어 opcode만 보고 모든 필드를 해석해도 되나요? (레슨17–20)
4. 핵심 적용: 베이스 a0를 매 반복 합으로 덮으면? (레슨10·21)
5. 선택: 메모리[0xA04]의−2 패턴을 little-endian으로 쓰면? (레슨24)
6. 선택: 일반32비트 명령어 세 개를 모두 압축할 수 있다고 가정하면 크기는? (레슨27)

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0xA0C입니다. 베이스0xA00에12바이트를 더합니다.</p>
<p>2. 다른 함수를 호출하거나 ra를 덮지 않는 리프 함수이므로 들어온 복귀 주소를 그대로 사용할 수 있습니다.</p>
<p>3. opcode로 형식을 고른 뒤 funct 필드 등으로 정확한 연산을 정해야 합니다.</p>
<p>4. 다음 주소 계산의 베이스를 잃습니다. 주소용 값과 누적값의 생존 구간이 겹치므로 분리해야 합니다.</p>
<p>5. 0xFE,0xFF,0xFF,0xFF 순입니다.</p>
<p>6. 12바이트에서6바이트입니다. 실제 압축 가능 여부는 명령어·레지스터·즉시값 제약을 확인해야 합니다.</p>
</details>

## 다음으로 이어가기

7장 마이크로아키텍처에서는 이 ISA의 상태 변화가 실제 레지스터·ALU·메모리·MUX·제어 회로에서 어떻게 발생하는지 설계합니다. 막히는 부분은 문제 옆 레슨으로 돌아가 다시 추적합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.9 및 6.1–6.8 종합, 인쇄 pp. 299–374 / PDF pp. 320–395. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
