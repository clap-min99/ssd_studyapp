## 이번 레슨의 목표

DRAM의 복원·refresh와 SRAM의 정적 유지 원리를 설명하고 셀·면적·지연의 비교 조건을 구별합니다.

## 앞에서 배운 내용

1장의 커패시터와 MOS 스위치, 3장의 교차 결합 피드백이 메모리 셀에서 다시 등장합니다.

## 저장 방식이 읽기와 유지 비용을 바꾼다

대표 DRAM 셀은 접근 트랜지스터 한 개와 커패시터 한 개(1T1C)입니다. wordline이 접근 스위치를 열면 저장 노드와 bitline이 연결됩니다. 저장 전하는 누설로 줄어들고, 읽기에서도 전하 공유로 저장 상태가 영향을 받으므로 감지 후 다시 써서 복원합니다. 접근하지 않아도 주기적 refresh가 필요합니다. 실제 bitline은 적절히 precharge하고 작은 전압 차를 감지하므로 셀이 긴 bitline을 즉시 완전한 0·1로 구동한다고 단순화하지 않습니다.

대표 6T SRAM 셀은 두 인버터의 피드백 4개 소자와 두 접근 트랜지스터로 구성합니다. wordline이 활성화되면 서로 보수인 두 저장 노드가 두 bitline에 연결됩니다. 전원이 있고 정상 유지 조건을 만족하면 피드백이 상태를 복원하므로 DRAM처럼 주기적 refresh를 요구하지 않습니다. 쓰기는 접근 경로가 기존 피드백 상태를 바꿀 수 있게 설계합니다.

| 항목 | DRAM | SRAM |
| --- | --- | --- |
| 대표 셀 | 1T+1C | 6T |
| 저장 원리 | 전하 | 쌍안정 피드백 |
| 주기적 refresh | 필요 | 불필요 |
| 전원 제거 | 데이터 소실 | 데이터 소실 |

플립플롭은 출력이 바로 나오는 작은 저장에, SRAM은 비교적 빠른 배열 접근에, DRAM은 높은 집적도에 적합한 경향이 있습니다. 공정·포트·용량·주변 회로·부하가 다르면 면적과 지연도 바뀝니다. 1T와 6T만으로 칩 전체 면적 비율을 1:6이라 계산하지 않습니다.

보충 개념으로 SDRAM은 접근을 클록에 맞추고 DDR은 양 에지를 활용해 전송률을 높입니다. 핀 전송률, 한 요청의 지연, refresh 비용은 다른 지표입니다. 특정 세대의 현재 최고 속도나 가격은 이 기초 레슨 범위에 포함하지 않습니다.

<svg viewBox="0 0 450 405" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c5-19-study-t c5-19-study-d">
<title id="c5-19-study-t">DRAM의 접근 스위치와 SRAM의 피드백 저장</title>
<desc id="c5-19-study-d">위는 wordline으로 여닫는 스위치와 저장 커패시터의 DRAM 기능도입니다. 아래 SRAM은 위 인버터의 출력 Q_bar가 아래 인버터의 입력으로,아래 출력 Q가 위 입력으로 돌아갑니다. 두 접근 스위치는 같은 wordline을 공유합니다. 인버터·스위치 기능 블록으로 그렸습니다.</desc>
<text x="60" y="25" font-size="16" text-anchor="middle" fill="var(--ink)">DRAM</text><path d="M70 70 H140 M225 70 H305 V105 M290 105 H320 M290 115 H320 M305 115 V143 M292 143 H318" fill="none" stroke="var(--ink)" stroke-width="2"/><rect x="140" y="48" width="85" height="42" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="182.5" y="74.0" font-size="15" text-anchor="middle" fill="var(--ink)">접근 S</text><text x="182" y="25" font-size="14" text-anchor="middle" fill="var(--ink)">wordline</text><path d="M182 30 V48" fill="none" stroke="var(--ink)" stroke-width="2"/><text x="55" y="95" font-size="14" text-anchor="middle" fill="var(--ink)">bitline</text><text x="352" y="115" font-size="15" text-anchor="middle" fill="var(--ink)">저장 C</text><text x="60" y="190" font-size="16" text-anchor="middle" fill="var(--ink)">SRAM</text><rect x="75" y="280" width="80" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="115.0" y="307.5" font-size="15" text-anchor="middle" fill="var(--ink)">접근 S</text><rect x="210" y="220" width="70" height="35" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="245.0" y="242.5" font-size="15" text-anchor="middle" fill="var(--ink)">NOT</text><rect x="210" y="285" width="70" height="35" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="245.0" y="307.5" font-size="15" text-anchor="middle" fill="var(--ink)">NOT</text><rect x="350" y="215" width="80" height="45" rx="5" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/><text x="390.0" y="242.5" font-size="15" text-anchor="middle" fill="var(--ink)">접근 S</text><path d="M20 302 H75 M155 302 H210 M185 302 V237 H210 M280 237 H350 M320 237 V302 H280 M430 237 H445 M115 205 V280 M390 205 V215 M115 205 H390" fill="none" stroke="var(--ink)" stroke-width="2"/><circle cx="185" cy="302" r="3" fill="var(--ink)"/><circle cx="320" cy="237" r="3" fill="var(--ink)"/><text x="250" y="196" font-size="14" text-anchor="middle" fill="var(--ink)">wordline</text><text x="34" y="335" font-size="14" text-anchor="middle" fill="var(--ink)">BL</text><text x="413" y="285" font-size="14" text-anchor="middle" fill="var(--ink)">BL_bar</text><text x="180" y="345" font-size="14" text-anchor="middle" fill="var(--ink)">Q</text><text x="320" y="222" font-size="13" text-anchor="middle" fill="var(--ink)">Q_bar</text><text x="225" y="380" font-size="13" text-anchor="middle" fill="var(--ink)">두 인버터의 CMOS 소자 4개 + 접근 소자 2개 = 6T</text>
</svg>
<p class="diagram-caption">그림 5-19. 위는 wordline으로 여닫는 스위치와 저장 커패시터의 DRAM 기능도입니다. 아래 SRAM은 위 인버터의 출력 Q_bar가 아래 인버터의 입력으로,아래 출력 Q가 위 입력으로 돌아갑니다. 두 접근 스위치는 같은 wordline을 공유합니다. 인버터·스위치 기능 블록으로 그렸습니다.</p>

## 셀을 실제로 읽고 쓰는 순서로 이해하기

DRAM 읽기는 bitline을 기준 전압으로 준비하고,선택 wordline을 켜 저장 커패시터와 연결한 다음 작은 전압 변화를 감지합니다. 저장 커패시터의 전하가 bitline과 나뉘므로 읽기 전의 강한 저장 상태가 그대로 남는다고 볼 수 없습니다. 감지 증폭기가 0·1을 판정하고 충분한 상태로 복원하는 단계까지 필요합니다. 저장 1을 읽는다고 커패시터가 긴 선을 곧바로 전원 전압으로 올리는 것은 아닙니다.

DRAM 쓰기는 원하는 값을 bitline 쪽에 마련한 뒤 wordline을 켜 커패시터를 충전하거나 방전합니다. wordline을 끄면 저장 노드는 격리되지만 누설은 계속됩니다. 따라서 읽은 행의 복원과,오랫동안 읽지 않은 행도 유지하기 위한 refresh는 목적이 다른 동작입니다.

SRAM은 내부 Q·Q_bar의 교차 결합이 두 안정 상태를 만듭니다. wordline이 꺼져도 전원이 있는 동안 두 인버터가 서로를 유지합니다. 읽기는 준비된 두 bitline 중 저장 상태에 따라 달라지는 쪽을 감지하고,쓰기는 bitline 쌍을 목표 값으로 강하게 구동해 내부 상태를 바꿉니다. 접근 소자와 피드백의 세기는 읽을 때는 상태를 해치지 않고 쓸 때는 바꿀 수 있도록 설계되어야 합니다. 여기서는 이 정성적 조건까지만 다룹니다.

## 따라 풀기

대표 셀만 비교하는 교육용 계산에서 16비트 SRAM은 16×6=96개 트랜지스터, DRAM은 16개 트랜지스터와 16개 커패시터입니다. 주소 디코더·감지 증폭기·쓰기 드라이버·refresh 제어는 제외했습니다. 따라서 이 숫자는 실제 배열의 총 소자 수가 아닙니다. DRAM을 한 번 읽었다면 같은 데이터를 계속 보존하려고 감지한 내용을 복원해야 하며, 읽지 않은 행도 주기적으로 관리해야 합니다.

### 조건을 바꾸어 한 번 더 풀기

‘1을 저장했다가 읽은 뒤에도 1을 보존’하는 과정을 비교합니다.

| 단계 | DRAM | SRAM |
| --- | --- | --- |
| 접근 전 | 전하가 1을 나타냄 | Q=1,Q_bar=0의 피드백 유지 |
| 선택 | wordline이 커패시터를 선에 연결 | 접근 트랜지스터가 저장 노드를 선 쌍에 연결 |
| 읽기 | 작은 전압 차를 감지 | bitline 쌍의 차이를 감지 |
| 보존 | 감지한 값을 다시 복원 | 정상 읽기 조건에서 내부 피드백 유지 |
| 장시간 대기 | 누설 때문에 refresh 필요 | 전원 유지 시 주기적 refresh 불필요 |

둘 다 전원이 사라지면 일반 셀의 데이터 유지 계약은 없습니다. ‘SRAM은 static’과 ‘ROM은 nonvolatile’을 같은 뜻으로 사용하지 않습니다.

## 헷갈리기 쉬운 점

SRAM의 static은 전원을 꺼도 남는다는 뜻이 아닙니다. refresh가 필요 없다는 말과 오류가 절대 없다는 말도 다릅니다. DRAM의 파괴적 읽기는 사용자 프로그램이 매번 내용을 잃는다는 뜻이 아니라 내부에서 복원한다는 뜻입니다.

## 직접 확인하기

1. SRAM에 refresh가 없는 이유는?
2. DRAM 읽기 뒤 왜 복원하나요?
3. DDR 전송률 두 배가 접근 지연 절반을 보장하나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 전원이 유지되는 동안 피드백이 안정 상태를 능동 유지하기 때문입니다.</p>
<p>2. 전하 공유 등으로 저장 노드가 영향을 받기 때문입니다.</p>
<p>3. 아닙니다. 전송률과 요청 지연은 다른 지표입니다.</p>
</details>

### 적용 문제: 직접 구성하고 이유 설명하기

DRAM에서 프로그램이 한 행을 계속 읽는 동안 다른 행은 전혀 읽지 않습니다. 읽은 행의 복원만 수행하면 전체 데이터가 유지되나요? SRAM과 비교해 설명하세요.

<details>
<summary>적용 문제 풀이와 검산</summary>
<p>아닙니다. 읽지 않은 행의 커패시터 전하도 누설됩니다. 읽은 행의 복원과 별개로 보존 요구 시간 안에 다른 행도 refresh해야 합니다.</p>
<p>SRAM은 전원이 유지되고 정상 조건이면 셀 피드백이 상태를 유지하므로 같은 주기적 refresh가 필요하지 않습니다. 다만 전원 제거·잡음·결함 등의 문제까지 없는 것은 아닙니다.</p>
</details>

## 다음으로 이어가기

다음에는 여러 주소를 동시에 읽는 작은 레지스터 파일을 봅니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §5.5.2–5.5.4, 인쇄 pp. 267–269 / PDF pp. 288–290. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. HDL 예제는 SystemVerilog입니다.
