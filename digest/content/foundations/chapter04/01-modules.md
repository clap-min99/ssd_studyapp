## 이번 레슨의 목표

모듈의 인터페이스를 읽고, 동작 기술과 구조 기술 및 시뮬레이션과 합성의 목적을 구별합니다.

## 앞에서 배운 내용

3장에서 조합논리·레지스터·FSM을 회로로 설계했습니다. 이제 같은 회로를 텍스트로 기술합니다. 회로 블록을 먼저 떠올리고 문법을 붙이는 순서를 유지합니다.

## 입출력의 약속부터 정한다

하드웨어 기술 언어(HDL)는 연결된 회로의 기능과 구조를 나타냅니다. 모듈(module)은 이름과 입력·출력 포트가 있는 재사용 단위입니다. 동작 기술은 출력이 어떤 함수인지를, 구조 기술은 어떤 하위 모듈을 연결했는지를 나타냅니다. 둘은 서로 다른 회로 종류가 아니라 기술 방식입니다.

문이 닫혀 있고 검사 허가가 있을 때만 통과시키는 1비트 회로를 만들어 봅시다. 입력 door_closed와 permit은 각각 0 또는 1이고 출력 pass도 1비트입니다.

```systemverilog
module access_gate(input logic door_closed, permit,
                   output logic pass);
  assign pass = door_closed & permit;
endmodule
```

`module`부터 `endmodule`까지가 한 블록입니다. `input`은 외부에서 들어오는 신호, `output`은 내보내는 신호입니다. `logic`은 여기서 4상태 신호 자료형이며 그 이름만으로 저장 소자가 생기지 않습니다. `assign`은 오른쪽 값에 따라 출력을 계속 결정하는 연속 할당입니다. 클록이 없고 과거를 저장하지 않으므로 AND 조합논리입니다.

시뮬레이션(simulation)은 입력을 주고 모델의 출력을 관찰하는 과정입니다. 합성(synthesis)은 합성 가능한 기술을 게이트·배선·저장 소자 연결망(netlist)으로 바꾸는 과정입니다. 합성기는 같은 함수를 다른 게이트 조합으로 최적화할 수 있습니다. 테스트벤치(testbench)는 입력 생성과 검사 환경이며, 화면 출력이나 시간 대기를 실제 논리 회로로 만들려는 코드와 구별합니다.

책은 SystemVerilog와 VHDL을 병렬로 설명합니다. 이 트랙에서는 `.sv` 파일을 쓰는 SystemVerilog를 중심으로 배우고 VHDL 차이는 선택 심화에서 비교합니다. 언어의 역사나 특정 도구의 가격은 학습 목표에 포함하지 않습니다.

<svg viewBox="0 0 450 210" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-1-study-t c4-1-study-d">
<title id="c4-1-study-t">모듈 포트와 AND 기능의 연결</title>
<desc id="c4-1-study-d">두 1비트 입력이 access_gate 안의 AND 기능으로 들어가고 pass 1비트로 나옵니다. 외곽 점선은 모듈 경계이며 저장 소자는 없습니다.</desc>
<rect x="135" y="35" width="180" height="150" rx="8" fill="none" stroke="var(--accent)" stroke-dasharray="5 4"/><rect x="180" y="85" width="90" height="60" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="225.0" y="120.0" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><path d="M35 95 H180 M35 135 H180 M270 115 H415" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="60" y="78" font-size="13" text-anchor="middle" fill="var(--ink)">door_closed</text><text x="60" y="160" font-size="14" text-anchor="middle" fill="var(--ink)">permit</text><text x="225" y="60" font-size="14" text-anchor="middle" fill="var(--ink)">access_gate</text><text x="385" y="100" font-size="15" text-anchor="middle" fill="var(--ink)">pass</text>
</svg>
<p class="diagram-caption">그림 4-1. 두 1비트 입력이 access_gate 안의 AND 기능으로 들어가고 pass 1비트로 나옵니다. 외곽 점선은 모듈 경계이며 저장 소자는 없습니다.</p>

## 문법을 읽기 전에 회로의 계약부터 적기

access_gate의 목적은 ‘두 조건을 모두 만족하면 통과’입니다. 먼저 입력의 뜻을 문장으로 적습니다. door_closed=1은 문이 닫혔다는 뜻이고 permit=1은 검사가 허가되었다는 뜻입니다. 출력 pass=1은 두 입력이 모두 1이라는 뜻입니다. ‘버튼을 한 번 누르면 계속 통과’ 같은 기억 동작은 이 계약에 없습니다. 따라서 저장 소자도 필요하지 않습니다.

다음으로 포트 폭을 정합니다. 여기서는 참·거짓 각각 한 비트면 충분합니다. 그 후 진리표 네 행에서 11인 행만 출력 1이라는 것을 보고 AND를 선택합니다. 이렇게 명세 → 표 → 게이트 → 코드 순서로 읽으면 코드가 회로와 연결됩니다. 반대로 문법부터 외우면 `logic`을 보고 레지스터라고 생각하거나 `assign`을 한 번만 실행하는 명령으로 읽기 쉽습니다.

합성할 때 AND 셀 한 개가 나올 수도 있고, 다른 게이트나 LUT로 같은 함수를 구현할 수도 있습니다. 모듈의 계약은 특정 셀의 이름이 아니라 입력과 출력의 관계입니다. 테스트벤치는 그 계약을 여러 입력에서 확인하는 별도 회로 환경입니다.

## 따라 풀기

입력 순서를 (door_closed, permit)으로 고정합니다. 00이면 0·0=0, 01이면 0·1=0, 10이면 1·0=0, 11이면 1·1=1입니다. 따라서 기대 출력열은 0,0,0,1입니다. 이 네 입력을 시뮬레이션에 넣어 비교하면 모든 이진 입력에 대한 기능을 검사할 수 있습니다. 실제 부품의 지연과 잡음 조건까지 검사했다는 뜻은 아닙니다.

### 조건을 바꾸어 한 번 더 풀기

입력 센서의 극성이 바뀌어 door_open=1이 ‘문 열림’이라고 합시다. permit은 그대로입니다. 문이 닫혔을 때를 나타내려면 먼저 `~door_open`을 만들어야 하므로 식은 `pass=(~door_open)&permit`입니다.

| door_open | permit | 닫힘 조건 | pass |
| --- | --- | --- | --- |
| 0 | 0 | 1 | 0 |
| 0 | 1 | 1 | 1 |
| 1 | 0 | 0 | 0 |
| 1 | 1 | 0 | 0 |

센서 이름만 바꾸고 원래 AND를 유지하면 열린 문에서 통과시키는 회로가 됩니다. 표의 01·11 두 행으로 이 오류를 확인할 수 있습니다.

## 헷갈리기 쉬운 점

포트 선언의 순서는 동작 단계가 아닙니다. SystemVerilog는 대소문자를 구분하므로 pass와 Pass는 다른 이름입니다. 세미콜론은 문장 끝에 쓰고, // 한 줄 주석과 /* 여러 줄 주석 */은 회로를 만들지 않습니다. 들여쓰기와 공백은 읽기 위한 도구입니다. 모듈·신호 이름을 숫자로 시작하지 않습니다.

## 직접 확인하기

1. 이 모듈에서 클록 없이 pass가 바뀌는 이유는 무엇인가요?
2. 시뮬레이션 통과와 합성 성공은 각각 무엇을 확인하나요?
3. AND 회로를 하위 모듈로 연결하는 기술은 어떤 방식인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 연속 할당이 현재 입력의 AND를 나타내기 때문입니다.</p>
<p>2. 전자는 주어진 검사에서 모델의 기능을, 후자는 도구가 해당 기술을 회로로 변환할 수 있음을 확인합니다. 둘 다 실제 회로의 모든 조건을 보장하지 않습니다.</p>
<p>3. 구조 기술입니다. 같은 기능을 식으로 쓰면 동작 기술입니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

permit=1일 때 door_closed를 0→1→0으로 바꿉니다. pass의 안정된 출력열과 저장 소자가 필요한지 적으세요. 다음으로 ‘한 번 닫히면 다시 열려도 pass를 유지’하도록 명세를 바꾸면 무엇을 추가해야 하나요?

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>원래 계약에서는 pass=0→1→0입니다. 현재 두 입력만으로 결정되므로 조합논리입니다.</p>
<p>바뀐 계약에서는 현재 door_closed=0이어도 과거에 닫혔는지 알아야 합니다. 상태 비트와 그 초기화·갱신 조건이 필요합니다. 단순 AND 식의 기호만 바꾸어 해결할 수 없습니다.</p>
</details>

## 다음으로 이어가기

다음에는 여러 비트를 묶은 버스에 게이트 연산을 적용합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.1–4.1.3, 인쇄 pp. 171–175 / PDF pp. 192–196. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
