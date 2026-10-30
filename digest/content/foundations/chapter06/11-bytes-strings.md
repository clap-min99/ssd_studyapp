## 이번 레슨의 목표

LB·LBU·SB의 확장·절단 규칙과 널 종료 문자열의 읽기 경계를 추적합니다.

## 앞에서 배운 내용

레슨10에서 원소 크기를 주소 계산에 반영했습니다. 바이트 배열은 인덱스 자체가 바이트 오프셋입니다.

## 한 바이트를 32비트 레지스터에 넣는 두 방법

`lb`는8비트를 읽어 부호 확장하고 `lbu`는0 확장합니다. `sb`는 레지스터 하위8비트만 저장합니다. 반워드 `lh`·`lhu`·`sh`도16비트에 같은 원리를 적용합니다. 읽는 바이트가0x80이면 lb는0xFFFFFF80, lbu는0x00000080입니다. 주소 계산식은 모두 베이스+signed 바이트 오프셋입니다.

ASCII 문자 'A'는0x41처럼 작은 코드 하나를 한 바이트에 담습니다. C 방식의 문자열은 끝에0x00인 널(null) 바이트를 붙입니다. 문자 '0'의0x30과 종료 바이트0x00은 다릅니다. 한글 같은 일반 텍스트를 ‘문자 하나=바이트 하나’로 가정하지 않습니다. 여기서는 ASCII 바이트만 사용합니다.

## 끝을 만나기 전까지 읽는 반복

다음은 a0가 유효한 널 종료 문자열을 가리킨다는 전제에서 바이트 길이를 t1에 셉니다. 종료 바이트를 포함해 읽을 수 있어야 합니다.

```asm
add  t0, a0, zero
addi t1, zero, 0
str_loop:
lbu  t2, 0(t0)
beq  t2, zero, str_done
addi t1, t1, 1
addi t0, t0, 1
jal  zero, str_loop
str_done:
```

길이는 널 앞의 바이트 수입니다. 이 코드는 최대 길이 제한이 없으므로 종료 문자가 없는 임의 버퍼에 사용할 수 없습니다. 실제 버퍼 처리에서는 길이를 별도로 제한합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-11-t c6-11-d">
<title id="c6-11-t">문자열 길이에는 종료 바이트가 빠지지만 저장 공간과 읽기에는 포함된다.</title>
<desc id="c6-11-d">0x700: &#x27;O&#x27; = 0x4F / 0x701: &#x27;K&#x27; = 0x4B / 0x702: 널 = 0x00 → 종료</desc>
<rect x="75" y="18" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="41" text-anchor="middle" font-size="14" fill="var(--ink)">0x700: &#x27;O&#x27; = 0x4F</text>
<rect x="75" y="56" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="79" text-anchor="middle" font-size="14" fill="var(--ink)">0x701: &#x27;K&#x27; = 0x4B</text>
<rect x="75" y="94" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="117" text-anchor="middle" font-size="14" fill="var(--ink)">0x702: 널 = 0x00 → 종료</text>
</svg>
<p class="diagram-caption">그림 6-11. 문자열 길이에는 종료 바이트가 빠지지만 저장 공간과 읽기에는 포함된다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

주소0x700부터[0x4F,0x4B,0x00]입니다. 첫 반복은 'O'를 읽고 t1=1,t0=0x701. 두 번째는 'K'를 읽고 t1=2,t0=0x702. 세 번째는 널을 읽고 종료합니다. 길이2, 점유3바이트, 읽기3회입니다.

별도로 t3=0x1234ABCD에서 `sb t3,1(a0)`을 실행하면0x701의 한 바이트만0xCD로 바뀝니다. 그곳의 lb 결과는−51인0xFFFFFFCD, lbu는205인0x000000CD입니다. 상위 바이트0x1234AB는 저장하지 않습니다.

## 헷갈리기 쉬운 점

lb와 lbu는 서로 다른 주소를 읽는 것이 아니라 같은 바이트를 확장하는 방법이 다릅니다. ASCII 소문자에서32를 빼는 변환은 입력이 'a'부터'z'인 경우에만 적용해야 하며 임의 문자나 널에 일괄 적용하면 안 됩니다.

## 직접 확인하기

1. 빈 문자열의 점유 공간과 예제의 읽기 횟수는?
2. 0xF0을 lb·lbu로 읽으면?
3. sb로0x100을 저장하면 그 바이트는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 널 한 바이트와 읽기1회입니다. 길이는0입니다.</p>
<p>2. lb는−16인0xFFFFFFF0, lbu는240입니다.</p>
<p>3. 하위8비트0x00입니다. 문자열 중간이면 종료 바이트가 될 수 있습니다.</p>
</details>

## 다음으로 이어가기

반복 코드를 재사용하려면 인자·결과·돌아갈 주소를 정한 함수 호출 규칙이 필요합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.3.6, 인쇄 pp. 317–319 / PDF pp. 338–340. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
