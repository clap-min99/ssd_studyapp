## 이번 레슨의 목표

[선택 심화] 같은32비트 값을 little-endian과 big-endian의 바이트 주소열로 나타냅니다.

## 앞에서 배운 내용

레슨4의 주소는 바이트 단위였습니다. 레슨17의 기계어 워드 표기와 바이트 저장 순서도 구별합니다.

## 낮은 주소에 어느 바이트를 먼저 둘까

엔디언(endianness)은 여러 바이트로 된 값의 바이트 순서입니다. 리틀 엔디언(little-endian)은 가장 낮은 주소에 최하위 바이트를, 빅 엔디언(big-endian)은 가장 낮은 주소에 최상위 바이트를 둡니다. 워드 값 자체의 자릿값이나 한 바이트 내부의 비트 번호를 뒤집는 규칙이 아닙니다.

값0x13579BDF를 주소0x900부터 저장하면 다음과 같습니다.

| 주소 | little-endian | big-endian |
| --- | --- | --- |
| 0x900 | DF | 13 |
| 0x901 | 9B | 57 |
| 0x902 | 57 | 9B |
| 0x903 | 13 | DF |

이 장의 프로그램 예제는 little-endian을 사용합니다. 각각의 환경에서 같은 규칙으로 저장하고 워드로 읽으면 동일한0x13579BDF를 되찾습니다. 하지만 첫 주소의 한 바이트만 읽으면 서로 다른 값을 얻습니다.

## 문자열 순서와 워드 해석은 분리하기

문자열의 첫 문자·둘째 문자는 주소가 증가하는 순서로 놓입니다. 텍스트를 통째로 역순으로 쓰는 것이 아닙니다. 파일·통신 규약이 정한 바이트 순서를 다른 엔디언의 CPU에서 워드로 해석할 때는 변환이 필요합니다. 레지스터 창에0x13579BDF가 보인다는 사실만으로 메모리 주소별 순서를 알 수는 없습니다.

<svg viewBox="0 0 480 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="c6-24-t c6-24-d">
<title id="c6-24-t">little-endian의 증가하는 네 주소: 최하위 바이트부터 저장한다.</title>
<desc id="c6-24-d">0x900 → 0xDF (비트7:0) / 0x901 → 0x9B (비트15:8) / 0x902 → 0x57 (비트23:16) / 0x903 → 0x13 (비트31:24)</desc>
<rect x="75" y="18" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="41" text-anchor="middle" font-size="14" fill="var(--ink)">0x900 → 0xDF (비트7:0)</text>
<rect x="75" y="56" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="79" text-anchor="middle" font-size="14" fill="var(--ink)">0x901 → 0x9B (비트15:8)</text>
<rect x="75" y="94" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="117" text-anchor="middle" font-size="14" fill="var(--ink)">0x902 → 0x57 (비트23:16)</text>
<rect x="75" y="132" width="330" height="34" rx="3" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="240" y="155" text-anchor="middle" font-size="14" fill="var(--ink)">0x903 → 0x13 (비트31:24)</text>
</svg>
<p class="diagram-caption">그림 6-24. little-endian의 증가하는 네 주소: 최하위 바이트부터 저장한다. 자체 개념도이며 실제 회로 배치도가 아닙니다.</p>

## 따라 풀기

little-endian 메모리0x900–0x903에[DF,9B,57,13]이 있습니다. LW 복원값은0xDF+(0x9B<<8)+(0x57<<16)+(0x13<<24)=0x13579BDF입니다. LBU로0x901만 읽으면0x9B=155,LB는0xFFFFFF9B=−101입니다.

같은 네 바이트를 big-endian 워드로 잘못 읽으면0xDF9B5713입니다. 반면 문자열 바이트[0x47,0x4F,0]을 주소순으로 읽으면 어느 경우든 'G','O',널입니다. 그 세 바이트를 문자열로 읽는 것과 여러 바이트 정수로 묶는 것은 다릅니다.

## 헷갈리기 쉬운 점

엔디언과 signed 여부는 독립적입니다. 먼저 바이트 순서로 비트 패턴을 복원한 뒤 필요하면 signed로 해석합니다. RISC-V의 명령어 인출 바이트 규칙까지 데이터 big-endian 표를 그대로 확장하지 않으며 여기의 예제는 little-endian으로 한정합니다.

## 직접 확인하기

1. 0x01020304를 little-endian으로 저장한 첫 바이트는?
2. 주소순 바이트[01,02,03,04]를 little-endian 워드로 읽으면?
3. 엔디언이 바뀌면0x80 한 바이트의 비트도 뒤집히나요?

<details>
<summary>정답과 해설 보기</summary>
<p>1. 0x04입니다.</p>
<p>2. 0x04030201입니다.</p>
<p>3. 아닙니다. 바이트 내부 값은0x80 그대로입니다.</p>
</details>

## 다음으로 이어가기

정상 실행이 중단되는 경우에는 별도의 PC·원인·보존 상태가 필요합니다.

## 참고 범위

Harris & Harris, 《Digital Design and Computer Architecture, RISC-V Edition》, §6.6.1, 인쇄 pp. 355–356 / PDF pp. 376–377. 설명·도식·수치 예제·확인 문제는 자체 구성입니다. 
