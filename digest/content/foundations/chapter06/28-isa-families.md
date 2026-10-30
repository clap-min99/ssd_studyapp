## 이번 레슨의 목표

기본 ISA·선택 확장·ABI·실행 환경을 구별하고 다른 RISC 계열의 비교 범위를 설명합니다.

## 앞에서 배운 내용

레슨6·27의 M·F·C는 기본 집합에 추가되는 기능이었습니다. ‘RISC-V용 프로그램’이라는 표현만으로 충분한지 살펴봅니다.

## 같은 계열 이름보다 필요한 기능을 확인하기

RV32I는32비트 정수 기본 집합이고 RV64I는64비트 정수 기본 집합입니다. RV32E는 적은 정수 레지스터를 사용하는 별도 기본 집합입니다. M은 정수 곱셈·나눗셈,F·D는 부동소수점,C는 압축,A는 원자적 연산을 위한 대표 확장입니다. 이름이 같아도 바이너리가 요구하는 집합과 구현이 제공하는 집합이 맞아야 합니다.

프로그램이 RV32IMC를 요구하면 RV32I만 있는 프로세서에서 그대로 실행할 수 있다고 보장할 수 없습니다. ISA 기능을 만족해도 인자 전달·데이터 크기·실행 파일 형식·시스템 호출·메모리 맵 등 실행 환경이 맞아야 합니다. 호환성은 명령어 해독 하나로 끝나지 않습니다.

책의 §6.7은 집필 당시 확장 개발 상태도 설명합니다. 이 레슨은 그 과거 상태표를 현재 승인 현황으로 재사용하지 않습니다. 여기서는 기본 집합과 확장을 나눈 설계 원리만 학습하며 실무 대상은 해당 구현과 명세 버전으로 확인합니다.

## MIPS·ARM 비교는 버전까지 명시하기

고전 MIPS의 일부 모델은 분기 기준PC+4와 지연 슬롯을 사용했습니다. 이 장 RV32I의 분기는 현재 PC 기준이며 지연 슬롯이 없습니다. MIPS에서 외운 주소 계산을 그대로 옮기지 않습니다.

책이 비교한 고전32비트 ARM은 조건 실행·이동된 소스 피연산자·복잡한 주소 지정으로 코드 크기를 줄이는 선택을 보여 줍니다. 이런 특징을 모든 ARM 버전과 AArch64 전체에 일괄 적용하지 않습니다. 비교의 목적은 어느 계열이 무조건 빠른지 순위를 매기는 것이 아니라 같은 기능을 어떤 상태·형식·명령어열로 표현하는지 살피는 것입니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-28-t c6-28-d">
<title id="c6-28-t">실행 호환성은 명령어 집합에서 호출 규약과 환경까지 확인한다.</title>
<desc id="c6-28-d">ISA 기능|RV32I + M + C / ABI|레지스터·자료 크기 / 실행 환경|OS·주소·진입점</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">ISA 기능</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">RV32I + M + C</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">ABI</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">레지스터·자료 크기</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">실행 환경</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">OS·주소·진입점</text>
</svg>
<p class="diagram-caption">그림 6-28. 실행 호환성은 명령어 집합에서 호출 규약과 환경까지 확인한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

프로그램 P는 정수 ADDI·LW·SW만 사용하고, Q는 MUL과16비트 압축 명령어도 사용한다고 합시다. 두 프로그램 모두 같은 ILP32 ABI·환경을 전제하면 RV32IMC 구현은 두 명령어 요구를 충족합니다. RV32I 구현은 P의 명령어는 실행할 수 있지만 Q의 기능은 부족합니다.

반대로 RV32IMC라는 이름만 같아도 P가 특정 OS의 ecall 번호와 로더를 요구하고 대상이 bare-metal이면 그대로 실행된다고 말할 수 없습니다. 지원 명령어 목록과 시작·서비스 계약을 따로 점검합니다.

## 헷갈리기 쉬운 점

책의 RV128 관련 전망이나 확장 개발 중 표시를 오늘의 모든 구현 상태로 단정하지 않습니다. 적은 명령어 수,짧은 코드,적은 클록,짧은 실행 시간은 서로 다른 지표입니다. RISC·CISC 이름만으로 성능을 예측하지 않습니다.

## 직접 확인하기

1. MUL을 쓰는 바이너리가 RV32I 지원만으로 충분한가요?
2. 같은 ISA면 다른 OS의 실행 파일도 반드시 동작하나요?
3. MIPS의 분기 PC+4 계산을 RV32I에 그대로 쓰면?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 아닙니다. 이 과정의 MUL은 M 확장이 필요합니다.</p>
<p>2. 아닙니다. ABI·로더·시스템 호출 같은 환경도 맞아야 합니다.</p>
<p>3. RV32I의 현재 PC 기준과 달라 목표 주소가4바이트 어긋날 수 있습니다.</p>
</details>

## 다음으로 이어가기

다음 선택 레슨은 책의 IA-32 x86 예를 사용해 다른 상태·피연산자·명령어 길이를 비교합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.7.1–6.7.3, 인쇄 pp. 363–366 / PDF pp. 384–387. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
