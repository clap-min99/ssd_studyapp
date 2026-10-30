## 이번 레슨의 목표

명령어 집합 구조(ISA)가 정하는 상태 변화와 마이크로아키텍처의 구현 선택을 구별합니다.

## 앞에서 배운 내용

5장에서 ALU·레지스터 파일·메모리를 만들었습니다. 이제 그 블록을 사용할 프로그램이 어떤 동작을 기대할 수 있는지 약속합니다.

## 프로그램이 볼 수 있는 약속

아키텍처(architecture)는 명령어의 종류와 의미, 레지스터, 메모리 주소 체계 등 프로그램에 보이는 규칙입니다. 명령어 집합(instruction set)은 가능한 연산의 목록이고, 각 명령어에는 무엇을 읽고 어디에 결과를 쓸지 정하는 피연산자(operand)가 있습니다. ISA는 이 명령어들의 비트 표현과 실행 의미를 정합니다.

`add x5, x6, x7`은 두 레지스터의 값을 더해 x5에 씁니다. 덧셈기가 리플 캐리인지 프리픽스인지, 한 명령어를 몇 클록에 실행하는지는 마이크로아키텍처(microarchitecture)의 선택입니다. 같은 ISA를 구현해도 속도·면적·전력은 달라질 수 있습니다. 같은 프로그램 실행에는 ISA 외에 ABI와 실행 환경도 맞아야 합니다.

## 이 장의 실행 모델

기본은 RV32I입니다. 정수 레지스터 폭 XLEN은 32비트이고 x0부터 x31까지 있습니다. 기본 명령어는 32비트, 즉 4바이트입니다. 압축 명령어 C 확장은 별도로 표시합니다. 이 장의 일반 예제는 C 확장을 끄고, 데이터 워드는 4바이트 경계에 정렬하며, 주소와 저장값을 구별합니다.

사람이 읽는 `add` 같은 표기는 어셈블리 언어(assembly language), CPU가 해독하는 비트열은 기계어(machine language)입니다. C의 한 문장이 여러 명령어로 바뀔 수 있습니다. 4장의 HDL은 회로를 표현했지만 여기의 어셈블리는 실행할 명령어열을 표현합니다.

규칙성, 흔한 경우의 단순화, 작은 피연산자 저장소, 명령어 형식 사이의 절충은 설계 이유입니다. ‘작으면 언제나 빠르다’ 같은 성능 보장으로 외우지 말고 어떤 경로와 비용을 줄이는지 설명합니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-1-t c6-1-d">
<title id="c6-1-t">같은 명령어 의미를 서로 다른 회로가 구현한다.</title>
<desc id="c6-1-d">ISA|x5 ← x6+x7 / 구현 선택|ALU·제어·저장 / 관찰 결과|같은 최종 상태</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">ISA</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">x5 ← x6+x7</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">구현 선택</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">ALU·제어·저장</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">관찰 결과</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">같은 최종 상태</text>
</svg>
<p class="diagram-caption">그림 6-1. 같은 명령어 의미를 서로 다른 회로가 구현한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

실행 전 x6=14, x7=9, x5=100이고 PC=0x100입니다. `add x5,x6,x7`을 정상 실행하면 x5=23, PC=0x104가 됩니다. x6와 x7 및 메모리는 그대로입니다. 이것이 관찰할 상태 변화입니다.

구현 A가 한 클록, 구현 B가 여러 클록을 사용해도 명령어 경계의 이 결과는 같아야 합니다. 최종값이 같다는 것만으로 처리 시간까지 같다고 결론 낼 수는 없습니다.

## 헷갈리기 쉬운 점

32비트 데이터, 32비트 주소, 32비트 명령어는 이 모델에서 우연히 폭이 같은 서로 다른 대상입니다. 명령어 개수와 클록 수, 기계어 호환성과 운영체제 호환성도 각각 구별합니다.

## 직접 확인하기

1. x5의 초기값 100을 더하나요?
2. 덧셈기를 바꾸면 반드시 ISA가 바뀌나요?
3. C의 a=(b+c)-d는 왜 한 명령어가 아닐 수 있나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 아닙니다. add의 소스는 x6와 x7이고 x5는 목적지입니다.</p>
<p>2. 아닙니다. 프로그램에 보이는 결과가 같다면 구현만 바뀔 수 있습니다.</p>
<p>3. 기본 산술 명령어 하나는 두 소스를 계산하므로 중간 합을 저장하는 명령어와 뺄셈을 나눌 수 있습니다.</p>
</details>

## 다음으로 이어가기

다음에는 실제 레지스터 이름을 붙이고 여러 산술 명령어의 상태 변화를 추적합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.1–6.2.1, 인쇄 pp. 299–302 / PDF pp. 320–323. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
