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

<svg viewBox="0 0 450 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-3-study-t c5-3-study-d">
<title id="c5-3-study-t">블록 캐리를 G와 P로 계산하는 기능 경로</title>
<desc id="c5-3-study-d">A[3:0]·B[3:0]에서 블록 G와 P를 먼저 계산합니다. P와 입력 c0의 AND를 G와 OR하여 c4를 만듭니다. 하위 자리의 캐리와 합 계산 경로는 생략한 기능도입니다.</desc>
<rect x="65" y="60" width="115" height="100" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="122.5" y="115.0" font-size="15" text-anchor="middle" fill="var(--ink)">블록 G/P</text><rect x="250" y="130" width="65" height="40" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="282.5" y="155.0" font-size="15" text-anchor="middle" fill="var(--ink)">AND</text><rect x="355" y="65" width="65" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="387.5" y="92.5" font-size="15" text-anchor="middle" fill="var(--ink)">OR</text><path d="M20 85 H65 M20 135 H65 M180 85 H355 M180 140 H250 M215 210 V155 H250 M315 150 H330 V95 H355 M420 87 H440" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="30" y="65" font-size="14" text-anchor="middle" fill="var(--ink)">A</text><text x="30" y="160" font-size="14" text-anchor="middle" fill="var(--ink)">B</text><text x="220" y="73" font-size="14" text-anchor="middle" fill="var(--ink)">G</text><text x="215" y="127" font-size="14" text-anchor="middle" fill="var(--ink)">P</text><text x="215" y="231" font-size="14" text-anchor="middle" fill="var(--ink)">c0</text><text x="433" y="66" font-size="14" text-anchor="middle" fill="var(--ink)">c4</text>
</svg>
<p class="diagram-caption">그림 5-3. A[3:0]·B[3:0]에서 블록 G와 P를 먼저 계산합니다. P와 입력 c0의 AND를 G와 OR하여 c4를 만듭니다. 하위 자리의 캐리와 합 계산 경로는 생략한 기능도입니다.</p>

## c1에서 c4까지 대입하여 미리보기 식 만들기

비트의 식 `c[i+1]=G_i+P_i·c[i]`에서 시작해 이전 캐리를 대입합니다. 아래 +는 모두 OR입니다.

```text
c1 = G0 + P0·c0
c2 = G1 + P1·G0 + P1·P0·c0
c3 = G2 + P2·G1 + P2·P1·G0 + P2·P1·P0·c0
c4 = G3 + P3·G2 + P3·P2·G1 + P3·P2·P1·G0
     + P3·P2·P1·P0·c0
```

예를 들어 P3·P2·G1은 bit1에서 스스로 만든 캐리를 bit2·3이 통과시키는 경우입니다. 마지막 항은 블록 밖의 c0가 네 자리 전부를 통과하는 경우입니다. c0에 붙지 않은 앞 네 항을 묶은 것이 G_3:0, c0에 붙은 계수가 P_3:0입니다. 블록 식은 외워야 할 별개 공식이 아니라 이 전개의 묶음입니다.

다른 블록의 캐리를 기다리기 전에 각 자리 A·B에서 G/P와 그 곱항을 계산할 수 있어 준비 시간을 겹칩니다. 다만 넓은 AND·OR는 실제로 여러 단계가 될 수 있고 배선도 늘어납니다. ‘식 한 줄’이 ‘게이트 한 단계’라는 뜻은 아닙니다.

## 따라 풀기

A=1011₂,B=0100₂이면 모든 자리에서 A와 B 중 하나만 1입니다. 따라서 G_3:0=0, P_3:0=1입니다. c0=0이면 c4=0이고 합은 1111, c0=1이면 c4=1이고 합은 0000입니다. 지연 예로 N=16,k=4,t_pg=60ps,t_pg_block=240ps,t_AND_OR=120ps,t_FA=180ps라 가정하면 60+240+3×120+4×180=1380ps입니다. 같은 가정의 리플 2880ps보다 짧지만 게이트와 배선 비용이 늘어납니다.

### 조건을 바꾸어 한 번 더 풀기

A=0101₂,B=0011₂,c0=0입니다. 낮은 자리부터 (G,P)는 (1,1),(0,1),(0,1),(0,0)입니다. c1=1,c2=1,c3=1이지만 bit3의 P3=0,G3=0이라 c4=0입니다. 합은 A XOR B XOR 각 입력 캐리로 구해 1000입니다.

여기서는 블록 P=0,G=0이어도 내부 c1·c2·c3는 1입니다. 블록 출력 캐리가 없다는 사실과 내부 어느 자리에서도 캐리가 없다는 말은 다릅니다. XOR형 합 계산과 OR형 전파를 구분해야 이 예제를 정확히 풀 수 있습니다.

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

### 적용 문제: 직접 구성하고 이유 설명하기

A=1000,B=1000에서 G_3:0,P_3:0과 c4를 구하세요. c0가 0과 1일 때 c4가 같은 이유를 전개식의 항으로 설명하고 전체 합도 비교하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>bit3의 G3=1이고 낮은 세 자리 P는 0이므로 블록 G=1,P=0입니다. c4=1+0·c0=1입니다. 최상위 자리 자체가 캐리를 생성하므로 입력 캐리를 기다리지 않습니다.</p>
<p>c0=0이면 전체 10000, c0=1이면 10001입니다. 하위 합은 다르지만 블록 출력 캐리는 둘 다 1입니다. 생성은 ‘모든 출력이 같다’가 아니라 ‘출력 캐리가 입력 캐리와 무관하게 생김’을 뜻합니다.</p>
</details>

## 다음으로 이어가기

다음 선택 심화는 G/P를 트리로 합치는 프리픽스 덧셈기입니다. 핵심 과정은 레슨5로 이어가도 됩니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.2.1, 인쇄 pp. 239–241 / PDF pp. 260–262. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
