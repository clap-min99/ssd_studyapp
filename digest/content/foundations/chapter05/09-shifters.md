## 이번 레슨의 목표

논리·산술 시프트와 회전을 계산하고 MUX 단계로 가변 이동량을 구현하는 원리를 설명합니다.

## 앞에서 배운 내용

4장의 슬라이스·연결은 비트를 조립했습니다. 시프터는 이동량에 따라 각 출력에 어떤 비트를 연결할지 고릅니다.

## 빈자리를 무엇으로 채우는가

논리 시프트는 빈자리를 0으로 채웁니다. 산술 오른쪽 시프트는 원래 부호 비트를 복제합니다. 왼쪽 이동 자체는 논리·산술에서 같고 폭 밖으로 밀린 비트는 사라집니다. 회전(rotate)은 밀려난 비트를 반대편 빈자리로 넣어 모든 비트를 보존합니다.

```systemverilog
module ch5_shift8(input logic [7:0] a, input logic [2:0] shamt,
                  output logic [7:0] left_y, right_y, arithmetic_y, ror_y);
  assign left_y = a << shamt;
  assign right_y = a >> shamt;
  assign arithmetic_y = $unsigned($signed(a) >>> shamt);
  assign ror_y = (a >> shamt) | (a << (4'd8-{1'b0,shamt}));
endmodule
```

>>>의 왼쪽 피연산자가 unsigned라면 부호 확장을 기대할 수 없습니다. 위 코드는 이동 연산을 signed로 수행한 뒤 그 비트 패턴을 unsigned 출력으로 명시 변환합니다. shamt는 0부터 7까지이며, 회전량 0에서는 두 번째 항이 8비트 왼쪽 이동으로 0이 되어 원래 a가 나옵니다. 다른 폭에 적용하려면 이동량 범위도 다시 정합니다.

N비트 가변 시프터는 출력마다 N:1 MUX를 두는 방식으로 볼 수 있습니다. 보충 구조로 8비트는 1·2·4비트 이동 여부를 고르는 2:1 MUX 세 단계로도 만들 수 있습니다. log₂8=3단계 조합 경로이며 세 클록 지연은 아닙니다. 회전기는 0 입력 대신 반대편 비트를 연결합니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-9-t c5-9-d">
<title id="c5-9-t">시프터와 회전기: 비트 이동과 수의 해석</title>
<desc id="c5-9-d">오른쪽 이동의 상위 빈자리 채우기 규칙을 비교한 개념도입니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">논리 오른쪽</text><text x="75" y="87">빈자리 0</text><text x="223" y="59">산술 오른쪽</text><text x="223" y="87">원래 부호 복제</text><text x="371" y="59">오른쪽 회전</text><text x="371" y="87">밀린 비트가 앞에</text></g>
</svg>
<p class="diagram-caption">그림 5-9. 오른쪽 이동의 상위 빈자리 채우기 규칙을 비교한 개념도입니다.</p>

## 따라 풀기

a=10110001,이동량=2입니다. 논리 오른쪽 00101100, 산술 오른쪽 11101100, 왼쪽 11000100, 오른쪽 회전 01101100입니다. signed 원래 값은 −79, 산술 오른쪽 결과는 −20입니다. −79/4=−19.75를 음의 무한대 방향으로 내린 값으로 0 방향 절삭과 다릅니다. 왼쪽 이동을 무조건 정확한 ×4로 읽으면 상위 비트 잘림을 놓칩니다.

## 헷갈리기 쉬운 점

시프터는 조합논리이고 시프트 레지스터는 에지마다 데이터를 저장·이동하는 순차논리입니다. signed 정수 나눗셈과 산술 오른쪽 이동은 음수의 반올림 규칙이 다를 수 있습니다.

## 직접 확인하기

1. 00000001을 오른쪽 1비트 회전하면?
2. 11111101을 signed 산술 오른쪽 1비트 이동하면?
3. 1·2·4 단계에서 이동량 5는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 10000000입니다.</p>
<p>2. 11111110 즉 −2입니다.</p>
<p>3. 1과 4 이동을 선택하고 2 이동은 통과합니다.</p>
</details>

## 다음으로 이어가기

다음 두 선택 심화는 곱셈·나눗셈입니다. 핵심 과정은 레슨12 고정소수점으로 이어갑니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.5, 인쇄 pp. 251–252 / PDF pp. 272–273. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
