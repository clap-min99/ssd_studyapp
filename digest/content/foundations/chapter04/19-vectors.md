## 이번 레슨의 목표

벡터 파일을 읽어 입력과 기대값을 분리하고 파일 오류·미지값·검사 종료를 명확히 처리합니다.

## 앞에서 배운 내용

자동 검사는 반복 가능한 입력과 기대값을 필요로 합니다. 벡터 수가 늘면 본문 코드를 계속 고치기보다 데이터를 따로 관리할 수 있습니다.

## 파일 형식과 검사의 끝을 약속한다

레슨 1의 access_gate를 계속 검사합니다. 파일 access_vectors.mem은 각 줄이 `closed_permit_expected` 순서의 3비트 패턴입니다. 아래처럼 정확히 네 줄을 시뮬레이터 작업 디렉터리에 둡니다. 밑줄은 이진수 읽기에서 무시됩니다.

```text
00_0
01_0
10_0
11_1
```

```systemverilog
module tb_access_file;
  timeunit 1ns;
  timeprecision 1ps;
  logic [2:0] vectors [0:3];
  logic closed, permit, pass, expected;
  integer fd;
  access_gate dut(.door_closed(closed), .permit(permit), .pass(pass));
  initial begin
    for (int i = 0; i < 4; i = i + 1) vectors[i] = 'x;
    fd = $fopen("access_vectors.mem", "r");
    if (fd == 0) $fatal(1, "Cannot open vector file");
    $fclose(fd);
    $readmemb("access_vectors.mem", vectors);
    for (int i = 0; i < 4; i = i + 1) begin
      if ($isunknown(vectors[i])) $fatal(1, "Invalid vector %0d", i);
      {closed, permit, expected} = vectors[i];
      #1;
      if (pass !== expected) $fatal(1, "Mismatch at %0d", i);
    end
    $display("PASS: file vectors");
    $finish;
  end
endmodule
```

`logic [2:0] vectors [0:3]`는 3비트 항목 네 개의 배열입니다. $readmemb는 이진 파일을, $readmemh는 16진 파일을 읽습니다. 파일을 못 열면 실패하고, 파일이 짧아 남은 항목이 X여도 $isunknown이 잡습니다. 이 예제는 정상 0·1 벡터만 허용합니다. X로 배열의 끝을 추측하지 않고 네 개라는 명시한 개수로 종료합니다. 더 긴 파일·가변 개수·형식 오류 전체를 처리하는 범용 파서는 아니므로 도구의 파일 로딩 오류도 확인합니다.

순차 회로는 클록을 만들고 입력 변경과 관찰 에지를 정해야 합니다. 예를 들어 주기 10ns에서는 하강 에지에 다음 입력을 주고 상승 에지 후 #1에 출력과 기대 상태를 비교할 수 있습니다. 기대 상태는 이전 기대 상태와 이번 입력에서 갱신합니다. 조합 회로의 벡터 한 줄과 달리 순차 회로에는 초기화와 입력 이력이 포함됩니다. 다음 종합 레슨에서 실제 코드로 연결합니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-19-t c4-19-d">
<title id="c4-19-t">파일 기반 검사: 벡터·클록·종료 조건</title>
<desc id="c4-19-d">파일 기반 테스트의 데이터·유효성·종료 규칙을 요약한 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">파일 항목</text><text x="75" y="91">3비트 × 4개</text><text x="223" y="63">유효성 검사</text><text x="223" y="91">파일 존재·X/Z 확인</text><text x="371" y="63">비교와 종료</text><text x="371" y="91">4개 검사 후 finish</text></g>
</svg>
<p class="diagram-caption">그림 4-19. 파일 기반 테스트의 데이터·유효성·종료 규칙을 요약한 개념도입니다.</p>

## 따라 풀기

마지막 항목 11_1은 3비트 111입니다. 연결 할당으로 closed=1,permit=1,expected=1을 받습니다. DUT가 1이면 !==는 0이라 통과합니다. 파일에 마지막 줄이 없으면 vectors[3]은 초기값 XXX이고 검사 전에 실패합니다. 기대 출력까지 X인 미완성 벡터를 통과시키지 않습니다. 순차 검사에서 E1에 넣은 입력을 E2의 기대값과 비교하는 실수를 막으려면 에지 번호를 함께 기록합니다.

## 헷갈리기 쉬운 점

파일 이름은 소스 파일 위치가 아니라 실행 작업 디렉터리를 기준으로 찾는 경우가 많습니다. ===/!==는 기대값 자체가 잘못되었을 때 정답을 만들어주지 않으므로 벡터도 검토합니다. 시뮬레이션 성공 메시지뿐 아니라 실패 시 프로세스 종료 상태와 도구 오류 로그도 확인합니다.

## 직접 확인하기

1. 배열 vectors의 전체 데이터 비트 수는 얼마인가요?
2. 파일이 짧으면 이 코드는 어떻게 검출하나요?
3. 레지스터 DUT에서 상승 에지와 동시에 입력을 바꾸고 바로 검사하면 왜 위험한가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 3×4=12비트입니다.</p>
<p>2. 초기 X가 남은 항목을 $isunknown으로 검사해 실패시킵니다.</p>
<p>3. 입력 샘플과 nonblocking 갱신 전에 관찰이 섞이는 경합이 생길 수 있습니다. 자극과 관찰 시점을 분리해야 합니다.</p>
</details>

## 다음으로 이어가기

마지막에는 회로 명세·HDL·자동 검사를 하나의 작은 제어기로 연결합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.9, 인쇄 pp. 220–222 / PDF pp. 241–243. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
