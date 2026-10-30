## 이번 레슨의 목표

[선택 심화] F 확장의 데이터 해석과 C 확장의 명령어 길이가 서로 다른 확장 축임을 설명합니다.

## 앞에서 배운 내용

5장 binary32 표현과 레슨7의 PC 진행을 사용합니다. 기본 RV32I에서 추가한 기능을 분명히 표시합니다.

## F: 실수 값을 다루는 별도 연산

전통적인 F 확장은32개의 부동소수점 레지스터 f0–f31과 binary32 연산을 제공합니다. x0–x31과 별도입니다. FLW는32비트 패턴을 부동소수점 레지스터에 적재하고 FADD.S는 그 패턴을 binary32로 해석해 더합니다. 정수 ADD를 같은 비트에 적용하는 것과 다릅니다. f0은 정수 x0처럼 상수0 레지스터가 아닙니다.

```asm
# F 확장 가정, a0는 float 두 개의 정렬된 베이스
flw    ft0, 0(a0)
flw    ft1, 4(a0)
fadd.s ft2, ft0, ft1
fsw    ft2, 8(a0)
```

D·Q는 각각 더 넓은 정밀도 연산을 위한 확장입니다. 부동소수점 값 전달 규약도 선택한 ABI와 맞아야 합니다. 숫자를 정수에서 실수로 바꾸는 변환과 단순 비트 복사는 같은 작업이 아닙니다.

## C: 연산 데이터는 유지하면서 명령어를 짧게

C 확장은 흔한 명령어를16비트로 표현합니다. RV32에서 `c.addi`가 짧다고16비트 정수만 계산하는 것이 아닙니다. 여전히32비트 정수 레지스터를 사용합니다. 짧은 즉시값,암묵적인 피연산자,일부 형식의 제한된 레지스터 집합으로 크기를 줄입니다. 모든 명령어를 압축할 수 있는 것은 아닙니다.

16비트와32비트가 섞이면 순차 PC는 현재 명령어 길이에 따라2 또는4 증가합니다. 명령어 시작 정렬은2바이트가 가능합니다. 기본 JAL의 링크 PC+4를 무조건 PC+2로 바꾸는 것은 아닙니다. 실제16비트 호출 명령어는 자기 길이에 맞는 링크를 사용합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-27-t c6-27-d">
<title id="c6-27-t">C 확장을 허용한 혼합 길이 코드에서는 시작 주소가2 또는4씩 증가한다.</title>
<desc id="c6-27-d">0x100: c.addi s0,1 (2바이트) / 0x102: add a0,a1,a2 (4바이트) / 0x106: c.addi s1,1 (2바이트) / 다음 PC=0x108</desc>
<rect x="75" y="18" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="41" text-anchor="middle" font-size="14" fill="var(--ink)">0x100: c.addi s0,1 (2바이트)</text>
<rect x="75" y="56" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="79" text-anchor="middle" font-size="14" fill="var(--ink)">0x102: add a0,a1,a2 (4바이트)</text>
<rect x="75" y="94" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="117" text-anchor="middle" font-size="14" fill="var(--ink)">0x106: c.addi s1,1 (2바이트)</text>
<rect x="75" y="132" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="155" text-anchor="middle" font-size="14" fill="var(--ink)">다음 PC=0x108</text>
</svg>
<p class="diagram-caption">그림 6-27. C 확장을 허용한 혼합 길이 코드에서는 시작 주소가2 또는4씩 증가한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

F 예제에서 두 입력이1.5와2.25면 결과는3.75입니다. binary32 비트는 각각0x3FC00000,0x40100000,0x40700000입니다. 비트 패턴끼리 정수 ADD한0x7FD00000은 실수 덧셈 결과가 아닙니다. FLW는 비트 이동,FADD.S는 실수 연산 역할입니다.

C 예제의 코드 길이는2+4+2=8바이트입니다. 모두 기본32비트로 표현하면12바이트여서4바이트를 줄였습니다. 이 예의 절약률은4/12=1/3입니다. 저장 크기가 줄었다고 실행 시간이 같은 비율로 줄었다고 결론 내리지는 않습니다.

## 헷갈리기 쉬운 점

C 확장을 지원하지 않는 프로세서에 압축 코드를 그대로 주면 호환되지 않습니다. F를 지원한다고 모든 부동소수점 ABI가 자동 호환되는 것도 아닙니다. 부동소수점 반올림·예외 플래그·NaN 세부 동작은 여기서 전체 구현하지 않습니다.

## 직접 확인하기

1. f0에 값을 쓰면 버려지나요?
2. RV32의16비트 압축 명령어가 쓰는 정수 레지스터 폭은?
3. PC=0x102의 일반32비트 JAL의 링크는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 아닙니다. 상수0인 것은 정수 x0입니다.</p>
<p>2. 32비트입니다. 명령어 길이와 데이터 폭은 별개입니다.</p>
<p>3. 0x106입니다. C를 허용해도 그 JAL 자체는4바이트입니다.</p>
</details>

## 다음으로 이어가기

확장을 조합할 때의 호환성 조건과 다른 ISA의 설계 선택을 비교합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.6.4–6.6.5, 인쇄 pp. 361–363 / PDF pp. 382–384. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
