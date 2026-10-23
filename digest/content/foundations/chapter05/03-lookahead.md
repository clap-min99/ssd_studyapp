## 이번 레슨의 목표

비트·블록의 생성/전파 신호를 구하고 CLA의 캐리와 지연을 계산합니다.

## 앞에서 배운 내용

리플의 느린 이유는 캐리가 모든 자리를 거치기 때문입니다. 여러 자리의 캐리 조건을 입력에서 먼저 계산할 수 있습니다.

## 캐리를 만드는 조건과 통과시키는 조건을 분리한다

책과 같이 G_i=A_i·B_i, P_i=A_i+B_i로 정의합니다. 여기의 +는 OR입니다. c[0]=C_in일 때 c[i+1]=G_i+P_i·c[i]입니다. G=1이면 입력 캐리 없이도 출력 캐리가 생기고 P=1이면 입력 캐리 1을 출력까지 보냅니다. A=B=1이면 G=P=1이어도 이 식은 성립합니다.

4비트 블록은 다음을 사용합니다.

```text
P_3:0 = P3·P2·P1·P0
G_3:0 = G3 + P3·G2 + P3·P2·G1 + P3·P2·P1·G0
c[4] = G_3:0 + P_3:0·c[0]
```

블록 전파는 모든 자리가 전파할 때 1입니다. 블록 생성은 블록 안의 어느 생성 캐리가 위 끝까지 전달될 때 1입니다. 한 블록의 G/P는 다른 블록의 입력 캐리를 기다리지 않고 A·B에서 계산합니다. 이 원리가 캐리 미리보기(carry-lookahead adder, CLA)입니다.

책의 단일 수준 블록 CLA는 블록 사이에서는 캐리를 차례로 넘기고 마지막 블록에서 짧은 리플로 합을 만듭니다. N이 k의 배수일 때 교육용 지연 모델은 `t_CLA=t_pg+t_pg_block+(N/k−1)·t_AND_OR+k·t_FA`입니다. 각 항은 비트 G/P 생성, 블록 G/P 생성, 블록 간 캐리, 마지막 블록 합 지연입니다. 이 구조는 블록을 정해 두면 여전히 N에 대해 선형 항이 있습니다. 모든 CLA가 같은 회로라는 뜻은 아닙니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-3-t c5-3-d">
<title id="c5-3-t">캐리 미리보기: Generate와 Propagate</title>
<desc id="c5-3-d">CLA가 캐리를 계산하는 세 수준의 기능 개념도입니다. 합 비트는 별도로 XOR를 사용합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">비트 G/P</text><text x="75" y="87">각 A_i·B_i에서 계산</text><text x="223" y="59">블록 G/P</text><text x="223" y="87">캐리 조건 묶기</text><text x="371" y="59">블록 출력 캐리</text><text x="371" y="87">G + P·입력 캐리</text></g>
</svg>
<p class="diagram-caption">그림 5-3. CLA가 캐리를 계산하는 세 수준의 기능 개념도입니다. 합 비트는 별도로 XOR를 사용합니다.</p>

## 따라 풀기

A=1011₂,B=0100₂이면 모든 자리에서 A와 B 중 하나만 1입니다. 따라서 G_3:0=0, P_3:0=1입니다. c0=0이면 c4=0이고 합은 1111, c0=1이면 c4=1이고 합은 0000입니다. 지연 예로 N=16,k=4,t_pg=60ps,t_pg_block=240ps,t_AND_OR=120ps,t_FA=180ps라 가정하면 60+240+3×120+4×180=1380ps입니다. 같은 가정의 리플 2880ps보다 짧지만 게이트와 배선 비용이 늘어납니다.

## 헷갈리기 쉬운 점

레슨1의 p=A XOR B를 이 레슨의 OR형 P와 혼용하지 않습니다. 특히 OR형 P를 S=P XOR c에 넣으면 A=B=1에서 틀립니다. 합은 항상 A XOR B XOR c입니다. HDL의 generate 문법과 캐리 generate 신호도 다른 뜻입니다.

## 직접 확인하기

1. A=B=1에서 G,P는?
2. 블록 P가 0이면 입력 캐리의 영향은?
3. 블록 간 캐리를 직렬로 넘기는 CLA의 지연이 반드시 log N인가요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 둘 다 1입니다. 캐리가 생성됩니다.</p>
<p>2. 블록 최상위 출력 캐리에는 전달되지 않습니다. 출력 캐리는 블록 G가 결정합니다.</p>
<p>3. 아닙니다. 이 모델에는 N/k에 비례하는 항이 있습니다.</p>
</details>

## 다음으로 이어가기

다음 선택 심화는 G/P를 트리로 합치는 프리픽스 덧셈기입니다. 핵심 과정은 레슨5로 이어가도 됩니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.1, 인쇄 pp. 239–241 / PDF pp. 260–262. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
