## 이번 레슨의 목표

입력 와일드카드가 나타내는 조건을 풀어 쓰고 case·casez 및 출력 X의 차이를 설명합니다.

## 앞에서 배운 내용

2장의 명세 don’t care는 출력 자유도였고, 시뮬레이션 X는 알 수 없는 값이었습니다. HDL의 패턴 와일드카드는 또 다른 문법적 역할입니다.

## 비교에서 무시하는 자리와 출력 자유도는 다르다

```systemverilog
module priority3(input logic [2:0] req,
                 output logic [2:0] grant);
  always_comb begin
    casez (req)
      3'b1??: grant = 3'b100;
      3'b01?: grant = 3'b010;
      3'b001: grant = 3'b001;
      default: grant = 3'b000;
    endcase
  end
endmodule
```

`casez`에서 ?와 Z 자리는 비교할 때 무시합니다. 위 항목은 이진 입력 100·101·110·111을 첫 분기로, 010·011을 둘째 분기로 묶습니다. 정상 0·1 입력에서는 출력이 모두 구체적으로 정해져 있습니다. ‘낮은 우선순위 입력을 보지 않는다’는 뜻이지 출력 비트를 마음대로 정하라는 뜻이 아닙니다.

반면 `grant = 3'bxxx;`는 시뮬레이션에서는 X 출력을 내고 합성에서는 구현 자유도로 해석될 수 있습니다. 실제 장치가 X라는 전압을 출력하는 것이 아닙니다. 이 트랙의 정상 동작 예제는 가능한 한 0·1 기본값을 지정하고, 명세가 정말 허용한 자유도만 별도로 표시합니다.

일반 `case`는 4상태 패턴을 정확히 맞춥니다. `casez`는 입력 쪽의 Z도 무시하므로 연결이 빠진 입력이 정상 분기처럼 보일 수 있습니다. `casex`는 X까지 무시해 초기화 누락을 더 쉽게 숨깁니다. 핵심 회로에서는 명확한 if 또는 정확한 case를 우선 고려하고, casez를 쓰면 입력이 유효한 이진값인지 별도로 검사합니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-12-t c4-12-d">
<title id="c4-12-t">Casez와 Don’t care: 자유도와 미지값 구별하기</title>
<desc id="c4-12-d">정상 이진 입력을 casez 패턴별로 묶은 개념도입니다. 나머지 중 001의 grant는 001이고 000의 grant는 000입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">1??</text><text x="75" y="91">100·101·110·111</text><text x="223" y="63">01?</text><text x="223" y="91">010·011</text><text x="371" y="63">나머지</text><text x="371" y="91">001 또는 000</text></g>
</svg>
<p class="diagram-caption">그림 4-12. 정상 이진 입력을 casez 패턴별로 묶은 개념도입니다. 나머지 중 001의 grant는 001이고 000의 grant는 000입니다.</p>

## 따라 풀기

req=110이면 첫 패턴 1??에 맞아 grant=100입니다. req=011이면 첫 패턴과는 최상위가 다르고 두 번째 01?에 맞아 010입니다. req=000이면 명시 패턴 어느 것에도 맞지 않아 000입니다. req=z00은 입력 Z도 와일드카드가 되므로 첫 패턴에 맞아 100이 될 수 있습니다. 따라서 정상 이진 입력 8가지를 통과한 검사와 미연결 입력을 검출하는 검사는 다릅니다.

## 헷갈리기 쉬운 점

겹치는 패턴에서는 먼저 나온 항목이 선택되어 우선순위가 생깁니다. 예제 패턴은 정상 이진 입력에서는 서로 겹치지 않습니다. ?는 어디에 쓰든 만능 don’t care라는 뜻이 아니며 casez 문맥을 확인합니다. 합성 최적화를 위해 X를 넣은 코드를 검증 오류 검출 코드로 동시에 믿지 않습니다.

## 직접 확인하기

1. req=101의 출력은 무엇인가요?
2. 이 예제의 ??는 grant의 두 비트가 자유라는 뜻인가요?
3. casez에서 입력 z00이 특히 위험한 이유는 무엇인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 100입니다.</p>
<p>2. 아닙니다. req의 낮은 두 자리를 비교하지 않는다는 뜻입니다. grant는 100으로 고정입니다.</p>
<p>3. 최상위 Z가 비교에서 무시되어 정상 요청처럼 첫 분기에 맞을 수 있습니다.</p>
</details>

## 다음으로 이어가기

다음에는 상태 레지스터와 조합 블록을 합쳐 FSM을 기술합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.5.3–4.5.4, 인쇄 pp. 203–204 / PDF pp. 224–225. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
