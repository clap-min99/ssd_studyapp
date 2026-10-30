## 이번 레슨의 목표

현재 PC를 기준으로 분기 목표를 구하고 조건 충족·불충족의 다음 PC를 추적합니다.

## 앞에서 배운 내용

레슨1의 기본 명령어는4바이트, 레슨5의 비교 대상은32비트 레지스터입니다. 이제 다음 주소를 고릅니다.

## 순차 실행과 조건부 이동

프로그램 카운터(program counter, PC)는 현재 명령어의 주소입니다. 이 장의 RV32I 일반 명령어는 정상 완료 뒤 PC+4로 진행합니다. 조건부 분기(branch)는 두 소스를 비교하여 참이면 PC+signed 변위, 거짓이면 PC+4로 갑니다. 변위는 분기 명령어 자체의 주소를 기준으로 한 바이트 거리입니다.

| 명령어 | 분기 조건 |
| --- | --- |
| beq / bne | 두 패턴이 같음 / 다름 |
| blt / bge | signed로 작음 / 크거나 같음 |
| bltu / bgeu | unsigned로 작음 / 크거나 같음 |

`beq s0,s1,match`에서 match는 레이블(label)입니다. 레이블이 가리키는 명령어 주소를 어셈블러가 알아내어 변위로 바꿉니다. 레이블 자체는 실행할 명령어가 아니며 바이트도 소비하지 않습니다. RV32I에는 분기 지연 슬롯이 없습니다. 분기가 선택되면 바로 목표의 명령어를 실행합니다.

무조건 점프 `jal zero,target`은 조건 없이 목표로 가고 복귀 주소 쓰기를 x0에 버립니다. 흔히 `j target`으로 씁니다. `jal ra,target`은 복귀 주소도 저장하므로 함수 호출에서 다시 다룹니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-7-t c6-7-d">
<title id="c6-7-t">PC=0x408에서 같은 값이면 목표로, 다르면 다음 명령어로 간다.</title>
<desc id="c6-7-d">beq s0,s1,L|PC=0x408 / 같음: +16|다름: +4 / 0x418 또는|0x40C 실행</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">beq s0,s1,L</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">PC=0x408</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">같음: +16</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">다름: +4</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">0x418 또는</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">0x40C 실행</text>
</svg>
<p class="diagram-caption">그림 6-7. PC=0x408에서 같은 값이면 목표로, 다르면 다음 명령어로 간다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

분기 주소는0x408, L은0x418입니다. 변위=0x418−0x408=0x10=16바이트입니다. s0=s1=7이면 다음 PC=0x418입니다. s1=8로 바꾸면 다음 PC=0x40C입니다. 어느 경우든 분기 명령어가 s0·s1을 수정하지는 않습니다.

반복을 위해 PC=0x420에서0x400으로 이동하면 변위는−0x20=−32입니다. ‘앞으로 몇 줄’ 대신 두 주소를 빼면 역방향에서도 같은 계산을 사용합니다.

## 헷갈리기 쉬운 점

PC+4는 복귀 주소나 분기 미선택 시의 다음 주소입니다. 분기 선택 시 기준 PC와 혼동하지 않습니다. 두 레지스터의 뺄셈 결과를 영구 플래그에 저장하고 다음 분기가 읽는 모델도 아닙니다.

## 직접 확인하기

1. 0x100의 bne가0x0F0으로 가는 변위는?
2. 분기를 선택하지 않았을 때 다음 PC는?
3. 0xFFFFFFFF와0을 blt·bltu로 비교하면?

<details>
<summary>정답과 해설 보기</summary>
<p>1. −16바이트입니다.</p>
<p>2. 기본32비트 명령어이므로 현재 PC+4입니다.</p>
<p>3. blt는 −1&lt;0으로 참, bltu는 4294967295&lt;0이 거짓입니다.</p>
</details>

## 다음으로 이어가기

이 분기들을 조합해 고급 언어의 if·else를 구현합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.1, 6.3.3, 인쇄 pp. 308, 311–313 / PDF pp. 329, 332–334. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
