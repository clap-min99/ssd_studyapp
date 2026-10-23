## 이번 레슨의 목표

논리 요소의 조합·저장 경로를 설명하고 LUT 분해와 레지스터 사이의 타이밍 예산을 계산합니다.

## 앞에서 배운 내용

LUT는 함수를 표로, 플립플롭은 상태를 저장했습니다. FPGA는 이런 작은 블록과 연결 경로를 재설정해 큰 회로를 구성합니다.

## 설정 비트가 기능과 배선을 결정한다

FPGA(field programmable gate array)는 설정 가능한 논리 요소와 라우팅, 입출력 요소를 포함합니다. 교육용 논리 요소를 ‘4입력·1출력 LUT 한 개와 플립플롭 한 개, 출력 bypass MUX’로 가정합니다. LUT 결과를 바로 내면 조합 함수이고 플립플롭을 거치면 에지에서 저장된 함수입니다. 실제 제품은 LUT 크기·분할·캐리 체인·RAM·DSP·클록 자원이 다르므로 이 모델의 개수를 모든 장치에 적용하지 않습니다.

4입력 LUT는 입력 조합 16개의 출력 비트를 설정합니다. 입력이 네 개보다 많은 함수는 중간 함수를 만들어 여러 LUT로 나눌 수 있습니다. 예를 들어 6입력 AND는 t=A·B·C·D, Y=t·E·F로 두 4입력 LUT에 들어갑니다. 한 LUT의 출력은 다음 LUT 입력으로 배선을 통해 연결됩니다.

FSM에서는 LUT가 다음 상태 함수, 플립플롭이 현재 상태를 맡고 그 출력이 LUT 입력으로 돌아갑니다. 필요한 상태 비트 수만큼 저장 자원이 필요하지만, 다음 상태·출력이 복잡하면 추가 LUT가 필요합니다. 전용 캐리 체인은 덧셈기의 매 비트를 일반 LUT 여러 개로 분해하는 것보다 효율적으로 처리할 수 있습니다.

구현 흐름은 HDL 기능 확인 → 합성 → 배치·배선 → 타이밍 분석 → 설정 데이터 생성입니다. SRAM으로 설정을 저장하는 장치는 전원을 끄면 설정을 잃어 다시 로드해야 합니다. Flash나 다른 설정 방식도 있으므로 FPGA 전체를 같은 휘발성으로 일반화하지 않습니다. 여기서는 특정 보드·현재 제품 추천 대신 회로 구조를 학습합니다.

<svg viewBox="0 0 446 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-24-t c5-24-d">
<title id="c5-24-t">FPGA: LUT·플립플롭·배선으로 회로 배치하기</title>
<desc id="c5-24-d">교육용 FPGA 논리 요소의 핵심 역할을 비교한 개념도입니다. 특정 제조사 셀의 실제 도면은 아닙니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)"><rect x="12" y="25" width="126" height="90" rx="7"/><rect x="160" y="25" width="126" height="90" rx="7"/><rect x="308" y="25" width="126" height="90" rx="7"/></g>
<g fill="var(--ink)" font-size="14" text-anchor="middle"><text x="75" y="59">LUT</text><text x="75" y="87">현재 입력의 함수</text><text x="223" y="59">플립플롭</text><text x="223" y="87">에지의 상태 저장</text><text x="371" y="59">라우팅·MUX</text><text x="371" y="87">연결·출력 경로 설정</text></g>
</svg>
<p class="diagram-caption">그림 5-24a. 교육용 FPGA 논리 요소의 핵심 역할을 비교한 개념도입니다. 특정 제조사 셀의 실제 도면은 아닙니다.</p>

<svg viewBox="0 0 460 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-24b-t c5-24b-d">
<title id="c5-24b-t">LUT 출력과 등록 출력을 선택하는 교육용 논리 요소</title>
<desc id="c5-24b-d">입력 네 개가 LUT에 들어갑니다. LUT 출력은 한 갈래로 플립플롭 D에 연결되고 다른 갈래로 출력 MUX의 조합 입력에 직접 연결됩니다. 플립플롭 Q는 MUX의 등록 입력에 연결됩니다. 설정 비트가 두 경로를 선택합니다.</desc>
<g fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"><rect x="70" y="80" width="95" height="90"/><rect x="225" y="120" width="75" height="65"/><rect x="350" y="65" width="65" height="120"/></g>
<g fill="none" stroke="var(--ink)" stroke-width="2"><path d="M20 97 H70 M20 115 H70 M20 133 H70 M20 151 H70 M165 140 H225 M195 140 V90 H350 M300 150 H350 M415 125 H445 M260 220 V185 M250 185 L260 173 L270 185 M382 30 V65"/></g>
<g fill="var(--ink)"><circle cx="195" cy="140" r="3"/></g>
<g fill="var(--ink)" font-size="15" text-anchor="middle"><text x="117" y="120">4입력</text><text x="117" y="145">LUT</text><text x="262" y="146">FF</text><text x="382" y="130">MUX</text><text x="276" y="78">직접 경로</text><text x="320" y="174">Q</text><text x="229" y="163">D</text><text x="260" y="241">clk</text><text x="382" y="20">설정 비트</text><text x="442" y="113">Y</text></g>
</svg>
<p class="diagram-caption">그림 5-24b. LUT의 조합 출력과 플립플롭을 거친 출력을 선택하는 기능 회로입니다. 설정 비트는 이 예제에서 사용자가 매 주기 바꾸는 데이터 입력과 구별합니다.</p>

## 따라 풀기

6입력 AND의 두 LUT 연결에서 A,B,C,D가 모두 1이면 t=1이고 E=1,F=0이면 Y=0입니다. 타이밍은 주기 4ns,t_pcq=0.20ns,t_setup=0.10ns,스큐=0이라고 가정합니다. 각 LUT와 그 뒤 배선의 합산 지연을 0.55ns로 가정하면 L단계에 0.20+0.55L+0.10≤4가 필요합니다. L≤6.727이므로 최대 6단계이며 7단계는 4.15ns로 실패합니다. 모델 밖의 별도 배선 지연을 또 더하거나 중복 계산하지 않습니다.

## 헷갈리기 쉬운 점

논리 요소 수만으로 속도를 예측하지 않습니다. 긴 라우팅과 팬아웃도 지연을 만듭니다. 합성 통과는 배치·배선 타이밍 통과와 다릅니다. 레지스터를 추가하는 파이프라인은 주기뿐 아니라 지연·제어 정렬 명세도 바꿉니다.

## 직접 확인하기

1. 4입력 LUT의 표 내용 비트 수는?
2. 등록 출력과 bypass 출력의 차이는?
3. 예제 6단계의 최소 주기는?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 16비트입니다.</p>
<p>2. 등록 출력은 플립플롭 에지에서 저장되고 bypass는 조합 경로로 바로 나옵니다.</p>
<p>3. 0.20+6×0.55+0.10=3.60ns입니다.</p>
</details>

## 다음으로 이어가기

다음 선택 심화에서는 ROM·PLA 배열을 소자 수준으로 구현할 때의 반전 관계를 봅니다. 핵심 과정은 레슨26 종합으로 이어갑니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.6.2, 인쇄 pp. 276–282 / PDF pp. 297–303. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
