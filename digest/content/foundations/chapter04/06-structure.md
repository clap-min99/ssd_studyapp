## 이번 레슨의 목표

모듈 정의와 인스턴스를 구별하고 이름 기반 포트 연결과 버스 분할을 추적합니다.

## 앞에서 배운 내용

1장의 계층화·모듈성 원칙을 코드에 적용합니다. 레슨 3의 조건 선택을 기본 블록으로 삼습니다.

## 정의 하나를 여러 위치에서 사용한다

모듈 정의는 블록의 기능을 기술하고, 인스턴스(instance)는 상위 회로 안에 그 블록을 사용하는 자리입니다. 인스턴스 이름은 같은 상위 모듈 안에서 구별되어야 합니다. 함수 호출처럼 한 회로를 시간 순서대로 공유하는 뜻은 아닙니다.

```systemverilog
module pick2(input logic [1:0] a, b, input logic s,
             output logic [1:0] y);
  assign y = s ? b : a;
endmodule

module pick4(input logic [1:0] a, b, c, d,
             input logic [1:0] sel,
             output logic [1:0] y);
  logic [1:0] low, high;
  pick2 u_low (.a(a), .b(b), .s(sel[0]), .y(low));
  pick2 u_high(.a(c), .b(d), .s(sel[0]), .y(high));
  pick2 u_out (.a(low), .b(high), .s(sel[1]), .y(y));
endmodule
```

`.a(c)`는 하위 모듈의 포트 a를 상위 신호 c에 연결한다는 뜻입니다. 점 뒤는 하위 포트 이름, 괄호 안은 상위 신호입니다. 이름 기반 연결은 포트 선언 순서가 달라도 대응을 읽기 쉽습니다. 위치 기반 `pick2 u(a,b,s,y);`도 가능하지만 순서를 틀리면 다른 회로가 됩니다.

4비트 버스를 두 개의 2비트 모듈로 나누려면 한 인스턴스에 a[1:0]·b[1:0]·y[1:0]을, 다른 인스턴스에 a[3:2]·b[3:2]·y[3:2]를 연결하고 선택 신호는 공유합니다. 서로 다른 출력 슬라이스를 구동해야 하며 같은 비트를 겹쳐 구동하지 않습니다. 하위 모듈 정의도 컴파일에 포함해야 합니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-6-t c4-6-d">
<title id="c4-6-t">구조 모델링: 인스턴스와 포트로 회로 연결하기</title>
<desc id="c4-6-d">pick4 안의 세 인스턴스와 입출력 관계를 나타낸 기능도입니다. u_low와 u_high는 나란히 동작하고 두 출력이 u_out으로 연결됩니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">u_low</text><text x="75" y="91">a·b → low</text><text x="223" y="63">u_high</text><text x="223" y="91">c·d → high</text><text x="371" y="63">u_out</text><text x="371" y="91">low·high → y</text></g>
</svg>
<p class="diagram-caption">그림 4-6a. pick4 안의 세 인스턴스와 입출력 관계를 나타낸 기능도입니다. u_low와 u_high는 나란히 동작하고 두 출력이 u_out으로 연결됩니다.</p>

<svg viewBox="0 0 460 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-6b-t c4-6b-d">
<title id="c4-6b-t">세 MUX를 연결한 pick4의 구조</title>
<desc id="c4-6b-d">a와 b는 u_low, c와 d는 u_high에 들어갑니다. 두 출력 low와 high는 u_out에 연결됩니다. 앞의 두 MUX는 sel[0], 마지막은 sel[1]로 선택합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"><rect x="75" y="25" width="95" height="65"/><rect x="75" y="155" width="95" height="65"/><rect x="315" y="90" width="95" height="90"/></g>
<g stroke="var(--ink)" stroke-width="2" fill="none"><path d="M35 43 H75 M35 73 H75 M35 173 H75 M35 203 H75 M170 58 H255 V112 H315 M170 188 H275 V153 H315 M410 135 H447 M122 110 V90 M122 240 V220 M362 210 V180"/></g>
<g fill="var(--ink)" font-size="14"><text x="15" y="47">a</text><text x="15" y="77">b</text><text x="15" y="177">c</text><text x="15" y="207">d</text><text x="94" y="62">u_low</text><text x="92" y="192">u_high</text><text x="338" y="139">u_out</text><text x="192" y="46">low</text><text x="192" y="177">high</text><text x="447" y="139">y</text><text x="96" y="128">sel[0]</text><text x="96" y="257">sel[0]</text><text x="335" y="230">sel[1]</text></g>
</svg>
<p class="diagram-caption">그림 4-6b. pick4의 실제 신호 연결을 나타낸 기능도입니다. 모든 데이터 경로는 2비트이고 선택 신호는 각각 1비트입니다.</p>

## 따라 풀기

a=00,b=01,c=10,d=11이고 sel=10입니다. sel[0]=0이므로 low=a=00, high=c=10입니다. sel[1]=1이므로 y=high=10입니다. sel=11로 바꾸면 low=01, high=11, y=11입니다. 중간 신호 둘을 모두 적어 보면 선택 비트를 바꿔 연결한 오류를 찾기 쉽습니다.

## 헷갈리기 쉬운 점

인스턴스는 always_ff 안에서 매 클록 생성하지 않습니다. 회로의 구조는 실행 전에 정해집니다. 합성기는 사용되지 않는 논리를 지우거나 계층을 평탄화할 수 있으므로 인스턴스 세 개가 반드시 특정 물리 셀 세 개를 보장하지는 않습니다. 3상태 버퍼 두 개를 묶은 MUX 모델도 가능하지만 여기서는 일반 조건 선택을 사용합니다.

## 직접 확인하기

1. u_high에서 .a(c)는 어느 쪽이 포트이고 어느 쪽이 상위 신호인가요?
2. sel=01이면 최종 출력은 무엇인가요?
3. 4비트를 2비트 모듈 둘로 나눌 때 두 출력에 모두 y[1:0]을 연결하면 왜 문제인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. a가 하위 포트이고 c가 상위 신호입니다.</p>
<p>2. b입니다. 첫 단계에서 low=b, high=d이고 둘째 단계에서 low를 고릅니다.</p>
<p>3. 하위 두 비트에 구동이 겹치며 상위 두 비트는 연결되지 않습니다.</p>
</details>

## 다음으로 이어가기

다음에는 조합 블록에 클록과 저장 소자를 추가합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.3, 인쇄 pp. 188–191 / PDF pp. 209–212. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
