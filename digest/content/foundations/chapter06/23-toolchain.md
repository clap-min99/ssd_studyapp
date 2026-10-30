## 이번 레슨의 목표

[선택 심화] 컴파일·어셈블·링크·로드의 입력과 출력을 구별하고 미정 주소가 언제 결정되는지 설명합니다.

## 앞에서 배운 내용

레슨16의 의사명령어와 레슨22의 섹션·심볼을 사용합니다. 소스 줄만으로 최종 주소를 확정할 수 없는 이유를 봅니다.

## 네 단계가 서로 다른 질문에 답한다

컴파일러(compiler)는 C 같은 고급 언어를 목표 ISA의 코드로 바꿉니다. 어셈블러(assembler)는 레지스터·연산·상수 필드를 기계어로 만들고 섹션·심볼·재배치 정보를 목적 파일(object file)에 넣습니다. 두 번 훑는 모델에서는 먼저 레이블 위치를 모으고 그 뒤 참조를 해결합니다.

링커(linker)는 여러 목적 파일과 라이브러리·시작 코드를 합치고 배치 주소와 외부 심볼을 해결합니다. 재배치(relocation)는 최종 주소가 정해졌을 때 고칠 위치와 계산 규칙을 기록한 것입니다. 가까운 호출을 줄이는 relaxation이 있으면 코드 크기와 뒤 주소도 달라질 수 있습니다.

로더(loader)는 실행 파일의 필요한 부분을 메모리에 놓고 시작 상태를 준비해 진입점으로 제어를 넘깁니다. bare-metal에서는 부트 코드가 데이터 복사·BSS 초기화·sp 준비 등을 맡을 수 있습니다. C의 main이 전원 직후 자동으로 첫 실행되는 것은 아닙니다.

## 출력 파일을 읽으며 확인하기

아래는 RISC-V 크로스 툴체인이 설치된 환경의 예시입니다. 도구 이름은 환경마다 다릅니다. 이 레슨은 도구 설치나 실행 환경을 앱에 추가하지 않습니다.

```sh
riscv64-unknown-elf-gcc -march=rv32i -mabi=ilp32 -S sample.c -o sample.s
riscv64-unknown-elf-gcc -march=rv32i -mabi=ilp32 -c sample.s -o sample.o
riscv64-unknown-elf-objdump -dr sample.o
```

`-S`는 어셈블리까지,`-c`는 목적 파일까지 만듭니다. objdump의`-r`은 재배치도 보여 줍니다. 실행 파일 링크에는 해당 보드의 메모리 맵·시작 코드·라이브러리 설정이 필요합니다. 호스트용 gcc로 만든 실행 파일이 RV32I 코드라고 가정하지 않습니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-23-t c6-23-d">
<title id="c6-23-t">목적 파일의 미정 참조는 최종 링크 배치에서 해결한다.</title>
<desc id="c6-23-d">C → 어셈블리|컴파일 / .o + 심볼·재배치|어셈블 / 실행 파일 → 메모리|링크 후 로드</desc>
<rect x="12" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="82" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">C → 어셈블리</text>
<text x="82" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">컴파일</text>
<path d="M152 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="168" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="238" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">.o + 심볼·재배치</text>
<text x="238" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">어셈블</text>
<path d="M308 94 h16 m-5 -5 l5 5 -5 5" fill="none" stroke="var(--ink)" stroke-width="2"/>
<rect x="324" y="45" width="140" height="95" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="394" y="76" text-anchor="middle" font-size="14" fill="var(--ink)">실행 파일 → 메모리</text>
<text x="394" y="99" text-anchor="middle" font-size="14" fill="var(--ink)">링크 후 로드</text>
</svg>
<p class="diagram-caption">그림 6-23. 목적 파일의 미정 참조는 최종 링크 배치에서 해결한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

main.o가 외부 함수 helper를 호출하고 util.o가 helper를 정의한다고 합시다. 컴파일 단계에서는 이름만 알 수 있고 최종 주소는 모를 수 있습니다. 링크가 호출 명령어를0x1010,helper를0x1080에 배치해 JAL 하나로 확정했다면 변위는0x70=112바이트,링크 주소는0x1014입니다.

util.o의 helper를0x2080으로 옮기면 같은 호출 소스라도 변위와 기계어가 달라집니다. 더 멀리 가면 단일 JAL 범위를 벗어나 AUIPC·JALR 등이 필요할 수 있습니다. 로드 주소가 달라지는 환경에서는 로드 시 재배치나 위치 독립 코드도 고려합니다.

## 헷갈리기 쉬운 점

목적 파일의0 주소 표기가 최종 메모리0번지에 프로그램을 놓겠다는 뜻은 아닙니다. 실행 파일의 진입점과 main도 동일하다고 단정하지 않습니다. 파일 크기와 BSS를 포함한 실행 시 메모리 사용량은 다를 수 있습니다.

## 직접 확인하기

1. 함수를 선언했지만 어떤 파일에도 정의하지 않으면 어느 단계에서 드러날 수 있나요?
2. 목적 파일에 기계어가 있으면 이미 실행 파일인가요?
3. 링커가 호출 두 명령어를 하나로 줄이면 무엇을 다시 계산해야 하나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 일반적으로 링크에서 미정의 심볼 오류가 납니다.</p>
<p>2. 아닙니다. 외부 참조·배치·시작 코드가 아직 해결되지 않았을 수 있습니다.</p>
<p>3. 뒤 코드와 심볼 주소 및 관련 변위를 새 배치에 맞춰 정해야 합니다.</p>
</details>

## 다음으로 이어가기

다음에는 워드를 바이트로 저장할 때의 순서와 예외·확장 동작을 선택 심화로 살펴봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.5.3–6.5.6, 인쇄 pp. 348–355 / PDF pp. 369–376. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
