from django.core.management.base import BaseCommand
from digest.models import Tag, Lesson

# (order, title, body) — 챕터(Tag) 하나를 여러 하위 레슨으로 쪼갤 때 여기에 채운다.
LESSON_PAGES = {
    "nand": [
        (1, "NAND 셀 하나의 구조", """이 트랙 전체가 결국 셀 하나의 물리적 동작에서 출발하므로, 가장 작은 단위부터 정확히 봐야 합니다.

## 셀은 스위치이자 기억소자다
NAND 셀은 기본적으로 트랜지스터입니다. 트랜지스터는 게이트에 전압을 걸면 소스-드레인 사이로 전류가 흐르는 스위치인데, NAND 셀은 이 게이트를 두 겹으로 만들어 "전류가 흐르는 문턱값 자체를 바꿀 수 있는" 스위치로 개조한 것입니다.

<svg viewBox="0 0 420 220" xmlns="http://www.w3.org/2000/svg">
  <rect x="60" y="14" width="300" height="34" fill="var(--accent)" rx="4"/>
  <text x="210" y="36" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">컨트롤 게이트 (Control Gate)</text>
  <rect x="60" y="48" width="300" height="12" fill="var(--border)"/>
  <text x="210" y="58" text-anchor="middle" fill="var(--muted)" font-size="9">절연막 (ONO)</text>
  <rect x="60" y="60" width="300" height="36" fill="var(--accent-soft)"/>
  <text x="210" y="80" text-anchor="middle" fill="#1c4a44" font-size="12" font-weight="700">플로팅 게이트 / 전하 트랩층</text>
  <circle cx="130" cy="90" r="3.5" fill="var(--accent)"/>
  <circle cx="155" cy="90" r="3.5" fill="var(--accent)"/>
  <circle cx="180" cy="90" r="3.5" fill="var(--accent)"/>
  <circle cx="245" cy="90" r="3.5" fill="var(--accent)"/>
  <circle cx="270" cy="90" r="3.5" fill="var(--accent)"/>
  <circle cx="295" cy="90" r="3.5" fill="var(--accent)"/>
  <rect x="60" y="96" width="300" height="12" fill="var(--border)"/>
  <text x="210" y="106" text-anchor="middle" fill="var(--muted)" font-size="9">터널 산화막 (Tunnel Oxide)</text>
  <rect x="60" y="108" width="300" height="70" fill="#e9eaec" rx="4"/>
  <rect x="75" y="126" width="60" height="35" fill="#c9ccd1" rx="3"/>
  <text x="105" y="148" text-anchor="middle" font-size="11" fill="var(--ink)">Source</text>
  <rect x="285" y="126" width="60" height="35" fill="#c9ccd1" rx="3"/>
  <text x="315" y="148" text-anchor="middle" font-size="11" fill="var(--ink)">Drain</text>
  <text x="210" y="170" text-anchor="middle" font-size="10" fill="var(--muted)">채널 (Substrate)</text>
  <text x="10" y="200" font-size="10" fill="var(--muted)">● = 플로팅 게이트/전하 트랩층에 갇힌 전자. 전자 개수가 많을수록 문턱전압이 높아진다.</text>
</svg>
<p class="diagram-caption">그림 1-1. NAND 셀의 기본 단면 구조</p>

## 두 가지 구현 방식: 플로팅 게이트 vs 전하 트랩
전자를 가두는 층을 어떤 재질로 만드느냐에 따라 두 갈래로 나뉩니다.

- **플로팅 게이트(Floating Gate)**: 도체(폴리실리콘)로 된 층에 전자를 가둡니다. 도체이기 때문에 전자가 층 전체에 고르게 퍼지고, 절연막에 미세한 결함이 하나만 생겨도 전자가 그 구멍으로 전부 빠져나갈 위험이 있습니다.
- **전하 트랩(Charge Trap Flash, CTF)**: 질화막(SiN) 같은 절연체에 전자를 가둡니다. 절연체이므로 전자가 국소적인 트랩 지점에 각각 갇혀서, 결함이 하나 생겨도 그 주변 전자만 새어나가고 전체가 무너지지 않습니다. 최근 3D NAND는 거의 전량 이 CTF 방식입니다 — 뒤에서 볼 3D 구조(5강)의 수직 적층 공정에 CTF가 훨씬 유리하기 때문입니다.

## 읽기 동작: 전류로 0과 1을 구분한다
셀을 읽을 때는 컨트롤 게이트에 특정 전압(읽기 전압)을 걸고, 소스-드레인 사이에 전류가 흐르는지를 봅니다. 갇힌 전자가 많으면(문턱전압이 높으면) 같은 읽기 전압으로는 전류가 잘 안 흐르고, 전자가 적으면(문턱전압이 낮으면) 전류가 흐릅니다. 컨트롤러의 센스 앰프(sense amplifier)가 이 미세한 전류 차이를 감지해 0인지 1인지 판정합니다. 다음 레슨에서 이 "문턱전압 축"을 몇 개의 구간으로 나누느냐가 왜 셀당 비트 수를 결정하는지 이어서 봅니다."""),

        (2, "셀당 비트 수: SLC부터 PLC까지, 그리고 그 대가", """1강에서 "문턱전압이 높을수록 전자가 많이 갇힌 것"이라고 배웠습니다. 이 문턱전압 축을 몇 개의 구간으로 쪼개느냐가 셀 하나에 몇 비트를 저장할지를 정합니다.

## 구간을 쪼갤수록 비트가 늘어난다
구간이 2개면 1비트(0 또는 1), 4개면 2비트, 8개면 3비트를 표현할 수 있습니다 — 구간 수가 2ⁿ이면 n비트입니다.

<svg viewBox="0 0 420 200" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="16" font-size="11" fill="var(--ink)" font-weight="700">SLC — 1bit/cell (2단계)</text>
  <rect x="10" y="22" width="190" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <line x1="105" y1="22" x2="105" y2="46" stroke="var(--accent)" stroke-width="2"/>
  <text x="10" y="74" font-size="11" fill="var(--ink)" font-weight="700">TLC — 3bit/cell (8단계)</text>
  <rect x="10" y="80" width="190" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <line x1="33" y1="80" x2="33" y2="104" stroke="var(--accent)" stroke-width="1"/>
  <line x1="57" y1="80" x2="57" y2="104" stroke="var(--accent)" stroke-width="1"/>
  <line x1="81" y1="80" x2="81" y2="104" stroke="var(--accent)" stroke-width="1"/>
  <line x1="105" y1="80" x2="105" y2="104" stroke="var(--accent)" stroke-width="1"/>
  <line x1="129" y1="80" x2="129" y2="104" stroke="var(--accent)" stroke-width="1"/>
  <line x1="153" y1="80" x2="153" y2="104" stroke="var(--accent)" stroke-width="1"/>
  <line x1="177" y1="80" x2="177" y2="104" stroke="var(--accent)" stroke-width="1"/>
  <text x="10" y="132" font-size="11" fill="var(--ink)" font-weight="700">QLC — 4bit/cell (16단계, 여백이 더 좁다)</text>
  <rect x="10" y="138" width="190" height="24" fill="#fbeaea" stroke="#c0392b"/>
  <line x1="22" y1="138" x2="22" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="34" y1="138" x2="34" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="46" y1="138" x2="46" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="58" y1="138" x2="58" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="70" y1="138" x2="70" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="82" y1="138" x2="82" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="94" y1="138" x2="94" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="106" y1="138" x2="106" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="118" y1="138" x2="118" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="130" y1="138" x2="130" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="142" y1="138" x2="142" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="154" y1="138" x2="154" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="166" y1="138" x2="166" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="178" y1="138" x2="178" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <line x1="190" y1="138" x2="190" y2="162" stroke="#c0392b" stroke-width="0.7"/>
  <text x="10" y="188" font-size="9" fill="var(--muted)">문턱전압(threshold voltage) 축 — 같은 폭을 더 잘게 쪼갤수록 구간 사이 여백이 좁아져 오독 확률이 오른다</text>
</svg>
<p class="diagram-caption">그림 2-1. 셀당 비트 수에 따른 문턱전압 구간 비교</p>

## 등급별 실측 대략치
- **SLC**(1bit/cell): P/E 사이클 약 6만\~10만 회. 가장 빠르고 오래 쓰지만 셀당 원가가 가장 비쌈
- **MLC**(2bit/cell): 약 3천\~1만 회
- **TLC**(3bit/cell): 약 1천\~3천 회. 현재 소비자용 SSD 주류
- **QLC**(4bit/cell): 약 100\~1천 회. 같은 실리콘 면적에서 원가가 가장 낮아 서버·데이터센터의 대용량 SSD에 채택 확대 중
- **PLC**(5bit/cell): 구간이 32개까지 촘촘해져 여백이 극도로 좁음. 아직 양산 초기 단계

## 왜 여백이 좁아지면 위험한가
문턱전압 전체 범위는 셀이 버틸 수 있는 전압 한계로 정해져 있어 거의 고정입니다. 그 안에 들어가는 구간 수만 늘어나니, 구간 하나의 폭(여백)은 비트 수가 늘수록 좁아질 수밖에 없습니다. 3강에서 볼 P/E 사이클 누적이나 시간 경과로 전자가 조금만 새어나가도, 좁은 여백에서는 옆 구간으로 값이 넘어가버려 오독이 생깁니다. QLC/PLC가 실제 제품으로 나올 수 있는 건, 이 오독을 컨트롤러가 강력한 ECC(5챕터에서 다룸)로 정정해주기 때문입니다.

다음 레슨에서는 애초에 왜 이 문턱전압이 바뀌는지 — 즉 쓰기(Program)와 지우기(Erase)가 셀을 어떻게 물리적으로 마모시키는지를 봅니다."""),

        (3, "P/E 사이클과 마모의 물리학", """1\~2강에서 "전자가 갇힌 개수가 곧 문턱전압"이라고 배웠습니다. 이 전자를 실제로 넣고 빼는 과정이 Program(쓰기)과 Erase(지우기)이고, 이 과정 자체가 셀을 조금씩 망가뜨립니다.

## 터널링: 절연막을 억지로 통과시키기
플로팅 게이트/전하 트랩층은 절연막으로 둘러싸여 있어 전자가 원래는 드나들 수 없습니다. NAND는 **파울러-노드하임 터널링(Fowler-Nordheim tunneling)** 이라는 양자역학적 현상을 이용해 이 절연막을 억지로 통과시킵니다 — 게이트에 아주 높은 전압을 걸면, 절연막이 얇다는 조건 아래에서 전자가 마치 벽을 뚫듯이 반대편으로 건너갑니다.

- **Program(쓰기)**: 컨트롤 게이트에 높은 양(+)의 전압을 걸어, 채널 쪽 전자를 플로팅 게이트/전하 트랩층 쪽으로 끌어올립니다. 전자가 들어갈수록 문턱전압이 높아집니다.
- **Erase(지우기)**: 반대로 기판(벌크) 쪽에 높은 양의 전압을 걸어, 갇혀 있던 전자를 채널 쪽으로 빼냅니다. 전자가 빠질수록 문턱전압이 낮아져 초기 상태로 돌아갑니다.

<svg viewBox="0 0 420 150" xmlns="http://www.w3.org/2000/svg">
  <rect x="60" y="10" width="300" height="30" fill="var(--accent)" rx="4"/>
  <text x="210" y="30" text-anchor="middle" fill="#fff" font-size="11" font-weight="700">컨트롤 게이트</text>
  <rect x="60" y="40" width="300" height="10" fill="var(--border)"/>
  <rect x="60" y="50" width="300" height="30" fill="var(--accent-soft)"/>
  <text x="210" y="70" text-anchor="middle" fill="#1c4a44" font-size="11" font-weight="700">전하 트랩층</text>
  <rect x="60" y="80" width="300" height="10" fill="var(--border)"/>
  <text x="210" y="88" text-anchor="middle" fill="#8a6d00" font-size="9" font-weight="700">← 터널 산화막: 매 사이클 손상 누적 →</text>
  <rect x="60" y="90" width="300" height="40" fill="#e9eaec" rx="3"/>
  <text x="210" y="114" text-anchor="middle" fill="var(--muted)" font-size="10">채널 / 기판</text>
  <line x1="150" y1="126" x2="150" y2="55" stroke="var(--accent)" stroke-width="2"/>
  <path d="M150,55 l-5,10 l10,0 z" fill="var(--accent)"/>
  <text x="150" y="145" text-anchor="middle" font-size="9" fill="var(--accent)">Program: 전자 주입</text>
  <line x1="290" y1="55" x2="290" y2="126" stroke="#c0392b" stroke-width="2"/>
  <path d="M290,126 l-5,-10 l10,0 z" fill="#c0392b"/>
  <text x="290" y="145" text-anchor="middle" font-size="9" fill="#c0392b">Erase: 전자 방출</text>
</svg>
<p class="diagram-caption">그림 3-1. Program(전자 주입)과 Erase(전자 방출) 시 터널링 방향</p>

## 왜 반복할수록 셀이 죽는가
전자가 터널 산화막을 강제로 통과할 때마다, 산화막 안에 미세한 결함(트랩)이 조금씩 쌓입니다. 이 결함들은 두 가지 문제를 일으킵니다.

1. **누설 경로가 생긴다**: 결함이 쌓이면 전자가 의도치 않게 조금씩 새어나가기 쉬워져, 2강에서 본 좁은 문턱전압 구간을 넘나드는 오독이 늘어납니다.
2. **쓰기/지우기 속도 자체가 느려진다**: 결함이 전자 이동을 방해해서, 같은 전압으로 원하는 문턱전압까지 도달하는 데 시간이 더 걸립니다.

이 손상이 임계치를 넘으면 셀이 더 이상 값을 안정적으로 유지하지 못하는데, 이게 바로 **P/E 사이클 한계**이고 2강에서 본 등급별 수치(SLC 6만\~10만 회 vs QLC 100\~1천 회)의 물리적 근거입니다. 셀당 비트 수가 많을수록 여백이 좁아 결함에 더 취약하기 때문에, 등급이 올라갈수록(SLC→QLC) 견딜 수 있는 사이클 수가 급격히 줄어드는 것입니다.

다음 레슨에서는 이 Program/Erase가 왜 "쓰기는 좁은 단위로, 지우기는 넓은 단위로만" 가능한지 — 즉 페이지와 블록 구조를 봅니다."""),

        (4, "페이지, 블록, 플레인, 다이 — 쓰기와 지우기 단위가 다른 이유", """3강에서 Program(쓰기)과 Erase(지우기)가 전자를 반대 방향으로 움직이는 별개의 동작이라는 걸 봤습니다. 이 두 동작은 실제로 걸리는 전압 회로 구조 자체가 달라서, 적용되는 범위(단위)도 다릅니다.

## 계층 구조: 셀에서 다이까지
NAND는 셀 하나하나가 독립적으로 관리되지 않고, 아래와 같은 계층으로 묶여서 관리됩니다.

<svg viewBox="0 0 440 190" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="20" width="90" height="140" fill="none" stroke="var(--border)" stroke-width="2" rx="4"/>
  <text x="55" y="15" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">다이(Die)</text>
  <rect x="20" y="30" width="35" height="60" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="20" y="95" width="35" height="60" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="60" y="30" width="35" height="60" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="60" y="95" width="35" height="60" fill="#f0f1f3" stroke="var(--border)"/>
  <path d="M105,60 L143,60" stroke="var(--muted)" stroke-width="1.5"/>
  <path d="M143,60 l-6,-5 l0,10 z" fill="var(--muted)"/>
  <rect x="150" y="30" width="90" height="120" fill="none" stroke="var(--border)" stroke-width="2" rx="4"/>
  <text x="195" y="20" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">플레인(Plane)</text>
  <rect x="158" y="38" width="32" height="34" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="198" y="38" width="32" height="34" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="158" y="76" width="32" height="34" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="198" y="76" width="32" height="34" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="158" y="114" width="32" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="198" y="114" width="32" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <path d="M245,60 L283,60" stroke="var(--muted)" stroke-width="1.5"/>
  <path d="M283,60 l-6,-5 l0,10 z" fill="var(--muted)"/>
  <rect x="290" y="20" width="140" height="140" fill="none" stroke="var(--accent)" stroke-width="2" rx="4"/>
  <text x="360" y="15" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">블록(Block)</text>
  <rect x="298" y="28" width="124" height="18" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="360" y="41" text-anchor="middle" font-size="8" fill="#1c4a44">페이지(Page) — 쓰기 단위</text>
  <rect x="298" y="50" width="124" height="18" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="298" y="72" width="124" height="18" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="298" y="94" width="124" height="18" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="298" y="116" width="124" height="18" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="298" y="138" width="124" height="18" fill="#f0f1f3" stroke="var(--border)"/>
  <text x="360" y="173" text-anchor="middle" font-size="9" fill="var(--accent)" font-weight="700">블록 전체가 지우기 단위</text>
</svg>
<p class="diagram-caption">그림 4-1. 다이 → 플레인 → 블록 → 페이지 계층 구조</p>

셀 여러 개가 한 줄로 묶여 **워드라인(word line)** 을 공유하고, 이 워드라인 하나가 곧 **페이지(Page, 보통 4\~16KB)** 입니다. 페이지 수백 개가 모여 **블록(Block)** 이 되고, 블록 여러 개가 **플레인(Plane)**, 플레인 여러 개가 **다이(Die)** 하나를 이룹니다.

## 왜 쓰기는 페이지 단위인가
Program 동작은 워드라인(=페이지) 하나에 전압을 걸어 그 줄에 있는 셀들에만 전자를 주입합니다. 워드라인이 다르면 회로가 분리돼 있어, 자연스럽게 "전압을 건 그 페이지만" 쓰기가 적용됩니다. 그래서 쓰기는 페이지 단위로 세밀하게 할 수 있습니다.

## 왜 지우기는 블록 단위인가
Erase 동작은 반대로 기판(벌크, 웰) 쪽에 전압을 겁니다. 그런데 이 벌크는 페이지별로 분리돼 있지 않고 블록 안의 모든 페이지가 같은 벌크를 공유합니다. 그래서 벌크에 전압을 거는 순간, 그 블록 안의 모든 페이지가 동시에 지워집니다 — 페이지 하나만 골라서 지우는 것 자체가 회로 구조상 불가능합니다.

이 "쓰기는 좁게, 지우기는 넓게"라는 비대칭이 이 트랙 전체에서 가장 중요한 제약입니다. 이미 데이터가 있는 페이지 하나를 "수정"하려면, 사실은 다른 빈 페이지에 새로 쓰고 예전 페이지를 나중에 블록째로 지워야 합니다 — 이 처리를 누가, 어떻게 하는지가 3챕터 FTL의 핵심 주제입니다.

다음 레슨에서는 이 페이지·블록 구조를 유지하면서 집적도를 어떻게 계속 늘려왔는지 — 3D NAND의 적층 구조를 봅니다."""),

        (5, "3D NAND: 적층과 스트링 구조", """4강까지는 셀 하나, 그리고 셀들이 페이지·블록으로 묶이는 구조를 평면적으로 봤습니다. 이번 레슨은 이 평면 구조를 수직으로 쌓아 올려 같은 면적에 훨씬 많은 셀을 담는 3D NAND를 다룹니다.

## 2D NAND의 한계: 더 이상 못 좁힌다
평면(2D) NAND는 셀을 웨이퍼 표면에 나란히 배열하고, 공정 미세화(셀 간격을 줄이는 것)로 집적도를 높여왔습니다. 하지만 셀 간격이 너무 좁아지면 1강에서 본 전하 트랩층의 전자가 바로 옆 셀에 전기적 영향을 주는 **셀 간 간섭(cell-to-cell interference)** 이 심해지고, 터널 산화막을 얇게 만드는 데도 물리적 한계가 있어 2강의 좁은 문턱전압 여백 문제가 더 악화됩니다.

<svg viewBox="0 0 420 200" xmlns="http://www.w3.org/2000/svg">
  <text x="100" y="16" text-anchor="middle" font-size="11" fill="var(--ink)" font-weight="700">2D NAND (평면 배열)</text>
  <rect x="20" y="28" width="30" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="55" y="28" width="30" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="90" y="28" width="30" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="125" y="28" width="30" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="20" y="63" width="30" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="55" y="63" width="30" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="90" y="63" width="30" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="125" y="63" width="30" height="30" fill="#f0f1f3" stroke="var(--border)"/>
  <path d="M20,105 L155,105" stroke="#c0392b" stroke-width="1.5" stroke-dasharray="4"/>
  <text x="87" y="120" text-anchor="middle" font-size="9" fill="#c0392b">간격을 더 줄이면 셀 간 간섭 ↑</text>
  <text x="87" y="185" text-anchor="middle" font-size="9" fill="var(--muted)">면적을 늘리지 않는 한 셀 수 한계</text>
  <line x1="195" y1="20" x2="195" y2="195" stroke="var(--border)"/>
  <text x="320" y="16" text-anchor="middle" font-size="11" fill="var(--ink)" font-weight="700">3D NAND (수직 적층)</text>
  <rect x="260" y="30" width="120" height="12" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="260" y="46" width="120" height="12" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="260" y="62" width="120" height="12" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="260" y="78" width="120" height="12" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="260" y="94" width="120" height="12" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="260" y="110" width="120" height="12" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <line x1="285" y1="30" x2="285" y2="122" stroke="var(--accent)" stroke-width="3"/>
  <line x1="320" y1="30" x2="320" y2="122" stroke="var(--accent)" stroke-width="3"/>
  <line x1="355" y1="30" x2="355" y2="122" stroke="var(--accent)" stroke-width="3"/>
  <text x="320" y="140" text-anchor="middle" font-size="9" fill="var(--muted)">세로 채널홀 하나가 여러 층을 통과</text>
  <text x="320" y="185" text-anchor="middle" font-size="9" fill="var(--muted)">층수(232단, 321단 등)를 늘려 셀 수 확보</text>
</svg>
<p class="diagram-caption">그림 5-1. 2D 평면 배열 vs 3D 수직 적층</p>

## 채널홀: 옆이 아니라 위아래로 쌓는다
**3D NAND(V-NAND)** 는 셀을 평면에 나란히 놓는 대신, 여러 층(레이어)을 수직으로 쌓고 그 층들을 관통하는 세로 구멍(**채널홀, channel hole**)을 뚫어, 그 구멍 하나를 따라 여러 층의 셀이 마치 기둥처럼 연결된 **스트링(string)** 을 만듭니다. 채널홀 하나가 지나가는 각 층이 셀 하나씩에 해당하고, 그 층의 게이트가 1강에서 본 컨트롤 게이트 역할을 합니다.

## 왜 전하 트랩(CTF) 방식이 유리한가
1강에서 플로팅 게이트는 도체라서 전자가 층 전체로 퍼진다고 했습니다. 3D 구조처럼 채널홀을 따라 얇고 길게 층을 쌓는 공정에서는, 도체 층을 셀마다 정교하게 분리하기가 훨씬 까다롭습니다. 반면 전하 트랩(CTF)은 절연체이므로 층 전체를 하나로 죽 이어 만들어도 전자가 각자의 트랩 지점에 국소적으로 갇혀 셀끼리 간섭이 적습니다. 그래서 3D NAND는 거의 전량 CTF 방식을 씁니다.

## 단수 경쟁: 232단, 321단이 의미하는 것
뉴스에 나오는 "176단", "232단", "321단" 같은 숫자는 이 수직 스택의 층수(word line 레이어 수)입니다. 평면 면적을 넓히지 않고도 층수를 늘리면 같은 칩 크기에서 셀 수(=용량)를 늘릴 수 있어, 이 단수 경쟁이 곧 원가·집적도 경쟁의 핵심 지표로 다뤄집니다.

## NAND 기초를 마치며
1강 셀 구조 → 2강 셀당 비트 수 → 3강 P/E 사이클과 마모 → 4강 페이지/블록 구조 → 5강 3D 적층까지 왔습니다. 이제 다음 챕터(호스트 인터페이스)로 넘어가면, 이 물리적 제약을 가진 NAND에게 호스트가 어떻게 명령을 전달하는지를 봅니다."""),
    ],

    "interface": [
        (1, "SATA/AHCI의 한계", """1챕터에서 NAND 셀 자체의 물리적 한계를 봤습니다. 이제 호스트(PC/서버)가 이 복잡한 저장장치와 어떻게 대화하는지 — 인터페이스를 봅니다. 인터페이스는 SSD의 이론적 성능 상한선을 결정하고, 다음 챕터들에서 다룰 FTL·컨트롤러가 그 상한선 안에서 실제 성능을 뽑아내는 기준선이 됩니다.

## SATA: HDD 시절 설계된 버스
**SATA(Serial ATA)** 는 원래 HDD를 위해 설계된 직렬 버스로, 최신 규격도 이론상 6Gbps(약 600MB/s)가 한계입니다. HDD의 실제 병목은 회전하는 디스크와 움직이는 헤드였기 때문에, 이 정도 대역폭으로도 충분했습니다.

## AHCI: 큐가 하나뿐인 프로토콜
SATA 위에서 명령을 주고받는 프로토콜이 **AHCI(Advanced Host Controller Interface)** 입니다. AHCI는 명령 큐(Command Queue)가 오직 1개, 큐 깊이도 32개로 제한돼 있습니다. HDD는 헤드 하나가 명령을 순차로 처리할 수밖에 없어 이 제약이 문제되지 않았습니다.

## 왜 SSD에는 병목이 되는가
SSD는 4챕터(컨트롤러)에서 볼 여러 채널을 동시에 병렬로 접근할 수 있는 구조입니다. 그런데 AHCI의 큐가 1개뿐이면, 이 병렬 능력을 다 쓰기도 전에 큐 자체가 줄을 서서 기다리는 병목이 됩니다. 초창기 SATA SSD가 HDD보다는 훨씬 빠르지만 SSD의 진짜 잠재력을 다 못 냈던 이유가 바로 이겁니다.

다음 레슨에서는 이 병목을 물리적으로 해결한 PCIe 버스를 봅니다."""),

        (2, "PCIe: 고속 인터페이스의 물리 계층", """SATA/AHCI의 큐 병목을 해결하려면, 먼저 그 위를 지나는 물리적 통로 자체를 넓혀야 합니다. 그 역할을 하는 게 PCIe입니다.

## 점대점 직렬 버스
**PCIe(PCI Express)** 는 SSD와 호스트를 1:1로 잇는 고속 직렬 버스입니다. 여러 장치가 버스 하나를 공유하던 옛날 병렬 버스 방식과 달리, 장치마다 전용 통로(레인, lane)를 갖기 때문에 경쟁 없이 온전한 대역폭을 씁니다.

## 세대마다 두 배씩
PCIe는 세대(Gen)가 오를 때마다 레인 하나당 대역폭이 대략 두 배씩 늘어납니다.

<svg viewBox="0 0 420 180" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="18" font-size="11" fill="var(--ink)" font-weight="700">PCIe x4 대역폭 (세대별, 대략치)</text>
  <text x="10" y="46" font-size="10" fill="var(--muted)">Gen3</text>
  <rect x="55" y="36" width="45" height="16" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="106" y="48" font-size="9" fill="var(--ink)">약 4GB/s</text>
  <text x="10" y="76" font-size="10" fill="var(--muted)">Gen4</text>
  <rect x="55" y="66" width="90" height="16" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="151" y="78" font-size="9" fill="var(--ink)">약 8GB/s</text>
  <text x="10" y="106" font-size="10" fill="var(--muted)">Gen5</text>
  <rect x="55" y="96" width="180" height="16" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="241" y="108" font-size="9" fill="var(--ink)">약 16GB/s</text>
  <text x="10" y="136" font-size="10" fill="var(--muted)">Gen6</text>
  <rect x="55" y="126" width="340" height="16" fill="var(--accent)"/>
  <text x="330" y="138" font-size="9" fill="#fff">약 32GB/s (PAM4)</text>
  <text x="10" y="165" font-size="9" fill="var(--muted)">레인(x4) 기준. 레인 수(x1, x2, x4)를 늘리면 대역폭은 그만큼 더 늘어난다</text>
</svg>
<p class="diagram-caption">그림 2-1. PCIe 세대별 x4 대역폭 대략치</p>

Gen6부터는 **PAM4**라는 변조 방식을 도입해, 신호 한 번에 2비트를 실어 전송 효율을 더 높입니다. 뉴스에서 "PCIe 5.0 지원 SSD 출시"라는 문구는 곧 인터페이스 단의 이론 성능 상한이 올라갔다는 뜻으로 읽을 수 있습니다.

다음 레슨에서는 이 넓어진 통로 위에서, SSD 전용으로 새로 설계된 프로토콜인 NVMe가 어떻게 SATA/AHCI의 큐 병목을 실제로 없애는지를 봅니다."""),

        (3, "NVMe 큐 구조: 병렬성의 핵심", """PCIe가 물리적 통로를 넓혔다면, 그 위에서 명령을 주고받는 방식 자체를 SSD에 맞게 새로 설계한 것이 NVMe입니다.

## AHCI 큐 1개 vs NVMe 큐 수만 개
**NVMe(Non-Volatile Memory Express)** 의 핵심 차이는 큐 구조에 있습니다. 최대 6만 4천 개의 큐를 만들 수 있고, 큐마다 깊이도 최대 6만 4천까지 가능합니다. 특히 CPU 코어마다 별도의 제출 큐(Submission Queue)와 완료 큐(Completion Queue)를 둘 수 있어, 멀티코어 환경에서 락(lock) 경합 없이 병렬로 명령을 밀어넣을 수 있습니다.

<svg viewBox="0 0 420 170" xmlns="http://www.w3.org/2000/svg">
  <text x="90" y="18" text-anchor="middle" font-size="11" fill="var(--ink)" font-weight="700">AHCI</text>
  <rect x="20" y="30" width="140" height="34" fill="#f0f1f3" stroke="var(--border)" rx="4"/>
  <text x="90" y="51" text-anchor="middle" font-size="10" fill="var(--ink)">큐 1개 · 깊이 32</text>
  <text x="90" y="85" text-anchor="middle" font-size="9" fill="var(--muted)">코어 여러 개가</text>
  <text x="90" y="98" text-anchor="middle" font-size="9" fill="var(--muted)">큐 하나를 줄서서 공유</text>
  <text x="320" y="18" text-anchor="middle" font-size="11" fill="var(--ink)" font-weight="700">NVMe</text>
  <rect x="240" y="26" width="56" height="16" fill="var(--accent-soft)" stroke="var(--accent)" rx="3"/>
  <text x="268" y="38" text-anchor="middle" font-size="8" fill="#1c4a44">Core 0 큐</text>
  <rect x="304" y="26" width="56" height="16" fill="var(--accent-soft)" stroke="var(--accent)" rx="3"/>
  <text x="332" y="38" text-anchor="middle" font-size="8" fill="#1c4a44">Core 1 큐</text>
  <rect x="240" y="46" width="56" height="16" fill="var(--accent-soft)" stroke="var(--accent)" rx="3"/>
  <text x="268" y="58" text-anchor="middle" font-size="8" fill="#1c4a44">Core 2 큐</text>
  <rect x="304" y="46" width="56" height="16" fill="var(--accent-soft)" stroke="var(--accent)" rx="3"/>
  <text x="332" y="58" text-anchor="middle" font-size="8" fill="#1c4a44">Core 3 큐</text>
  <text x="300" y="90" text-anchor="middle" font-size="9" fill="var(--muted)">코어마다 전용 큐 쌍</text>
  <text x="300" y="103" text-anchor="middle" font-size="9" fill="var(--muted)">— 최대 6만 4천 개까지</text>
</svg>
<p class="diagram-caption">그림 3-1. AHCI 단일 큐 vs NVMe 코어별 다중 큐</p>

여기에 명령어 세트 자체도 단순화되어, 명령 하나당 처리 오버헤드가 줄었습니다. 이 큐 구조 덕분에 NVMe SSD는 낮은 큐 깊이에서도 지연시간이 짧고, 높은 큐 깊이(멀티스레드 부하)에서는 IOPS가 SATA 대비 수십 배까지 차이 납니다.

다음 레슨에서는 이 NVMe 명령이 호스트 입장에서는 왜 단순해 보이는지, 그리고 그 단순함 뒤에서 실제 복잡한 일을 누가 처리하는지를 정리합니다."""),

        (4, "인터페이스가 감추는 것과 드러내는 것", """1\~3강에서 SATA/AHCI의 한계, PCIe의 물리적 대역폭, NVMe의 큐 구조를 봤습니다. 이제 이 인터페이스가 호스트에게 무엇을 보여주고 무엇을 숨기는지 정리합니다.

## 호스트가 보는 것: 단순한 주소 하나
호스트 입장에서 NVMe 명령은 "논리 블록 주소(LBA) N번에 이 데이터를 써줘" 수준으로 단순합니다. 실제로 이 LBA가 어느 채널의 어느 다이, 어느 블록, 어느 페이지에 저장될지는 인터페이스 계층이 전혀 알려주지 않습니다.

## 감춰진 일: 다음 챕터의 몫
이 LBA를 실제 NAND의 물리적 위치로 바꾸는 작업은 다음 챕터에서 다룰 **FTL**이 담당합니다. 즉 인터페이스는 "얼마나 빨리, 얼마나 많은 명령을 동시에 보낼 수 있는가"의 문제이고, FTL은 "그 명령을 받아서 내부에서 실제로 어떻게 처리하는가"의 문제입니다. 이 둘은 서로 완전히 독립된 계층이라, NVMe 큐를 통해 초당 수십만 개의 쓰기 요청이 들어와도 그 요청을 어떻게 NAND 블록에 매핑할지는 전적으로 FTL의 역할입니다.

다음 챕터에서 이 매핑과, 매핑이 낳는 청소(가비지 컬렉션) 메커니즘을 다룹니다."""),
    ],

    "ftl": [
        (1, "FTL이 존재하는 이유와 L2P 매핑", """1챕터에서 확인했듯 NAND는 페이지 단위로만 쓰고 블록 단위로만 지울 수 있습니다. 하지만 호스트(OS 파일시스템)는 "같은 주소에 자유롭게 덮어쓸 수 있다"고 가정하고 명령을 보냅니다. 이 간극을 메우는 소프트웨어 계층이 **FTL(Flash Translation Layer)** 입니다.

## 왜 필요한가
FTL이 없다면 OS는 NAND의 물리적 제약을 전부 알아야 하므로, 저장장치를 바꿀 때마다 파일시스템을 새로 만들어야 할 것입니다. FTL이 이 복잡함을 전부 감춰서, 2챕터에서 본 것처럼 호스트는 그저 "LBA 몇 번에 써줘"라고만 하면 됩니다.

## L2P 매핑 테이블
FTL의 핵심 자료구조는 **L2P(Logical-to-Physical) 매핑 테이블**입니다. 호스트가 "LBA 100번에 써줘"라고 하면, FTL은 실제로는 비어 있는 다른 물리 페이지(예: 채널3-블록52-페이지7)에 쓰고, "LBA 100번은 이제 그 위치를 가리킨다"고 테이블을 갱신합니다. 예전에 LBA 100번이 가리키던 페이지는 "무효(invalid)"로 표시됩니다.

이 매핑 단위가 페이지 단위면 정밀하지만 테이블이 커지고(DRAM 필요량 증가), 블록 단위면 테이블은 작아지지만 유연성이 떨어져 실제로는 두 방식을 섞은 하이브리드 매핑을 많이 씁니다.

다음 레슨에서는 이렇게 "무효" 표시만 되고 쌓여가는 예전 페이지들을 FTL이 어떻게 정리하는지 봅니다."""),

        (2, "가비지 컬렉션과 쓰기 증폭", """1강에서 본 것처럼 쓰기가 계속되면 "무효" 표시된 페이지가 여기저기 흩어진 블록들이 쌓입니다. NAND는 블록 단위로만 지울 수 있으므로, 이 무효 페이지들을 정리하는 절차가 필요합니다.

## 가비지 컬렉션(GC)
FTL은 주기적으로 유효 페이지 비율이 낮은 블록을 골라 (1) 그 블록 안에 남은 유효 페이지들을 다른 블록으로 복사하고 (2) 원래 블록을 통째로 지워서 빈 블록으로 되돌리는 작업을 합니다. 이것이 **가비지 컬렉션(GC)** 입니다.

<svg viewBox="0 0 420 190" xmlns="http://www.w3.org/2000/svg">
  <text x="105" y="16" text-anchor="middle" font-size="11" fill="var(--ink)" font-weight="700">GC 전: 무효 페이지가 섞인 블록</text>
  <rect x="30" y="26" width="150" height="18" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="105" y="39" text-anchor="middle" font-size="8" fill="#1c4a44">유효</text>
  <rect x="30" y="46" width="150" height="18" fill="#f0f1f3" stroke="var(--border)"/>
  <text x="105" y="59" text-anchor="middle" font-size="8" fill="var(--muted)">무효</text>
  <rect x="30" y="66" width="150" height="18" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="105" y="79" text-anchor="middle" font-size="8" fill="#1c4a44">유효</text>
  <rect x="30" y="86" width="150" height="18" fill="#f0f1f3" stroke="var(--border)"/>
  <text x="105" y="99" text-anchor="middle" font-size="8" fill="var(--muted)">무효</text>
  <path d="M195,65 L235,65" stroke="var(--muted)" stroke-width="1.5"/>
  <path d="M235,65 l-6,-5 l0,10 z" fill="var(--muted)"/>
  <text x="215" y="55" text-anchor="middle" font-size="8" fill="var(--muted)">유효만</text>
  <text x="215" y="80" text-anchor="middle" font-size="8" fill="var(--muted)">복사</text>
  <text x="325" y="16" text-anchor="middle" font-size="11" fill="var(--ink)" font-weight="700">GC 후</text>
  <rect x="250" y="26" width="150" height="18" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="325" y="39" text-anchor="middle" font-size="8" fill="#1c4a44">유효 (새 블록)</text>
  <rect x="250" y="46" width="150" height="18" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="325" y="59" text-anchor="middle" font-size="8" fill="#1c4a44">유효 (새 블록)</text>
  <rect x="250" y="70" width="150" height="34" fill="#fff" stroke="#c0392b" stroke-dasharray="3"/>
  <text x="325" y="90" text-anchor="middle" font-size="9" fill="#c0392b">원래 블록: 통째로 Erase</text>
  <text x="10" y="140" font-size="9" fill="var(--muted)">문제: 호스트가 요청하지 않은 "복사를 위한 쓰기"가 추가로 발생한다</text>
</svg>
<p class="diagram-caption">그림 2-1. 가비지 컬렉션 전후 — 유효 페이지 복사 후 블록 통째로 Erase</p>

## 쓰기 증폭(WAF)
문제는 이 GC 과정에서 호스트가 요청하지 않은 "복사를 위한 쓰기"가 추가로 발생한다는 점입니다.

**WAF = (SSD가 실제로 NAND에 쓴 양) / (호스트가 요청한 쓰기 양)**

WAF가 3이라면, 호스트가 1GB를 쓰라고 했을 때 SSD 내부적으로는 3GB만큼 NAND에 썼다는 뜻이고, 이는 곧 P/E 사이클을 3배 빨리 소모한다는 의미입니다. SSD가 꽉 찰수록(빈 블록이 적을수록) GC가 복사해야 할 유효 페이지가 늘어나 WAF가 급격히 나빠지는데, 이를 완화하려는 것이 **오버프로비저닝(Over-Provisioning)** 입니다 — 사용자에게 보이는 용량보다 실제 NAND 용량을 더 크게 만들어 GC의 여유 공간을 확보합니다.

다음 레슨에서는 GC와 별개로, 특정 블록만 집중적으로 닳는 문제를 막는 웨어 레벨링을 봅니다."""),

        (3, "웨어 레벨링", """GC가 "무효 페이지를 정리"하는 절차라면, 웨어 레벨링은 "마모를 골고루 분산"시키는 절차입니다. 목적이 다른 만큼 별도로 봐야 합니다.

## 특정 블록만 먼저 죽는 문제
특정 블록만 반복해서 쓰고 지우면 그 블록만 먼저 수명을 다합니다. 예를 들어 운영체제의 로그 파일처럼 항상 같은 위치에 자주 쓰이는 데이터가 있다면, FTL이 아무 대책 없이 매핑한다면 그 데이터가 담긴 물리 블록만 P/E 사이클을 빨리 소모하게 됩니다.

## 웨어 레벨링의 두 갈래
**웨어 레벨링**은 모든 블록의 P/E 사이클 소모량이 비슷해지도록 쓰기를 분산시키는 기법입니다.

- **동적 웨어 레벨링**: 새로 쓰기가 들어올 때마다, 지금까지 가장 덜 닳은 빈 블록을 우선적으로 골라 씁니다.
- **정적 웨어 레벨링**: 자주 바뀌지 않는 "차가운(cold)" 데이터가 있는 블록과 자주 바뀌는 "뜨거운(hot)" 데이터가 있는 블록을 강제로 맞바꿔줍니다. 그대로 두면 cold 데이터가 담긴 블록은 영원히 마모가 안 되고, hot 데이터가 담긴 블록만 계속 닳기 때문입니다.

두 방식 모두 결국 2강의 WAF와 트레이드오프 관계에 있습니다 — 데이터를 옮기는 것 자체가 추가 쓰기이기 때문입니다. 그래서 FTL은 "지금 웨어 레벨링을 할 가치가 있는가"를 계속 판단해야 합니다.

다음 레슨에서는 호스트가 FTL의 이 부담을 덜어주는 방법인 TRIM/UNMAP을 봅니다."""),

        (4, "TRIM/UNMAP: 호스트가 FTL을 돕는 방법", """1\~3강에서 본 GC와 웨어 레벨링은 모두 FTL이 SSD 내부에서 혼자 판단해서 처리하는 일이었습니다. 이번 레슨은 호스트가 이 부담을 덜어주는 유일한 통로를 봅니다.

## FTL이 모르는 것: 삭제된 파일
파일을 삭제해도 SSD 입장에서는 그 LBA가 "이제 안 쓴다"는 사실을 알 방법이 없습니다 — 파일시스템 메타데이터만 지워질 뿐, SSD에는 아무 명령도 오지 않기 때문입니다. FTL은 여전히 그 페이지를 "유효"하다고 여기고, 2강의 GC 때 쓸데없이 복사해 버립니다.

## TRIM이 메우는 간극
**TRIM**(UNMAP) 명령은 OS가 "이 LBA들은 이제 유효하지 않다"고 SSD에 미리 알려주는 명령입니다. TRIM을 받으면 FTL은 L2P 매핑에서 해당 LBA를 즉시 무효 처리할 수 있어, GC 때 이 페이지들을 복사할 필요 없이 바로 버릴 수 있습니다. 결과적으로 WAF가 낮아지고, 웨어 레벨링이 옮겨야 할 데이터 양도 줄어듭니다.

## FTL 챕터를 마치며
1강 L2P 매핑 → 2강 GC와 WAF → 3강 웨어 레벨링 → 4강 TRIM까지, "호스트는 자유롭게 덮어쓴다고 믿지만 실제로는 새로 쓰고 나중에 치운다"는 이 챕터의 핵심 아이디어가 어떻게 구현되는지 봤습니다. 다음 챕터에서는 이 모든 판단을 실시간으로 수행하는 하드웨어, 즉 컨트롤러 아키텍처를 다룹니다."""),
    ],

    "controller": [
        (1, "컨트롤러 구조와 채널/웨이", """지금까지 다룬 인터페이스 처리, L2P 매핑, 가비지 컬렉션, 웨어 레벨링을 전부 실시간으로 수행하는 주체가 **SSD 컨트롤러**입니다. 컨트롤러는 사실상 저장장치 안에 들어 있는 전용 임베디드 컴퓨터이며, 보통 여러 개의 ARM 코어와 전용 하드웨어 가속 블록(ECC 엔진, 암호화 엔진 등)으로 구성됩니다.

## 채널과 웨이: 병렬성의 근원
컨트롤러와 NAND 다이(die) 사이는 **채널(Channel)** 이라는 독립된 버스로 연결됩니다. 채널 하나에는 여러 개의 NAND 칩(**웨이, Way** 또는 CE-Chip Enable로 구분)이 물려 있습니다.

<svg viewBox="0 0 420 170" xmlns="http://www.w3.org/2000/svg">
  <text x="210" y="16" text-anchor="middle" font-size="11" fill="var(--ink)" font-weight="700">8채널 × 4웨이 = 32개 다이 동시 접근</text>
  <rect x="20" y="30" width="30" height="120" fill="none" stroke="var(--border)" stroke-width="1.5"/>
  <text x="35" y="26" text-anchor="middle" font-size="8" fill="var(--muted)">CH0</text>
  <rect x="26" y="36" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="26" y="64" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="26" y="92" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="26" y="120" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="60" y="30" width="30" height="120" fill="none" stroke="var(--border)" stroke-width="1.5"/>
  <text x="75" y="26" text-anchor="middle" font-size="8" fill="var(--muted)">CH1</text>
  <rect x="66" y="36" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="66" y="64" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="66" y="92" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="66" y="120" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="120" y="95" font-size="14" fill="var(--muted)">···</text>
  <rect x="160" y="30" width="30" height="120" fill="none" stroke="var(--border)" stroke-width="1.5"/>
  <text x="175" y="26" text-anchor="middle" font-size="8" fill="var(--muted)">CH7</text>
  <rect x="166" y="36" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="166" y="64" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="166" y="92" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="166" y="120" width="18" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="230" y="60" width="160" height="40" fill="var(--accent)" rx="4"/>
  <text x="310" y="84" text-anchor="middle" font-size="11" fill="#fff" font-weight="700">SSD 컨트롤러</text>
</svg>
<p class="diagram-caption">그림 1-1. 채널·웨이 구조와 병렬 접근</p>

채널이 많을수록, 그리고 채널마다 웨이가 많을수록 동시에 여러 NAND 다이에 접근할 수 있어 병렬 처리량이 늘어납니다. "채널/웨이 인터리빙(interleaving)"이라는 표현이 나오면 이 병렬 접근을 최적화한다는 뜻입니다.

다음 레슨에서는 컨트롤러가 이 채널들로 오가는 매핑 테이블을 어디에 두는지 — DRAM 유무의 차이를 봅니다."""),

        (2, "DRAM 기반 vs DRAM-less", """1강에서 본 채널·웨이 구조로 NAND에 병렬 접근할 수 있어도, 3챕터에서 배운 L2P 매핑 테이블을 매번 NAND에서 읽어야 한다면 느립니다. 이를 어디에 캐싱하느냐로 컨트롤러 설계가 갈립니다.

## L2P 테이블을 DRAM에 캐싱
L2P 매핑 테이블은 보통 수백 MB\~수 GB 크기라, 이를 빠르게 조회하려면 별도의 DRAM에 캐싱해두는 것이 유리합니다. 이렇게 전용 DRAM을 탑재한 것이 **DRAM 기반 SSD**입니다.

## 원가를 낮춘 대안: DRAM-less
반면 원가를 낮추기 위해 DRAM을 아예 빼고, 대신 호스트 시스템 메모리 일부를 빌려쓰는 **HMB(Host Memory Buffer)** 라는 NVMe 기능을 활용하는 **DRAM-less SSD**도 있습니다. DRAM-less는 원가는 낮지만 매핑 테이블 조회를 위해 매번 NAND를 오가야 할 가능성이 있어(HMB가 이를 상당히 보완하지만) 워스트케이스 지연시간이 불리할 수 있습니다.

## 어디에 쓰이는가
고성능 서버·워크스테이션용 SSD는 대부분 DRAM 기반을 씁니다. 반면 보급형 소비자용 SSD나 원가가 민감한 임베디드 스토리지는 DRAM-less를 채택해 가격 경쟁력을 확보합니다.

다음 레슨에서는 컨트롤러가 명령 하나를 받아서 실제로 어떤 순서로 처리하는지 — 펌웨어 파이프라인을 봅니다."""),

        (3, "펌웨어 파이프라인", """1\~2강에서 컨트롤러의 하드웨어 구조(채널/웨이, DRAM 유무)를 봤습니다. 이 하드웨어 위에서 실제로 명령을 처리하는 소프트웨어 순서가 펌웨어 파이프라인입니다.

## 명령 하나의 여정
호스트에서 명령이 들어오면 컨트롤러 펌웨어는 대략 다음 순서로 처리합니다.

1. NVMe 큐에서 명령 수신
2. L2P 조회/갱신
3. (쓰기라면) DRAM 캐시에 버퍼링 후 NAND 채널로 분산 기록, (읽기라면) 물리주소 확인 후 해당 채널에서 읽기
4. ECC 디코딩으로 오류 정정
5. 호스트로 데이터 반환 및 완료 큐에 알림

## 왜 이게 제조사별 성능 차이를 만드는가
이 파이프라인이 얼마나 효율적으로 짜였는지가 같은 NAND, 같은 인터페이스를 쓰고도 제조사별 SSD 성능이 갈리는 이유입니다 — 즉 "NAND는 원자재, 컨트롤러 펌웨어는 요리 실력"에 가깝습니다. 예를 들어 GC를 언제 백그라운드로 돌릴지, 여러 채널에 쓰기를 어떻게 분산할지, ECC 디코딩을 얼마나 병렬화할지 같은 판단이 전부 이 펌웨어 안에 있습니다.

다음 레슨에서는 이 파이프라인이 실제로 체감 속도를 어떻게 바꾸는지, SLC 캐싱을 통해 봅니다."""),

        (4, "SLC 캐싱과 폴딩", """3강에서 본 펌웨어 파이프라인 중 "쓰기" 단계를 더 자세히 보면, TLC/QLC SSD 대부분이 쓰는 흥미로운 트릭이 있습니다.

## QLC 셀을 SLC처럼 쓰기
TLC/QLC SSD 상당수는 실제로는 QLC 셀 일부를 SLC 모드(셀당 1비트만 사용)로 임시 운용해 빠른 쓰기 버퍼로 씁니다. 1챕터에서 봤듯 SLC는 구간이 2개뿐이라 쓰기 속도가 훨씬 빠릅니다. 쓰기가 들어오면 먼저 이 **SLC 캐시**에 빠르게 기록합니다.

## 폴딩: 나중에 다시 압축
유휴 시간에 컨트롤러가 백그라운드로 QLC 영역에 다시 압축해서 옮깁니다. 이 과정을 **폴딩(folding)** 이라 부릅니다. 폴딩은 사실상 SLC 캐시에 있던 1비트짜리 데이터 4개를 QLC 셀 하나에 4비트로 다시 쓰는 작업입니다.

## 캐시가 꽉 차면 느려지는 이유
벤치마크에서 "초반엔 빠르다가 캐시가 꽉 차면 속도가 급격히 떨어진다"는 현상이 바로 이 SLC 캐시 소진 때문입니다. SLC 캐시가 다 차면 더 이상 빠른 버퍼를 쓸 수 없어, 들어오는 쓰기가 QLC 영역에 직접 기록되면서 원래 QLC의 느린 쓰기 속도가 그대로 드러납니다.

## 컨트롤러 챕터를 마치며
1강 채널/웨이 → 2강 DRAM 유무 → 3강 펌웨어 파이프라인 → 4강 SLC 캐싱까지, 컨트롤러가 NAND의 물리적 한계 안에서 어떻게 성능을 짜내는지 봤습니다. 다음 챕터에서는 컨트롤러가 아무리 정교해도 피할 수 없는 물리적 오류를 어떻게 감지하고 정정하는지 — 신뢰성을 다룹니다."""),
    ],

    "reliability": [
        (1, "오류의 원인: RBER", """1챕터에서 봤듯 셀당 비트 수가 늘어날수록(TLC→QLC→PLC) 문턱전압 구간 사이 여백이 좁아집니다. 이 여백이 실제로 어떻게 오류로 이어지는지 봅니다.

## 전자가 새는 두 가지 경로
3챕터(FTL)에서 다룬 것처럼 P/E 사이클이 누적되면서 절연막이 손상되면 전자가 조금씩 새거나(전하 손실), 인접 셀의 프로그램 동작이 옆 셀에 간섭을 주기도 합니다(셀 간 간섭). 두 경우 모두 원래 저장했던 값과 다르게 읽히는 비트가 생깁니다.

## RBER: 오류율을 수치화하기
이렇게 생기는 오류의 비율을 **RBER(Raw Bit Error Rate, 원시 비트 오류율)** 이라 부릅니다. RBER은 P/E 사이클이 쌓일수록, 그리고 셀당 비트 수가 많을수록 증가합니다. 컨트롤러는 이 RBER을 실시간으로 추정해서, 뒤에서 볼 ECC의 정정 강도를 조절하거나 블록 수명을 관리하는 데 씁니다.

다음 레슨에서는 이 오류를 실제로 어떻게 감지하고 고치는지 — ECC와 LDPC를 봅니다."""),

        (2, "ECC와 LDPC", """1강에서 본 RBER은 결코 0이 될 수 없습니다. 그래서 컨트롤러는 오류가 나더라도 원래 데이터를 복원할 방법을 갖춰야 합니다.

## 오류정정부호(ECC)
컨트롤러는 실제 데이터를 쓸 때 오류정정부호(**ECC**)를 함께 기록해둡니다. 예전에는 BCH 코드를 많이 썼지만, TLC 이상에서는 오류율이 BCH의 정정 능력을 넘어서는 경우가 많습니다.

## LDPC: 확률로 판단하는 정정
현재 주류는 **LDPC(Low-Density Parity-Check)** 코드입니다. LDPC는 "하드 디코딩"(비트를 0/1로만 판단)뿐 아니라 "소프트 디코딩"(문턱전압을 여러 단계로 세밀하게 읽어 확률적으로 판단)까지 지원합니다.

<svg viewBox="0 0 420 160" xmlns="http://www.w3.org/2000/svg">
  <text x="105" y="16" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">하드 디코딩: 0 또는 1로만 판정</text>
  <rect x="20" y="26" width="170" height="24" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <line x1="105" y1="26" x2="105" y2="50" stroke="var(--accent)" stroke-width="2"/>
  <text x="60" y="42" text-anchor="middle" font-size="9" fill="#1c4a44">0</text>
  <text x="150" y="42" text-anchor="middle" font-size="9" fill="#1c4a44">1</text>
  <text x="105" y="65" text-anchor="middle" font-size="8" fill="var(--muted)">경계 근처 값도 강제로 양쪽 중 하나로 판정 → 정보 손실</text>
  <text x="315" y="16" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">소프트 디코딩: 확률로 판단</text>
  <rect x="230" y="26" width="170" height="24" fill="#fff" stroke="var(--accent)"/>
  <line x1="265" y1="26" x2="265" y2="50" stroke="var(--accent)" stroke-width="0.7"/>
  <line x1="300" y1="26" x2="300" y2="50" stroke="var(--accent)" stroke-width="0.7"/>
  <line x1="335" y1="26" x2="335" y2="50" stroke="var(--accent)" stroke-width="0.7"/>
  <line x1="365" y1="26" x2="365" y2="50" stroke="var(--accent)" stroke-width="0.7"/>
  <text x="315" y="65" text-anchor="middle" font-size="8" fill="var(--muted)">문턱전압을 여러 단계로 세밀히 읽어 확률로 보정</text>
</svg>
<p class="diagram-caption">그림 2-1. 하드 디코딩 vs 소프트 디코딩</p>

이 소프트 디코딩 덕분에 LDPC는 BCH보다 훨씬 높은 오류율까지 정정할 수 있습니다 — QLC/PLC가 실제 제품으로 나올 수 있는 것은 LDPC 없이는 불가능합니다.

다음 레슨에서는 ECC로도 막기 어려운, 읽기 자체가 유발하는 오류인 리드 디스터브를 봅니다."""),

        (3, "리드 디스터브와 리텐션, PLP", """2강의 ECC는 오류가 생긴 뒤 고치는 방법이었습니다. 이번 레슨은 오류가 애초에 왜, 언제 더 잘 생기는지 — 읽기와 시간 경과, 그리고 전원 문제를 봅니다.

## 리드 디스터브: 읽기만 해도 옆이 흔들린다
같은 블록의 특정 페이지를 반복해서 읽기만 해도, 그 옆 페이지들이 미세한 전압 스트레스를 받아 값이 틀어질 수 있습니다. 이를 **리드 디스터브**라 하며, 컨트롤러는 특정 블록의 누적 읽기 횟수가 임계치를 넘으면 그 블록 데이터를 통째로 다른 블록에 재기록(리프레시)해서 예방합니다.

## 리텐션: 시간이 지나면 전자가 샌다
전원이 꺼진 채로 오래 방치되면 갇혀 있던 전자가 서서히 빠져나가 데이터가 흐려집니다(**리텐션** 열화). P/E 사이클을 많이 소모한 셀일수록 절연막이 약해져 리텐션이 더 빨리 나빠집니다.

## PLP: 쓰다가 전원이 나가면
쓰기 도중 전원이 꺼지는 경우를 대비해 엔터프라이즈 SSD는 **PLP(Power Loss Protection)** 용 커패시터를 탑재해, 정전 순간에도 4챕터에서 본 DRAM 캐시에 있던 쓰기 데이터를 NAND에 마저 내려쓸 수 있는 시간을 확보합니다.

다음 레슨에서는 셀 하나가 아니라 다이 하나가 통째로 죽는 경우와, 이 모든 걸 종합한 수명 지표를 봅니다."""),

        (4, "RAIN과 수명 지표", """1\~3강에서 셀 하나 단위의 오류(RBER, 리드 디스터브, 리텐션)를 봤습니다. 이번 레슨은 더 큰 단위의 고장과, 이 모든 신뢰성 요소를 종합한 제품 스펙을 봅니다.

## RAIN: 다이 하나가 통째로 죽는 경우
RAID가 여러 디스크를 묶어 디스크 하나의 고장에 대비하듯, **RAIN(Redundant Array of Independent NAND)** 은 SSD 내부에서 NAND 다이 여러 개에 패리티를 분산 저장해, 다이 하나가 완전히 죽어도 데이터를 복구할 수 있게 합니다.

## TBW와 DWPD: 모든 걸 종합한 보증 스펙
제조사가 표기하는 **TBW(Total Bytes Written)** 와 **DWPD(Drive Writes Per Day)** 는 앞서 배운 P/E 사이클 한계, WAF, 오버프로비저닝을 전부 반영해 제조사가 보증하는 수명 스펙입니다. 뉴스에서 "이 서버용 SSD는 3 DWPD를 지원한다"는 표현은 곧 쓰기가 매우 잦은 워크로드(데이터베이스 로그 등)에도 견디도록 설계됐다는 뜻입니다.

## 신뢰성 챕터를 마치며
1강 RBER → 2강 ECC/LDPC → 3강 리드 디스터브/리텐션/PLP → 4강 RAIN과 수명 지표까지, "기존 SSD를 어떻게 안정적으로 오래 쓰게 만드는가"를 다뤘습니다. 마지막 챕터에서는 이 한계들을 아예 다른 접근으로 우회하거나 완화하려는 차세대 기술을 다룹니다."""),
    ],

    "emerging": [
        (1, "ZNS: 호스트가 GC를 도와준다", """1\~5챕터에서 다룬 SSD는 결국 "블록 디바이스"라는 좁은 창구(LBA 읽기/쓰기)로만 호스트와 대화합니다. 이 챕터의 기술들은 대체로 "FTL이 혼자 짊어지던 일 일부를 호스트와 나눠서 하거나", "인터페이스의 쓰임새를 저장 이외로 확장"하는 방향입니다. 먼저 3챕터의 GC와 WAF 문제를 호스트와 나눠 푸는 ZNS를 봅니다.

## 존 단위로 쓰기를 제한한다
**ZNS(Zoned Namespace)** SSD는 저장 공간을 여러 개의 "존(Zone)"으로 나누고, 각 존은 반드시 순차적으로만 써야 하며(랜덤 덮어쓰기 불가), 지울 때도 존 단위로 통째로 리셋합니다.

<svg viewBox="0 0 420 170" xmlns="http://www.w3.org/2000/svg">
  <text x="100" y="16" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">일반 SSD: 무작위 쓰기</text>
  <rect x="20" y="26" width="160" height="90" fill="#f0f1f3" stroke="var(--border)"/>
  <rect x="30" y="34" width="30" height="14" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="70" y="60" width="30" height="14" fill="#fbeaea" stroke="#c0392b"/>
  <rect x="120" y="40" width="30" height="14" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <rect x="40" y="90" width="30" height="14" fill="#fbeaea" stroke="#c0392b"/>
  <rect x="130" y="80" width="30" height="14" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="100" y="130" text-anchor="middle" font-size="8" fill="var(--muted)">유효·무효 페이지가 뒤섞여 GC 부담 큼</text>
  <text x="320" y="16" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">ZNS: 존 단위 순차 쓰기</text>
  <rect x="240" y="26" width="160" height="26" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="320" y="43" text-anchor="middle" font-size="8" fill="#1c4a44">Zone 0 — 순차 기록 중</text>
  <rect x="240" y="56" width="160" height="26" fill="#fff" stroke="var(--border)" stroke-dasharray="3"/>
  <text x="320" y="73" text-anchor="middle" font-size="8" fill="var(--muted)">Zone 1 — 비어 있음</text>
  <rect x="240" y="86" width="160" height="26" fill="#fff" stroke="var(--border)" stroke-dasharray="3"/>
  <text x="320" y="103" text-anchor="middle" font-size="8" fill="var(--muted)">Zone 2 — 비어 있음</text>
  <text x="320" y="130" text-anchor="middle" font-size="8" fill="var(--muted)">한 존을 다 쓰면 다음 존으로, 지울 땐 존째로 리셋</text>
</svg>
<p class="diagram-caption">그림 1-1. 일반 SSD의 무작위 쓰기 vs ZNS의 존 단위 순차 쓰기</p>

## 왜 GC 부담이 줄어드는가
이 구조를 NAND 블록 경계와 맞추면, 호스트(주로 데이터베이스나 파일시스템)가 애초에 "관련된 데이터를 같은 존에 순차로 쓰는" 방식으로 동작할 경우 SSD 내부에서 무효 페이지가 여기저기 흩어지는 일 자체가 줄어들어 GC 부담과 WAF가 크게 낮아집니다. 대신 이 이점을 얻으려면 호스트 소프트웨어가 ZNS를 인식하도록 다시 작성돼야 합니다.

다음 레슨에서는 인터페이스의 쓰임새 자체를 저장 이외로 넓히는 CXL을 봅니다."""),

        (2, "CXL: 메모리 계층의 확장", """1강의 ZNS가 "GC 책임을 호스트와 나누는" 방향이었다면, CXL은 2챕터에서 다룬 PCIe/NVMe 인터페이스의 쓰임새 자체를 저장 이외로 넓히는 방향입니다.

## PCIe 위의 새 프로토콜
**CXL(Compute Express Link)** 은 같은 PCIe 물리 계층 위에서 동작하되 메모리 일관성(cache coherency)을 지원하는 새 프로토콜입니다. 2챕터에서 PCIe가 순수하게 저장장치와 데이터를 주고받는 통로였다면, CXL은 그 통로 위에 "메모리처럼 취급 가능하다"는 새로운 약속을 추가합니다.

## 메모리 풀링과 확장
이를 통해 SSD나 별도의 메모리 확장 장치를 마치 호스트의 메인 메모리(DRAM)처럼 취급할 수 있는 "메모리 풀링/확장"이 가능해집니다. 서버가 DRAM 슬롯 물리적 한계를 넘어 메모리를 늘리거나, 여러 서버가 메모리 풀을 공유하는 시나리오에 쓰입니다.

## SSD 회사가 CXL에 뛰어드는 이유
NAND보다 훨씬 빠르지만 DRAM보다는 값싼 "중간 계층 메모리"로 포지셔닝할 수 있기 때문입니다. 4챕터에서 본 컨트롤러의 DRAM 캐싱 개념을 서버 전체 규모로 확장한 것에 가깝다고 볼 수 있습니다.

다음 레슨에서는 데이터를 아예 옮기지 않고 저장장치 근처에서 계산까지 끝내는 PIM/연산 스토리지를 봅니다."""),

        (3, "PIM과 연산 스토리지", """1\~2강에서 GC 책임 분담(ZNS), 메모리 계층 확장(CXL)을 봤습니다. 이번 레슨은 아예 "계산을 어디서 할 것인가"를 재설계하는 접근입니다.

## 데이터를 옮기지 말고 그 자리에서 계산
전통적인 구조는 "저장장치 → 버스 → CPU"로 데이터를 옮긴 뒤 CPU가 계산합니다. **PIM(Processing-In-Memory)** 이나 **연산 스토리지(Computational Storage)** 는 메모리·스토리지 칩 안 또는 바로 옆에 연산 유닛을 두어, 대용량 데이터를 굳이 CPU까지 옮기지 않고 그 자리에서 필터링·집계 같은 단순 연산을 끝내는 접근입니다.

## AI 데이터센터에서의 쓰임
AI 추론에서 SSD에 저장된 KV 캐시를 스토리지 근처에서 처리하려는 시도들이 이 계열에 속합니다. 데이터 이동 자체가 병목이자 전력 소모의 큰 부분을 차지하는 대규모 AI 워크로드에서, "이동을 줄인다"는 이 접근의 가치가 특히 부각됩니다.

다음 레슨에서는 ZNS, CXL, PIM 세 기술을 관통하는 공통점을 정리하고 SSD 트랙을 마무리합니다."""),

        (4, "세 기술의 공통점과 트랙 마무리", """1\~3강에서 ZNS, CXL, PIM을 각각 봤습니다. 서로 다른 기술이지만 관통하는 하나의 질문이 있습니다.

## 경계를 다시 협상하는 기술들
ZNS·CXL·PIM 모두 "호스트와 스토리지 사이의 경계를 어디에 그을 것인가"를 다시 협상하는 기술입니다. ZNS는 3챕터에서 본 GC 책임의 일부를 호스트로, CXL은 2챕터에서 본 인터페이스를 메모리 계층 구조 자체로 확장, PIM은 연산의 위치를 이동시킵니다. AI 데이터센터에서 스토리지 수요·아키텍처 기사가 나올 때 이 세 키워드가 자주 겹쳐 등장하는 이유이기도 합니다.

## SSD 트랙을 마치며
1챕터 NAND 셀의 물리적 제약에서 시작해, 그 제약을 인터페이스(2)로 감추고, FTL(3)로 관리하고, 컨트롤러(4)로 실행하고, 신뢰성 기법(5)으로 보완하고, 마지막으로 그 경계 자체를 재설계하는 차세대 기술(6)까지 왔습니다. 이제 실제 뉴스 기사를 볼 때 "이건 어느 계층 이야기인가"를 구분할 수 있는 기본기가 갖춰졌습니다."""),
    ],

    "vehicle-arch": [
        (1, "ECU와 MCU, 그리고 Domain 아키텍처", """자동차 SW 뉴스에 나오는 ECU, Zonal, HPC 같은 단어는 전부 "차 안에 컴퓨터가 몇 개 있고, 어떻게 배치돼 있는가"라는 하나의 질문에서 갈라져 나온 것들입니다.

## ECU와 MCU
**ECU(Electronic Control Unit)** 는 차량의 특정 기능(엔진 제어, 브레이크, 창문, 에어컨 등)을 담당하는 임베디드 제어기입니다. 그 안에서 연산을 담당하는 반도체 칩이 **MCU(Microcontroller Unit)** 입니다. 현대차 한 대에는 많게는 수십\~150개 안팎의 ECU가 들어갑니다.

## Domain 아키텍처: 기능별로 묶기
초창기 확장 방식은 **Domain(도메인) 아키텍처**였습니다. 파워트레인 도메인, 섀시 도메인, 바디 도메인처럼 기능 영역별로 ECU를 묶고, 도메인마다 대표 컨트롤러를 두는 방식입니다.

## 왜 한계에 부딪히는가
문제는 차량에 기능이 계속 추가되면서 ECU 개수와 배선(와이어링 하네스)이 같이 늘어난다는 점입니다 — 배선 무게가 수십 kg에 달하고, ECU마다 별도 SW를 개발·검증해야 해서 개발 비용도 함께 늘어납니다.

다음 레슨에서는 이 한계를 물리적 위치 기준으로 재배치해서 푸는 Zonal 아키텍처를 봅니다."""),

        (2, "Zonal 아키텍처", """1강에서 본 Domain 아키텍처의 배선·개발비 문제를 해결하는 접근이 Zonal 아키텍처입니다.

## 기능이 아니라 위치로 묶기
**Zonal(존) 아키텍처**는 기능이 아니라 차량의 물리적 위치(전방/후방/좌/우 등 구역)를 기준으로 컨트롤러를 묶습니다. 각 구역의 존 컨트롤러가 근처 센서·액추에이터 신호를 모아, 중앙의 고성능 컴퓨팅 유닛인 **HPC(High Performance Computer)** 로 전달합니다.

<svg viewBox="0 0 420 190" xmlns="http://www.w3.org/2000/svg">
  <text x="105" y="16" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">Domain: 기능별 배선</text>
  <circle cx="105" cy="90" r="14" fill="var(--accent)"/>
  <text x="105" y="94" text-anchor="middle" font-size="7" fill="#fff">중앙</text>
  <circle cx="45" cy="40" r="10" fill="#f0f1f3" stroke="var(--border)"/>
  <circle cx="165" cy="40" r="10" fill="#f0f1f3" stroke="var(--border)"/>
  <circle cx="45" cy="140" r="10" fill="#f0f1f3" stroke="var(--border)"/>
  <circle cx="165" cy="140" r="10" fill="#f0f1f3" stroke="var(--border)"/>
  <circle cx="30" cy="90" r="10" fill="#f0f1f3" stroke="var(--border)"/>
  <circle cx="180" cy="90" r="10" fill="#f0f1f3" stroke="var(--border)"/>
  <line x1="105" y1="90" x2="45" y2="40" stroke="var(--muted)"/>
  <line x1="105" y1="90" x2="165" y2="40" stroke="var(--muted)"/>
  <line x1="105" y1="90" x2="45" y2="140" stroke="var(--muted)"/>
  <line x1="105" y1="90" x2="165" y2="140" stroke="var(--muted)"/>
  <line x1="105" y1="90" x2="30" y2="90" stroke="var(--muted)"/>
  <line x1="105" y1="90" x2="180" y2="90" stroke="var(--muted)"/>
  <text x="105" y="175" text-anchor="middle" font-size="8" fill="var(--muted)">ECU마다 긴 배선이 각각 연결</text>
  <text x="320" y="16" text-anchor="middle" font-size="10" fill="var(--ink)" font-weight="700">Zonal: 구역별로 짧게 모음</text>
  <circle cx="320" cy="90" r="16" fill="var(--accent)"/>
  <text x="320" y="94" text-anchor="middle" font-size="7" fill="#fff">HPC</text>
  <rect x="256" y="34" width="26" height="18" fill="var(--accent-soft)" stroke="var(--accent)" rx="3"/>
  <rect x="360" y="34" width="26" height="18" fill="var(--accent-soft)" stroke="var(--accent)" rx="3"/>
  <rect x="256" y="130" width="26" height="18" fill="var(--accent-soft)" stroke="var(--accent)" rx="3"/>
  <rect x="360" y="130" width="26" height="18" fill="var(--accent-soft)" stroke="var(--accent)" rx="3"/>
  <line x1="320" y1="90" x2="269" y2="43" stroke="var(--accent)" stroke-width="1.5"/>
  <line x1="320" y1="90" x2="373" y2="43" stroke="var(--accent)" stroke-width="1.5"/>
  <line x1="320" y1="90" x2="269" y2="139" stroke="var(--accent)" stroke-width="1.5"/>
  <line x1="320" y1="90" x2="373" y2="139" stroke="var(--accent)" stroke-width="1.5"/>
  <text x="320" y="175" text-anchor="middle" font-size="8" fill="var(--muted)">존 컨트롤러가 근처 신호를 모아 HPC로</text>
</svg>
<p class="diagram-caption">그림 2-1. Domain(기능별) vs Zonal(구역별) 배선 비교</p>

## 배선 절감과 SW 통합
배선이 구역 안에서만 짧게 연결되면 되므로 배선 절감 효과가 크고, 무거운 연산은 HPC 한 곳에 집중되므로 SW를 통합·업데이트하기도 쉬워집니다. 뉴스에서 "중앙집중형 아키텍처로 전환"이라는 표현이 나오면 대체로 Domain에서 Zonal로 옮겨가는 흐름을 가리킵니다.

다음 레슨에서는 이 하드웨어 재배치가 왜 SDV(소프트웨어 정의 차량) 전환의 전제조건이 되는지를 봅니다."""),

        (3, "Zonal이 SDV로 이어지는 이유", """1\~2강에서 Domain에서 Zonal로 옮겨가는 배경을 봤습니다. 이 변화가 왜 소프트웨어 트렌드(SDV)와 직결되는지 정리합니다.

## 흩어진 ECU, 흩어진 업데이트
ECU가 수십 개로 흩어져 있으면 SW 업데이트도 ECU 개수만큼 따로 관리해야 합니다. 제조사마다, 부품사마다 SW가 제각각이라 통합 업데이트 자체가 어렵습니다.

## 연산이 집중되면 SW로 기능을 바꿀 수 있다
반대로 연산이 HPC 몇 개로 집중되면, 새 기능을 추가하거나 성능을 개선하는 일이 하드웨어 교체가 아니라 소프트웨어 업데이트만으로 가능해집니다 — 이것이 최근 자동차 업계가 말하는 **SDV(소프트웨어 정의 차량)** 전환의 하드웨어적 전제조건입니다.

## 챕터를 마치며
1강 ECU/MCU와 Domain → 2강 Zonal 아키텍처 → 3강 SDV로 이어지는 이유까지, 차량 하드웨어가 왜 이렇게 재편되고 있는지를 봤습니다. 다음 챕터에서는 존 컨트롤러와 HPC가 실제로 무엇으로 연결되는지 — 차량 통신 기술을 다룹니다."""),
    ],

    "vehicle-comm": [
        (1, "CAN과 CAN-FD", """1챕터에서 본 Zonal 아키텍처가 실제로 동작하려면, 존 컨트롤러와 HPC 사이에서 초당 수천 개의 신호가 오가야 합니다. 가장 오래되고 기본이 되는 통신부터 봅니다.

## 자동차 통신의 기본기
**CAN(Controller Area Network)** 은 수십 년간 자동차 통신의 표준이었습니다. 여러 ECU가 하나의 버스를 공유하며 메시지를 브로드캐스트하는 방식으로, 느리지만(최대 1Mbps 수준) 노이즈에 강하고 저렴해서 지금도 널리 쓰입니다.

## CAN-FD: 대역폭을 넓힌 버전
대역폭을 개선한 **CAN-FD(CAN with Flexible Data-rate)** 는 데이터 구간의 전송 속도를 높여 더 큰 메시지를 빠르게 보낼 수 있게 한 버전입니다. 기본 CAN과 물리적으로 호환되면서도 처리량을 끌어올려, 완전히 새 배선 없이 점진적으로 도입할 수 있다는 장점이 있습니다.

다음 레슨에서는 CAN으로도 부족한 대용량 데이터(카메라·라이다 영상 등)를 위한 Automotive Ethernet과 SOME/IP를 봅니다."""),

        (2, "Automotive Ethernet과 SOME/IP", """1강의 CAN/CAN-FD로도 감당이 안 되는 대역폭 요구가 최근 늘고 있습니다. 이를 해결하는 두 기술을 함께 봅니다.

## 대역폭이 필요해진 이유
카메라·라이다 영상, OTA 업데이트 파일처럼 대용량 데이터가 오가기 시작하면서 CAN의 대역폭으로는 부족해졌습니다. **Automotive Ethernet**은 일반 이더넷을 차량 환경(진동, 전자파 간섭, 단선 케이블)에 맞게 개조한 표준으로, CAN보다 훨씬 넓은 대역폭을 제공합니다.

<svg viewBox="0 0 420 150" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="18" font-size="10" fill="var(--ink)" font-weight="700">차량 통신 대역폭 (대략 비교)</text>
  <text x="10" y="46" font-size="9" fill="var(--muted)">CAN</text>
  <rect x="60" y="36" width="8" height="16" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="75" y="48" font-size="8" fill="var(--ink)">~1Mbps</text>
  <text x="10" y="76" font-size="9" fill="var(--muted)">CAN-FD</text>
  <rect x="60" y="66" width="24" height="16" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="90" y="78" font-size="8" fill="var(--ink)">~5-8Mbps</text>
  <text x="10" y="106" font-size="9" fill="var(--muted)">Auto Ethernet</text>
  <rect x="60" y="96" width="330" height="16" fill="var(--accent)"/>
  <text x="200" y="108" text-anchor="middle" font-size="8" fill="#fff">최대 수 Gbps급 (100BASE-T1 ~ 멀티기가비트)</text>
  <text x="10" y="135" font-size="8" fill="var(--muted)">카메라·라이다 영상, OTA 이미지처럼 큰 데이터일수록 이더넷이 유리</text>
</svg>
<p class="diagram-caption">그림 2-1. CAN·CAN-FD·Automotive Ethernet 대역폭 비교(대략치)</p>

## SOME/IP: 이더넷 위에서 서비스처럼 통신하기
이더넷으로 대역폭 문제는 풀렸지만, "어떤 형식으로 메시지를 주고받을 것인가"는 별개의 문제입니다. **SOME/IP(Scalable service-Oriented MiddlewarE over IP)** 는 Automotive Ethernet 위에서 기능을 "서비스"로 취급해, 필요한 ECU가 필요한 서비스를 찾아 구독하는 방식의 통신을 제공합니다. 3챕터에서 다룰 Adaptive AUTOSAR가 이 SOME/IP를 표준 통신 수단으로 채택하고 있습니다.

다음 레슨에서는 이더넷의 약점인 "도착 시간 미보장" 문제를 푸는 TSN을 봅니다."""),

        (3, "TSN: 실시간성 보장하기", """2강에서 본 이더넷은 원래 "최선을 다해 전달"할 뿐 도착 시간을 보장하지 않습니다. 하지만 제동·조향처럼 지연이 곧 안전 문제가 되는 신호는 정해진 시간 안에 반드시 도착해야 합니다.

## 우선순위와 시간 동기화
**TSN(Time-Sensitive Networking)** 은 이더넷 위에 우선순위와 시간 동기화 규칙을 더해, 중요한 메시지가 정해진 시간 안에 도착하도록 보장하는 표준 기술군입니다. 일반 데이터(영상 스트리밍 등)와 안전 필수 데이터(제동 신호 등)가 같은 이더넷 배선을 공유하더라도, TSN이 안전 필수 데이터에 우선순위를 줘서 지연시간을 보장합니다.

## 왜 필요한가
1챕터에서 본 Zonal/HPC 구조에서는 다양한 종류의 데이터가 같은 통신 인프라를 공유하게 됩니다. TSN이 없다면 영상 데이터 폭주가 제동 신호 지연으로 이어질 수 있어, 안전 필수 통신에는 TSN 같은 실시간성 보장 기술이 필수적입니다.

다음 레슨에서는 정비소에서 차량을 진단하는 것도 결국 통신이라는 관점에서 DoIP/UDS를 봅니다."""),

        (4, "DoIP/UDS와 다음 챕터", """1\~3강에서 CAN, Ethernet, TSN까지 차량 안 통신을 봤습니다. 마지막으로 차량과 외부(정비소) 사이의 통신을 봅니다.

## 진단도 결국 통신이다
정비소에서 차량 진단기를 연결하는 것도 통신입니다. 기존에는 CAN 기반 진단 프로토콜인 **UDS(Unified Diagnostic Services)** 를 썼는데, **DoIP(Diagnostics over Internet Protocol, ISO 13400)** 는 이 UDS를 2강에서 본 이더넷 위로 옮긴 표준입니다.

## 대역폭이 넓어지며 생기는 새 쓰임
대역폭이 넓어진 만큼 DoIP는 대용량 로그 수집이나 OTA 업데이트 진단에도 활용됩니다. 예전 CAN 기반 진단으로는 차량 하나의 전체 로그를 뽑는 데 오래 걸렸지만, 이더넷 기반 DoIP라면 훨씬 빠르게 처리할 수 있습니다.

## 챕터를 마치며
1강 CAN/CAN-FD → 2강 Ethernet/SOME-IP → 3강 TSN → 4강 DoIP/UDS까지, 통신 인프라가 갖춰졌다면 그 위에서 실제로 동작하는 소프트웨어를 어떤 규칙으로 만들지가 다음 문제입니다. 다음 챕터에서는 이 규칙을 표준화한 AUTOSAR와, 그 위에서 자라난 SDV 소프트웨어 플랫폼을 다룹니다."""),
    ],

    "autosar": [
        (1, "AUTOSAR Classic: BSW·MCAL·CDD", """완성차 업체마다, 부품사마다 ECU 소프트웨어를 각자 다른 방식으로 만들면 재사용도 안 되고 검증 비용도 중복됩니다. **AUTOSAR(AUTomotive Open System ARchitecture)** 는 여러 완성차·부품사가 공동으로 만든 차량 SW 표준 플랫폼입니다.

## 전통적인 ECU를 위한 표준
**AUTOSAR Classic**은 기존 방식의 개별 ECU를 겨냥한 표준입니다. 계층 구조가 명확한데, 가장 아래에 하드웨어 레지스터 접근을 추상화하는 **MCAL(Microcontroller Abstraction Layer)** 이 있고, 그 위에 표준 기능 모듈들의 묶음인 **BSW(Basic Software)** 가 있습니다.

<svg viewBox="0 0 420 170" xmlns="http://www.w3.org/2000/svg">
  <rect x="110" y="16" width="200" height="30" fill="var(--accent)" rx="3"/>
  <text x="210" y="35" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">Application (앱 SW 컴포넌트)</text>
  <rect x="110" y="50" width="200" height="26" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="210" y="67" text-anchor="middle" font-size="9" fill="#1c4a44">RTE (Runtime Environment)</text>
  <rect x="110" y="80" width="200" height="26" fill="#f0f1f3" stroke="var(--border)"/>
  <text x="210" y="97" text-anchor="middle" font-size="9" fill="var(--ink)">BSW (표준 기능 모듈)</text>
  <rect x="110" y="110" width="90" height="24" fill="#fff" stroke="#c0392b" stroke-dasharray="3"/>
  <text x="155" y="126" text-anchor="middle" font-size="8" fill="#c0392b">CDD (특수 HW용)</text>
  <rect x="220" y="110" width="90" height="24" fill="#f0f1f3" stroke="var(--border)"/>
  <text x="265" y="126" text-anchor="middle" font-size="8" fill="var(--ink)">MCAL</text>
  <rect x="110" y="140" width="200" height="20" fill="#e9eaec" rx="3"/>
  <text x="210" y="154" text-anchor="middle" font-size="9" fill="var(--muted)">MCU 하드웨어</text>
</svg>
<p class="diagram-caption">그림 1-1. AUTOSAR Classic 계층 구조</p>

## CDD: 표준만으로 안 될 때
표준 BSW 모듈만으로 처리하기 어려운 특수 하드웨어나 엄격한 실시간 요구사항은 **CDD(Complex Device Driver)** 로 별도 구현합니다. 이 전체를 개발·검증하는 프로세스 성숙도를 평가하는 표준이 **ASPICE(Automotive SPICE)** 입니다.

다음 레슨에서는 1챕터에서 본 HPC처럼 여러 기능을 통합 처리하는 컴퓨팅 유닛을 위한 새 표준, AUTOSAR Adaptive를 봅니다."""),

        (2, "AUTOSAR Adaptive: SOA와 ara::com", """1강에서 본 Classic의 정적인 구조는, 1챕터에서 본 HPC처럼 여러 기능을 통합 처리하는 고성능 컴퓨팅 유닛에는 맞지 않습니다. 이를 위한 새 표준이 Adaptive입니다.

## 서비스 지향 아키텍처
**AUTOSAR Adaptive**는 서비스 지향 아키텍처(SOA)를 기반으로 합니다. 2챕터에서 다룬 SOME/IP를 표준 통신 수단으로 삼아 ECU 간 통신을 **ara::com**이라는 미들웨어 API로 추상화합니다.

## 통신 방식을 몰라도 되는 개발자
덕분에 개발자는 통신이 실제로 SOME/IP로 나가는지 공유 메모리로 처리되는지 신경 쓰지 않고, 이벤트·메서드·필드 같은 패턴만으로 기능을 구현할 수 있습니다. 이는 2챕터에서 본 인터페이스가 호스트에게 LBA만 보여주고 나머지를 감추는 것과 비슷한 발상입니다 — 복잡한 통신 디테일을 추상화 계층 뒤로 숨기는 것입니다.

다음 레슨에서는 이 표준 위에서 실제로 SW를 무선으로 배포하는 OTA와, SDV 전환의 흐름을 봅니다."""),

        (3, "SDV와 OTA", """1\~2강에서 AUTOSAR Classic/Adaptive라는 SW 구조 표준을 봤습니다. 이 표준 위에서 실제로 SW를 배포하고 발전시키는 방식을 봅니다.

## 무선으로 SW를 갱신한다
**OTA(Over-The-Air)** 는 SW를 무선으로 원격 업데이트하는 방식입니다. 유엔 규정 **UNECE R156**과 그에 대응하는 **SUMS(Software Update Management System)** 는 OTA 업데이트를 안전하게 관리하도록 요구하는 규정·시스템입니다.

## 플랫폼을 공유하려는 흐름
최근에는 완성차·부품사가 각자 폐쇄형 SW 스택을 중복 개발하는 대신, **Eclipse S-CORE** 같은 오픈소스 차량 SW 플랫폼이나 트라톤의 **One OS**처럼 자체 통합 플랫폼을 외부에 개방하는 시도도 늘고 있습니다. 이는 1강의 AUTOSAR가 애초에 추구했던 "공통 표준으로 중복 개발을 줄인다"는 목표의 연장선입니다.

## 챕터를 마치며
1강 AUTOSAR Classic → 2강 AUTOSAR Adaptive → 3강 SDV/OTA까지, 차량 SW가 표준화되고 원격으로 업데이트되는 흐름을 봤습니다. 다음 챕터에서는 이렇게 SW로 제어되는 범위가 넓어질수록 더 중요해지는 기능안전과 사이버보안을 다룹니다."""),
    ],

    "functional-safety": [
        (1, "ISO 26262와 ASIL", """3챕터에서 본 SW 플랫폼과 OTA 덕분에 차량은 점점 더 소프트웨어로 제어됩니다. 이 말은 곧 SW 오류가 실제 사고로 이어질 수 있다는 뜻입니다. 먼저 이 위험을 관리하는 기능안전 표준을 봅니다.

## 위험도에 등급을 매기다
**ISO 26262**는 차량용 전기전자 시스템의 기능안전을 다루는 국제표준입니다. 시스템이 고장 났을 때 생길 수 있는 위험의 심각도·노출빈도·통제가능성을 따져 **ASIL(Automotive Safety Integrity Level)** 이라는 등급(QM, A\~D)을 매깁니다.

<svg viewBox="0 0 420 150" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="16" font-size="10" fill="var(--ink)" font-weight="700">ASIL 등급별 요구 엄격도 (대략)</text>
  <text x="10" y="44" font-size="9" fill="var(--muted)">QM</text>
  <rect x="50" y="34" width="30" height="16" fill="#f0f1f3" stroke="var(--border)"/>
  <text x="10" y="69" font-size="9" fill="var(--muted)">A</text>
  <rect x="50" y="59" width="80" height="16" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="10" y="94" font-size="9" fill="var(--muted)">B</text>
  <rect x="50" y="84" width="140" height="16" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="10" y="119" font-size="9" fill="var(--muted)">C</text>
  <rect x="50" y="109" width="220" height="16" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="10" y="144" font-size="9" fill="var(--muted)">D</text>
  <rect x="50" y="134" width="320" height="16" fill="var(--accent)"/>
  <text x="380" y="146" font-size="8" fill="var(--ink)">브레이크·조향 등</text>
</svg>
<p class="diagram-caption">그림 1-1. QM에서 ASIL D로 갈수록 요구되는 설계 검증 수준이 커진다</p>

## 등급이 실무에 미치는 영향
등급이 높을수록(D가 최고) 더 엄격한 설계 검증과 테스트를 요구합니다. 브레이크나 조향처럼 고장이 곧 사고로 이어지는 시스템일수록 높은 ASIL 등급이 붙어, 개발·검증 비용도 함께 늘어납니다.

다음 레슨에서는 SW가 무선으로 연결되면서 새롭게 중요해진 사이버보안 표준을 봅니다."""),

        (2, "TARA와 UNECE R155: 사이버보안", """1강에서 본 기능안전이 "고장에 어떻게 대응할 것인가"를 다뤘다면, 이번 레슨은 "누군가 악의적으로 조작하려 하면 어떻게 막을 것인가"를 봅니다.

## 위협을 먼저 분석한다
**TARA(Threat Analysis and Risk Assessment)** 는 차량 시스템에 어떤 위협이 있을 수 있는지 미리 분석하고 위험도를 평가하는 절차입니다. 3챕터에서 본 OTA처럼 무선으로 SW를 업데이트할 수 있는 경로는, 거꾸로 공격자가 악성 SW를 주입할 수 있는 경로도 됩니다.

## 규제로 강제되는 보안 체계
유엔 규정 **UNECE R155**는 완성차 업체가 이런 위협분석을 포함한 사이버보안 관리체계(CSMS)를 갖추도록 강제하는 규제로, 3챕터의 UNECE R156(OTA)과 함께 최근 차량 인증의 필수 요건이 되고 있습니다. 즉 R155는 "보안을 어떻게 관리할 것인가"를, R156은 "SW 업데이트를 어떻게 안전하게 할 것인가"를 각각 규정하며 서로 맞물립니다.

다음 레슨에서는 실제로 SW가 변조되지 않았는지 확인하는 기술적 방법과, 반도체 부품 자체의 신뢰성 인증을 봅니다."""),

        (3, "무결성 검증과 부품 신뢰성", """1\~2강에서 기능안전(ISO 26262)과 사이버보안 체계(TARA, R155)를 봤습니다. 이번 레슨은 이를 실제로 구현하는 기술적 방법을 봅니다.

## CRC와 디지털 서명은 무엇이 다른가
ECU 펌웨어가 전송 중 손상되지 않았는지, 혹은 다른 사람이 몰래 바꿔치기하지 않았는지 확인하는 방법은 목적에 따라 다릅니다. **CRC(Cyclic Redundancy Check)** 는 계산이 빨라 우발적인 데이터 손상(전송 중 비트 에러 등)을 빠르게 검출하지만, 누군가 의도적으로 데이터를 바꾸고 CRC 값도 같이 재계산해 버리면 막을 수 없습니다. 반대로 **디지털 서명(Digital Signature)** 은 개인키로 서명하고 공개키로 검증하는 비대칭 암호 방식이라, 서명자만 알고 있는 개인키 없이는 위조가 불가능해 의도적인 변조까지 막아줍니다.

## AEC-Q100: 부품 자체의 신뢰성
소프트웨어뿐 아니라 반도체 부품 자체도 검증이 필요합니다. **AEC-Q100**은 차량용 반도체가 극한 온도와 진동 등 가혹한 환경에서도 오래 견디는지 검증하는 업계 표준 신뢰성 인증으로, 이 인증을 통과하지 못한 칩은 대부분 완성차에 채택되지 않습니다.

## 챕터를 마치며
1강 ISO 26262/ASIL → 2강 TARA/UNECE R155 → 3강 무결성 검증/AEC-Q100까지, 차량이 SW로 제어될수록 왜 안전과 보안을 함께 다뤄야 하는지 봤습니다. 마지막 챕터에서는 이 안전한 기반 위에서 실제로 사용자가 체감하는 ADAS 같은 응용 소프트웨어를 다룹니다."""),
    ],

    "adas": [
        (1, "Vehicle Motion Management", """1챕터의 Zonal/HPC 구조, 2챕터의 고대역폭 통신, 3챕터의 SDV 플랫폼, 4챕터의 기능안전까지 — 이 모든 게 필요했던 이유는 결국 이번 챕터에서 다루는 무거운 응용을 안전하게 돌리기 위해서입니다. 먼저 섀시 제어를 통합하는 기술을 봅니다.

## 흩어져 있던 섀시 제어
전통적으로 서스펜션·제동·구동·조향은 각각 별도 ECU가 따로 제어했습니다. **Vehicle Motion Management**는 이 섀시 기능들을 하나의 소프트웨어 레이어에서 통합 제어하는 개념입니다.

## Zonal/HPC 구조가 만든 가능성
1챕터에서 본 Zonal/HPC 구조 덕분에 여러 섀시 신호를 한 곳에서 모아 처리할 수 있게 되면서 가능해졌습니다. 예를 들어 급제동과 동시에 조향을 미세 조정해 차량 안정성을 높이는 식의 협조 제어가 이런 통합 위에서 이뤄집니다. 이는 1챕터에서 배선이 짧아지고 연산이 집중되면 SW로 새 기능을 만들기 쉬워진다고 했던 바로 그 사례입니다.

다음 레슨에서는 이 통합 제어가 가능하게 만든 또 다른 축, 조향 자체를 전자화한 Steer-by-Wire를 봅니다."""),

        (2, "Steer-by-Wire", """1강의 Vehicle Motion Management가 여러 섀시 기능을 통합하는 소프트웨어 층이었다면, Steer-by-Wire는 그중 조향 자체를 근본적으로 바꾸는 기술입니다.

## 기계적 연결을 걷어내다
**Steer-by-Wire**는 스티어링 휠과 바퀴 사이의 기계적 연결을 없애고, 전자 신호로 조향을 제어하는 방식입니다. 기계적 제약이 없어 스티어링 각도나 반응 특성을 소프트웨어로 자유롭게 튜닝할 수 있고, 자율주행 시 운전대가 필요 없는 형태의 실내 설계도 가능해져 SDV 설계에서 자주 언급됩니다.

## 왜 기능안전이 특히 엄격한가
다만 전자 신호 하나에 조향 전체를 맡기는 구조이기 때문에, 4챕터에서 다룬 기능안전(ASIL D급 요구가 흔함)이 특히 엄격하게 적용되는 영역이기도 합니다. 기계적 백업이 없다는 것은 곧 전자 시스템의 고장이 바로 조향 상실로 이어질 수 있다는 뜻이라, 이중화된 센서·액추에이터·전원 설계가 필수적입니다.

다음 레슨에서는 이렇게 배포된 SW가 실제 도로에서 어떻게 계속 개선되는지 — Data Flywheel을 보고 자동차 트랙을 마무리합니다."""),

        (3, "Data Flywheel과 트랙 마무리", """1\~2강에서 섀시 통합 제어와 Steer-by-Wire라는 "지금의" 응용 기술을 봤습니다. 마지막으로 이런 응용이 계속 좋아지는 원리를 봅니다.

## 도로에서 배운 걸 다시 도로로
자율주행 SW는 한 번 배포하고 끝나는 게 아니라, 실제 주행에서 나오는 데이터로 계속 개선됩니다. **Data Flywheel**은 현장 차량이 수집한 주행 데이터를 AI 학습에 활용하고, 개선된 모델을 다시 현장에 배치하는 흐름을 지속적으로 순환시키는 폐루프 구조입니다.

<svg viewBox="0 0 420 190" xmlns="http://www.w3.org/2000/svg">
  <circle cx="210" cy="95" r="70" fill="none" stroke="var(--border)" stroke-width="2" stroke-dasharray="6 4"/>
  <circle cx="210" cy="25" r="30" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="210" y="21" text-anchor="middle" font-size="9" fill="#1c4a44">주행 데이터</text>
  <text x="210" y="33" text-anchor="middle" font-size="9" fill="#1c4a44">수집</text>
  <circle cx="285" cy="140" r="30" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="285" y="136" text-anchor="middle" font-size="9" fill="#1c4a44">AI</text>
  <text x="285" y="148" text-anchor="middle" font-size="9" fill="#1c4a44">모델 학습</text>
  <circle cx="135" cy="140" r="30" fill="var(--accent-soft)" stroke="var(--accent)"/>
  <text x="135" y="136" text-anchor="middle" font-size="9" fill="#1c4a44">OTA로</text>
  <text x="135" y="148" text-anchor="middle" font-size="9" fill="#1c4a44">현장 배치</text>
  <path d="M235,45 L265,115" stroke="var(--accent)" stroke-width="1.5" marker-end="url(#fw)"/>
  <path d="M255,150 L165,150" stroke="var(--accent)" stroke-width="1.5" marker-end="url(#fw)"/>
  <path d="M155,115 L185,45" stroke="var(--accent)" stroke-width="1.5" marker-end="url(#fw)"/>
  <defs>
    <marker id="fw" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto">
      <path d="M0,0 L7,3.5 L0,7 z" fill="var(--accent)"/>
    </marker>
  </defs>
</svg>
<p class="diagram-caption">그림 3-1. Data Flywheel — 수집·학습·배치가 계속 순환</p>

## OTA가 이 순환의 배포를 담당한다
3챕터의 OTA가 바로 이 순환의 "배포" 단계를 담당합니다 — Data Flywheel이 도는 속도는 결국 OTA 인프라가 얼마나 안정적이고 빠른지에 달려 있습니다.

## 자동차 트랙을 마치며
1챕터 하드웨어 배치(Zonal/HPC)에서 시작해, 2챕터 통신(CAN/이더넷/SOME-IP)으로 연결하고, 3챕터 AUTOSAR/SDV 플랫폼으로 SW 구조를 표준화하고, 4챕터 기능안전·보안으로 신뢰성을 확보한 뒤, 마지막으로 그 위에서 동작하는 ADAS 응용까지 왔습니다. 이제 자동차 SW 뉴스를 볼 때 "이 기사는 어느 계층 이야기인가"를 구분할 수 있는 기본기가 갖춰졌습니다."""),
    ],
}


class Command(BaseCommand):
    help = "챕터를 하위 레슨(Lesson) 여러 개로 채운다."

    def handle(self, *args, **kwargs):
        total = 0
        for slug, pages in LESSON_PAGES.items():
            chapter = Tag.objects.filter(slug=slug).first()
            if not chapter:
                self.stdout.write(self.style.WARNING(f"챕터 없음: {slug}"))
                continue
            for order, title, body in pages:
                Lesson.objects.update_or_create(
                    chapter=chapter, order=order, defaults={"title": title, "body": body}
                )
                total += 1
        self.stdout.write(self.style.SUCCESS(f"{total}개 레슨 저장 완료"))
