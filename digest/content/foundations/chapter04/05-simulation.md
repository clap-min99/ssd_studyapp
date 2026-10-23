## 이번 레슨의 목표

4상태 연산과 공유 버스의 충돌을 추적하고 시뮬레이션 지연을 실제 타이밍 조건과 구별합니다.

## 앞에서 배운 내용

2장의 X는 미지값, Z는 구동하지 않는 상태였습니다. 3장의 초기화하지 않은 레지스터도 시뮬레이션에서는 X로 드러납니다.

## 미지값과 무구동을 숨기지 않는다

SystemVerilog의 logic은 0·1·x·z를 표현합니다. X는 초기화 누락이나 충돌 등으로 값이 확정되지 않았다는 모델이고 Z는 고임피던스입니다. 어느 쪽도 유효한 세 번째 이진 숫자가 아닙니다. `0 & x=0`, `1 & x=x`, `1 | z=1`처럼 다른 입력으로 결과가 결정되는 경우도 있습니다.

```systemverilog
module shared_line(input logic a, b, en_a, en_b,
                   output tri bus_line);
  assign bus_line = en_a ? a : 1'bz;
  assign bus_line = en_b ? b : 1'bz;
endmodule
```

여러 구동원을 연결하는 이 교육용 모델에서는 net인 `tri`를 사용합니다. 두 enable이 모두 0이면 Z, 하나만 1이면 해당 값, 둘 다 1이고 서로 다른 값을 보내면 X입니다. 같은 값을 보내면 모델에서는 그 값으로 해소되지만, 이는 상호 배제 제어를 생략해도 된다는 설계 규칙이 아닙니다. 실제 구현의 내부 3상태 지원 여부는 대상 기술과 도구에 따라 다르므로 일반 선택 회로는 MUX로 기술합니다.

아래는 별도의 시뮬레이션 지연 모델입니다.

```systemverilog
module delay_model(input logic a, b, output logic y);
  timeunit 1ns;
  timeprecision 1ps;
  assign #3 y = a & b;
endmodule
```

`#3`은 이 모델에서 3ns 대기를 뜻합니다. 단위는 1ns, 시간 정밀도는 1ps입니다. 이 지연은 실제 게이트의 지연을 지정하는 배치·배선 제약이 아닙니다. 합성 도구가 무시하거나 허용하지 않을 수 있으므로 합성할 설계와 분리합니다. 짧은 펄스는 지연 모델의 이벤트 취소 규칙에도 영향을 받으므로 아래 예제는 입력이 충분히 오래 유지된 경우입니다.

<svg viewBox="0 0 446 145" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c4-5-t c4-5-d">
<title id="c4-5-t">X·Z와 지연: 시뮬레이션이 표현하는 것</title>
<desc id="c4-5-d">shared_line의 세 구동 조건을 비교한 개념도입니다. 단일 구동 칸에서는 en_b=0을 가정합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="30" width="126" height="85" rx="7"/><rect x="160" y="30" width="126" height="85" rx="7"/><rect x="308" y="30" width="126" height="85" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="63">무구동</text><text x="75" y="91">en_a=en_b=0 → Z</text><text x="223" y="63">단일 구동</text><text x="223" y="91">en_a=1 → a</text><text x="371" y="63">충돌</text><text x="371" y="91">a≠b·둘 다 켬 → X</text></g>
</svg>
<p class="diagram-caption">그림 4-5. shared_line의 세 구동 조건을 비교한 개념도입니다. 단일 구동 칸에서는 en_b=0을 가정합니다.</p>

## 따라 풀기

a=0,b=1입니다. enable 쌍 00이면 Z, 10이면 0, 01이면 1, 11이면 X입니다. 별도 delay_model에서는 b=1이 안정되어 있고 a가 10ns에 0→1로 바뀐 뒤 유지되면 y의 상승은 13ns입니다. 입력이 10ns에 바뀌었다는 사실만으로 실제 칩에서도 13ns에 바뀐다고 결론내릴 수는 없습니다.

## 헷갈리기 쉬운 점

코드의 x 할당을 실제 하드웨어가 X를 생성한다는 뜻으로 읽지 않습니다. 합성에서는 자유도로 취급될 수 있습니다. 시뮬레이션 X는 아날로그 준안정성의 해소 시간이나 MTBF를 계산하는 모델도 아닙니다.

## 직접 확인하기

1. 0&z와 1&z는 각각 무엇인가요?
2. 두 구동원이 0과 1을 동시에 보내면 tri의 결과는 무엇인가요?
3. #3을 #6으로 바꾸면 합성된 칩이 반드시 두 배 느려지나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0과 X입니다. AND의 0 입력은 결과를 확정합니다.</p>
<p>2. 같은 구동 세기를 가정한 이 모델에서는 X입니다.</p>
<p>3. 아닙니다. 실제 지연은 소자·배선·부하와 구현 제약으로 결정됩니다.</p>
</details>

## 다음으로 이어가기

다음에는 하위 모듈 여러 개를 연결해 큰 회로를 구성합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §4.2.8, 4.2.10, 인쇄 pp. 184–187 / PDF pp. 205–208. 설명·도식·예제·확인 문제는 자체 구성입니다. 주 예제는 SystemVerilog이며 VHDL 비교는 별도 표시합니다.
