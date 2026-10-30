## 이번 레슨의 목표

바이트 주소·워드 번호·실효 주소·저장값을 구별하고 LW·SW의 효과를 추적합니다.

## 앞에서 배운 내용

5장 메모리는 주소로 워드를 선택했습니다. RV32I 프로그램의 주소 단위는 바이트라는 약속을 추가합니다.

## 주소는 장소이고 값은 그곳의 내용이다

RV32I는 바이트 주소 지정(byte addressing)을 사용합니다. 주소 1 증가는 8비트 한 칸 이동입니다. 32비트 워드는 4바이트이므로 연속 워드의 시작 주소는 4씩 증가합니다. 32비트 주소 공간은 2³²바이트=4GiB이지만 모든 주소에 실제 RAM이 있다는 뜻은 아닙니다.

`lw rd,offset(rs1)`은 실효 주소(effective address) EA=R[rs1]+sign_extend(offset)의 32비트 워드를 rd로 읽습니다. `sw rs2,offset(rs1)`는 같은 방식의 주소에 rs2의 하위32비트를 씁니다. offset은 바이트 단위의 12비트 signed 값입니다. 산술 명령어는 레지스터에서 계산하고 메모리 접근은 load·store로 분리합니다.

```asm
lw   t0, 8(s0)
addi t0, t0, 7
sw   t0, 12(s0)
```

이 코드는 주소를 레지스터에 복사하는 것이 아닙니다. s0+8에 있던 값을 가져와 7을 더하고 다른 주소 s0+12에 저장합니다. s0은 변하지 않습니다. 이번 장은 워드 접근을 4바이트 경계에 정렬하는 모델입니다. 정렬되지 않은 접근 지원과 예외 처리는 실행 환경에 따라 다릅니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-4-t c6-4-d">
<title id="c6-4-t">s0=0x200일 때 명령어의 오프셋은 워드 번호가 아닌 바이트 수다.</title>
<desc id="c6-4-d">0x200: A[0] = 11 / 0x204: A[1] = 22 / 0x208: A[2] = 30 → 읽기 / 0x20C: A[3] ← 37 쓰기</desc>
<rect x="75" y="18" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="41" text-anchor="middle" font-size="14" fill="var(--ink)">0x200: A[0] = 11</text>
<rect x="75" y="56" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="79" text-anchor="middle" font-size="14" fill="var(--ink)">0x204: A[1] = 22</text>
<rect x="75" y="94" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="117" text-anchor="middle" font-size="14" fill="var(--ink)">0x208: A[2] = 30 → 읽기</text>
<rect x="75" y="132" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="155" text-anchor="middle" font-size="14" fill="var(--ink)">0x20C: A[3] ← 37 쓰기</text>
</svg>
<p class="diagram-caption">그림 6-4. s0=0x200일 때 명령어의 오프셋은 워드 번호가 아닌 바이트 수다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

초기 s0=0x200, 메모리 워드 [0x208]=30, [0x20C]=90입니다. lw의 EA는 0x200+8=0x208이므로 t0=30입니다. addi 뒤 t0=37, sw의 EA는 0x200+12=0x20C이므로 그 워드가 37로 바뀝니다. [0x208]은 여전히 30입니다.

반대로 s0=0x210에서 `lw t1,-8(s0)`도 EA=0x208이므로 30을 가져옵니다. 정렬 검산은 0x208 mod 4=0입니다. offset 2였다면 EA=0x212로 이 장의 정렬 조건을 어깁니다.

## 헷갈리기 쉬운 점

sw의 첫 레지스터는 목적지 레지스터가 아니라 저장할 데이터의 소스입니다. lw·sw는 베이스 포인터를 자동 증가시키지 않습니다. 워드의 바이트 순서는 레슨24에서 따로 설명하며 이 장은 little-endian을 사용합니다.

## 직접 확인하기

1. s0=0x300에서 5번째 인덱스 워드 A[5]의 주소는?
2. sw t0,4(s0) 뒤 s0은?
3. lw t0,0(s0)에서 t0이 주소인지 값인지 어떻게 아나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0x300+5×4=0x314입니다. A[0]부터 셉니다.</p>
<p>2. 원래 값입니다. 주소 계산에 읽었을 뿐 쓰지 않았습니다.</p>
<p>3. lw의 의미가 메모리 내용을 적재하므로 값입니다. 주소 자체는 s0에 있습니다.</p>
</details>

## 다음으로 이어가기

읽어 온 데이터에서 일부 비트만 꺼내려면 논리·시프트 명령어를 조합합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.2.2, 인쇄 pp. 306–308 / PDF pp. 327–329. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
