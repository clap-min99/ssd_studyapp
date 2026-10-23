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

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-18-t c4-18-d">
<title id="c4-18-t">테스트벤치: 입력 생성에서 자동 검사까지</title>
<desc id="c4-18-d">한 벡터를 검사하는 순서입니다. 네 벡터를 반복한 뒤 PASS를 출력하고 종료합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">자극 생성</text><text x="75" y="91">v=0,1,2,3</text><text x="223" y="63">DUT 평가</text><text x="223" y="91">입력 뒤 #1 대기</text><text x="371" y="63">자동 검사</text><text x="371" y="91">===·실패 종료</text></g>
</svg>
<p class="diagram-caption">그림 4-18. 한 벡터를 검사하는 순서입니다. 네 벡터를 반복한 뒤 PASS를 출력하고 종료합니다.</p>

## 따라 풀기

v=2이면 v[1:0]=10이므로 closed=1,permit=0입니다. 기대값은 case의 default에서 0입니다. #1 뒤 pass=0이면 통과합니다. 실수로 DUT를 AND 대신 OR로 작성했다면 pass=1이 되어 이 벡터에서 실패합니다. 출력이 연결되지 않아 X가 나와도 X===0은 0이므로 실패합니다. 테스트가 정상 코드만 통과하는지뿐 아니라 이런 오류도 잡는지 확인합니다.

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

## 다음으로 이어가기

다음에는 벡터를 파일에서 읽고 클록이 있는 회로를 검사하는 순서를 정합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.9, 인쇄 pp. 218–220 / PDF pp. 239–241. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
