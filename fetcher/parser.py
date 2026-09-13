"""
데일리 다이제스트 원문 텍스트를 구조화된 dict로 변환하는 파서.

입력 형식 예시:

    ■ 1. SSD/NAND 컨트롤러

    1) 기사 제목
    - 링크: https://...
    - 요약: ...
    - 인사이트: ...

    ■ 2. 자동차 SW/펌웨어

    (기사 없음 또는 위와 동일한 형식)

    [오늘의 학습 콘텐츠] / ## 오늘의 학습 콘텐츠
    1) 소제목
    본문...

    용어 설명 / ■ 용어 설명
    - 용어: 설명
"""

import re
from dataclasses import dataclass, field


@dataclass
class Article:
    title: str
    links: list[str] = field(default_factory=list)
    summary: str = ""
    insight: str = ""
    category: str = ""  # "ssd" 또는 "automotive"


@dataclass
class LearningItem:
    heading: str
    body: str


@dataclass
class Term:
    term: str
    meaning: str


@dataclass
class ParsedDigest:
    articles: list[Article] = field(default_factory=list)
    learning_items: list[LearningItem] = field(default_factory=list)
    terms: list[Term] = field(default_factory=list)
    no_article_sections: list[str] = field(default_factory=list)  # "기사 없음" 표시된 섹션


# 섹션을 나누는 기준선들. 순서대로 매칭을 시도한다.
SECTION_SSD = re.compile(r"■\s*1\.\s*SSD.*?컨트롤러")
SECTION_AUTO = re.compile(r"■\s*2\.\s*자동차")
SECTION_LEARNING = re.compile(r"(\[오늘의 학습 콘텐츠\]|##?\s*오늘의 학습 콘텐츠)")
SECTION_TERMS = re.compile(r"(■\s*용어 설명|용어 설명\s*\n)")

# 기사 항목: "1) 제목" 다음에 "- 링크:", "- 요약:", "- 인사이트:" 가 따라옴
ARTICLE_BLOCK = re.compile(
    r"\d+\)\s*(?P<title>.+?)\n"
    r"(?P<meta>(?:-[^\n]*\n?)+)",
)
LINK_LINE = re.compile(r"-\s*링크(?:\(.*?\))?:\s*(\S+)")
SUMMARY_LINE = re.compile(r"-\s*요약:\s*(.+)")
INSIGHT_LINE = re.compile(r"-\s*인사이트:\s*(.+)")

# 학습 콘텐츠: "1) 소제목\n본문..."
LEARNING_BLOCK = re.compile(r"\d+\)\s*(?P<heading>.+?)\n(?P<body>.+?)(?=\n\d+\)|\Z)", re.S)

# 용어 설명: "- 용어: 의미" 또는 "- 용어(영문): 의미"
TERM_LINE = re.compile(r"-\s*([^:：]+?)\s*[:：]\s*(.+)")


def _slice_between(text: str, start_pattern: re.Pattern, end_patterns: list[re.Pattern]) -> str:
    """start_pattern이 매칭된 지점부터, end_patterns 중 가장 먼저 나오는 지점 전까지 잘라낸다."""
    start_match = start_pattern.search(text)
    if not start_match:
        return ""
    start_idx = start_match.end()

    end_idx = len(text)
    for pat in end_patterns:
        m = pat.search(text, pos=start_idx)
        if m and m.start() < end_idx:
            end_idx = m.start()

    return text[start_idx:end_idx].strip()


def _parse_articles(section_text: str, category: str) -> tuple[list[Article], bool]:
    """섹션 텍스트에서 기사 목록을 뽑는다. (기사 목록, '기사 없음' 여부) 반환."""
    if not section_text or "관련 기사가 없" in section_text or "기사가 확인되지 않" in section_text:
        return [], True

    articles = []
    for block in ARTICLE_BLOCK.finditer(section_text):
        title = block.group("title").strip()
        meta = block.group("meta")

        links = LINK_LINE.findall(meta)
        summary_m = SUMMARY_LINE.search(meta)
        insight_m = INSIGHT_LINE.search(meta)

        articles.append(
            Article(
                title=title,
                links=links,
                summary=summary_m.group(1).strip() if summary_m else "",
                insight=insight_m.group(1).strip() if insight_m else "",
                category=category,
            )
        )
    return articles, False


def _parse_learning_items(section_text: str) -> list[LearningItem]:
    items = []
    for block in LEARNING_BLOCK.finditer(section_text):
        heading = block.group("heading").strip()
        body = block.group("body").strip()
        items.append(LearningItem(heading=heading, body=body))
    return items


def _parse_terms(section_text: str) -> list[Term]:
    terms = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        m = TERM_LINE.match(line)
        if m:
            terms.append(Term(term=m.group(1).strip(), meaning=m.group(2).strip()))
    return terms


def parse_digest(raw_text: str) -> ParsedDigest:
    """다이제스트 원문 전체를 파싱해서 ParsedDigest로 반환한다."""

    end_patterns = [SECTION_AUTO, SECTION_LEARNING, SECTION_TERMS]
    ssd_section = _slice_between(raw_text, SECTION_SSD, end_patterns)

    end_patterns = [SECTION_LEARNING, SECTION_TERMS]
    auto_section = _slice_between(raw_text, SECTION_AUTO, end_patterns)

    end_patterns = [SECTION_TERMS]
    learning_section = _slice_between(raw_text, SECTION_LEARNING, end_patterns)

    terms_match = SECTION_TERMS.search(raw_text)
    terms_section = raw_text[terms_match.end():].strip() if terms_match else ""

    result = ParsedDigest()

    ssd_articles, ssd_empty = _parse_articles(ssd_section, category="ssd")
    auto_articles, auto_empty = _parse_articles(auto_section, category="automotive")

    result.articles = ssd_articles + auto_articles
    if ssd_empty:
        result.no_article_sections.append("ssd")
    if auto_empty:
        result.no_article_sections.append("automotive")

    result.learning_items = _parse_learning_items(learning_section)
    result.terms = _parse_terms(terms_section)

    return result


if __name__ == "__main__":
    # 간단한 자체 테스트용 샘플 (9/8 다이제스트 축약본)
    sample = """■ 1. SSD/NAND 컨트롤러

1) SK하이닉스, Solidigm 프리IPO 루머에 "결정된 사항 없다" 공식 반박
- 링크: https://example.com/a
- 요약: SK하이닉스가 SEC 공시를 통해 프리IPO 추진설을 공식 부인했다.
- 인사이트: eSSD 컨트롤러/낸드 분야 3대 기업 중 하나인 Solidigm의 지배구조 변화 이슈.

■ 2. 자동차 SW/펌웨어

오늘은 관련 기사가 없었습니다.

## 오늘의 학습 콘텐츠

1) ISO 26262 기능안전 표준과 ASIL 등급 체계
자동차 SW 채용 공고에서 기능안전 경험을 요구하는 경우가 많다...

2) CAN FD와 CAN XL
기존 CAN의 대역폭 한계를 극복하기 위해...

용어 설명
- 프리IPO(Pre-IPO): 정식 상장 이전에 지분을 먼저 판매하는 단계.
- ASIL(Automotive Safety Integrity Level): 자동차 기능안전 위험도 등급.
"""
    parsed = parse_digest(sample)
    print(f"기사 {len(parsed.articles)}건, 학습콘텐츠 {len(parsed.learning_items)}건, 용어 {len(parsed.terms)}건")
    for a in parsed.articles:
        print(" -", a.title, "|", a.category, "|", a.links)
    for t in parsed.terms:
        print(" *", t.term, ":", t.meaning[:30])
