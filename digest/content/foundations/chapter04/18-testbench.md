## 이번 레슨의 목표

DUT와 테스트벤치를 구별하고 모든 이진 입력을 검사하며 X가 나왔을 때도 실패시키는 검사를 작성합니다.

## 앞에서 배운 내용

레슨 1에서 네 입력 조합을 손으로 확인했습니다. 시뮬레이터가 기대 출력과 비교하도록 만들어 반복 검사를 줄입니다.

## 입력·기대값·관찰 시점·종료를 정한다

아래 테스트벤치는 레슨 1의 access_gate를 DUT(device under test)로 사용합니다. access_gate 정의와 함께 컴파일합니다. 테스트벤치는 외부 입출력 포트 없이 내부에서 자극을 만듭니다.

```systemverilog
module tb_access;
  timeunit 1ns;
  timeprecision 1ps;
  logic closed, permit, pass;
  logic expected;
  access_gate dut(.door_closed(closed), .permit(permit), .pass(pass));
  initial begin
    for (int v = 0; v < 4; v = v + 1) begin
      {closed, permit} = v[1:0];
      case (v)
        3: expected = 1'b1;
        default: expected = 1'b0;
      endcase
      #1;
      assert (pass === expected)
        else $fatal(1, "v=%0d pass=%b expected=%b", v, pass, expected);
    end
    $display("PASS: 4 vectors");
    $finish;
  end
endmodule
```

`initial`은 시뮬레이션 시작에 한 번 실행됩니다. for는 00,01,10,11을 순서대로 적용합니다. `#1`로 조합논리 평가가 끝난 뒤 검사하며 여기서는 1ns입니다. 이는 회로의 실제 지연을 측정한 수치가 아닙니다. 기대값은 DUT의 식을 그대로 복사하지 않고 별도 진리표에서 정했습니다.

`===`는 X·Z도 포함해 비교하고 항상 확정된 참·거짓을 냅니다. 기대값이 0·1인데 pass가 X면 실패합니다. `==`는 비교가 X가 될 수 있고 `if (pass != expected)`처럼 쓰면 미지 비교를 놓칠 수 있습니다. assert의 실패 분기에서는 $fatal로 테스트를 실패 종료하고, 모든 벡터가 맞으면 $display 후 $finish로 끝냅니다. 화면에서 파형만 보는 검사보다 반복 실행하기 쉽습니다.

이 장의 initial·시간 대기·출력 문장은 검증 환경용입니다. 일부 FPGA 도구의 초기화 지원과 같은 별도 기능을 일반화하지 않고, 합성할 핵심 회로와 테스트벤치 파일을 분리합니다. 시뮬레이터에서는 SystemVerilog 모드와 최상위 tb_access를 선택합니다. 구체 명령은 설치한 도구에 맞춥니다.

<svg viewBox="0 0 450 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-18-study-t c4-18-study-d">
<title id="c4-18-study-t">한 테스트 벡터의 자극과 관찰 순서</title>
<desc id="c4-18-study-d">0ns에 입력 벡터 00을 주고 #1 이후 1ns에 비교합니다. 다음 벡터 01을 그 뒤 적용하고 2ns에 비교합니다. 이 시간은 시뮬레이션 관찰 간격이며 실제 게이트 지연값이 아닙니다.</desc>
<path d="M35 110 H420 M70 100 V120 M210 100 V120 M350 100 V120" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="70" y="145" font-size="15" text-anchor="middle" fill="var(--ink)">0ns</text><text x="210" y="145" font-size="15" text-anchor="middle" fill="var(--ink)">1ns</text><text x="350" y="145" font-size="15" text-anchor="middle" fill="var(--ink)">2ns</text><text x="80" y="50" font-size="14" text-anchor="middle" fill="var(--ink)">입력 00 적용</text><text x="223" y="50" font-size="14" text-anchor="middle" fill="var(--ink)">00 결과 비교</text><text x="223" y="75" font-size="14" text-anchor="middle" fill="var(--ink)">그 뒤 01 적용</text><text x="353" y="50" font-size="14" text-anchor="middle" fill="var(--ink)">01 결과 비교</text><text x="225" y="195" font-size="13" text-anchor="middle" fill="var(--ink)">자극 → 조합 평가 대기 → 기대값 비교 → 다음 자극</text>
</svg>
<p class="diagram-caption">그림 4-18. 0ns에 입력 벡터 00을 주고 #1 이후 1ns에 비교합니다. 다음 벡터 01을 그 뒤 적용하고 2ns에 비교합니다. 이 시간은 시뮬레이션 관찰 간격이며 실제 게이트 지연값이 아닙니다.</p>

## 실패해야 할 설계도 실제로 실패하는 검사 만들기

테스트벤치의 입력 생성과 기대값 계산은 서로 다른 역할입니다. for의 v는 어떤 입력을 주는지 정하고 case의 expected는 명세상 정답을 제공합니다. DUT의 AND 식을 그대로 복사해 기대값을 만들면 동일한 오해를 양쪽에 넣을 수 있으므로 진리표 같은 독립 표현을 사용합니다.

두 비트 입력에는 네 이진 조합이 있습니다. 각 벡터에서 자극을 먼저 주고, 조합 평가를 기다린 다음 비교합니다. 이 순서를 하나의 반복 안에 묶어야 ‘이전 입력의 출력’을 다음 기대값과 비교하는 실수를 줄일 수 있습니다. 실패 메시지에는 벡터 번호와 실제·기대값을 함께 넣어 원인을 재현하게 합니다.

검사의 품질은 PASS만으로 알 수 없습니다. AND를 OR로 바꾸거나 포트를 미연결로 둔 별도 오류 사본이 실제로 실패해야 합니다. 이는 일부러 오류를 넣어 검출 능력을 확인하는 학습 실습입니다. 정상 소스에 오류를 남기지 말고 사본에서 수행한 뒤 원상태로 돌아옵니다.

## 따라 풀기

v=2이면 v[1:0]=10이므로 closed=1,permit=0입니다. 기대값은 case의 default에서 0입니다. #1 뒤 pass=0이면 통과합니다. 실수로 DUT를 AND 대신 OR로 작성했다면 pass=1이 되어 이 벡터에서 실패합니다. 출력이 연결되지 않아 X가 나와도 X===0은 0이므로 실패합니다. 테스트가 정상 코드만 통과하는지뿐 아니라 이런 오류도 잡는지 확인합니다.

### 조건을 바꾸어 한 번 더 풀기

올바른 AND와 잘못된 OR의 출력표를 비교합니다.

| closed·permit | 기대 AND | 오류 OR | 검사 결과 |
| --- | --- | --- | --- |
| 00 | 0 | 0 | 차이 없음 |
| 01 | 0 | 1 | 실패 검출 |
| 10 | 0 | 1 | 실패 검출 |
| 11 | 1 | 1 | 차이 없음 |

00·11 두 벡터만 시험하면 OR 오류도 통과합니다. 모든 이진 조합을 다룰 수 있는 작은 회로에서는 전체 열거가 명료한 기준입니다. 큰 회로에서는 상태·경계·중요 조건을 정해 검사 범위를 설명해야 합니다.

### 터미널에서 직접 실행하는 실습

본문의 완전한 HDL 블록을 파일로 내보내는 도구를 제공합니다. 프로젝트 루트에서 다음을 실행합니다. `hdl_practice`는 아직 없는 새 폴더 이름으로 정하세요. 이미 만든 실습 파일을 덮어쓰지 않도록 기존 폴더는 거부합니다.

```powershell
.\venv\Scripts\python.exe scripts/export_foundations_hdl.py --output hdl_practice
cd hdl_practice
```

출력 폴더에는 원문 레슨 코드에서 추출한 `lessons.sv`와 파일 기반 실습용 `access_vectors.mem`이 생깁니다. 별도로 설치한 SystemVerilog 시뮬레이터에서 최상위 모듈을 `tb_access`로 선택합니다. Icarus Verilog를 사용하는 경우의 예는 다음과 같습니다. 도구 설치 명령이 아니며 `iverilog`·`vvp`가 실행 가능한 환경이 전제입니다.

```powershell
iverilog -g2012 -s tb_access -o access.vvp lessons.sv
vvp access.vvp
```

정상 기대 로그는 `PASS: 4 vectors`입니다. 파일 기반 검사는 최상위를 `tb_access_file`로 바꾸고 같은 폴더에서 실행하면 `PASS: file vectors`가 기대됩니다. 클록 실습은 `tb_parity_control`을 최상위로 선택하고 `PASS: parity control`을 기대합니다. 한 번에 최상위 하나를 선택해야 서로 다른 테스트벤치의 `$finish`가 다른 검사를 중간에 끝내지 않습니다.

먼저 코드를 그대로 실행하고,그 뒤 실습 사본에서 `access_gate`의 AND를 OR로 바꾸어 실패하는 벡터와 로그를 확인하세요. 마지막에는 원래 코드로 되돌려 다시 통과시킵니다. 여기의 로그는 기대 결과이며 이 문서 작성 검증에서 HDL 시뮬레이터를 실행했다는 기록은 아닙니다.

## 헷갈리기 쉬운 점

입력만 주고 출력을 확인하지 않은 실행은 자동 검사가 아닙니다. 합성 성공도 이 테스트를 대신하지 않습니다. 4개 벡터의 완전 검사는 이 작은 2입력 이진 조합 함수에만 해당하며 실제 타이밍·전력·모든 X/Z 조합까지 검사한 것은 아닙니다.

## 직접 확인하기

1. 독립된 1비트 입력이 3개면 이진 조합은 몇 개인가요?
2. 기대값이 1인데 pass=X이면 === 비교는 어떻게 되나요?
3. 왜 입력 대입 직후 같은 순간에 바로 검사하지 않나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 2³=8개입니다.</p>
<p>2. 거짓이 되어 assert가 실패합니다.</p>
<p>3. 연속 할당과 조합 블록의 이벤트 평가가 반영되기 전에 읽는 경합을 피하려고 관찰 시점을 분리합니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

입력 둘 중 permit 연결을 실수로 closed에 연결해 DUT가 closed AND closed를 계산합니다. 네 벡터 중 어떤 것이 이 오류를 검출하나요? 출력이 X인 경우도 실패하도록 비교 연산자를 선택하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>closed=1,permit=0인 10에서 기대 0과 실제 1이 달라집니다. 01에서는 closed가 0이므로 이 특정 오류는 드러나지 않습니다.</p>
<p>기대값을 유효한 0/1로 둔 채 assert(pass===expected) 또는 if(pass!==expected)로 검사합니다. 출력 X도 확정적으로 불일치 처리해야 미연결 오류를 놓치지 않습니다.</p>
</details>

## 다음으로 이어가기

다음에는 벡터를 파일에서 읽고 클록이 있는 회로를 검사하는 순서를 정합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.9, 인쇄 pp. 218–220 / PDF pp. 239–241. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
