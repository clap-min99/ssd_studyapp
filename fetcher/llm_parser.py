"""
다이제스트 메일 원문을 Claude API로 구조화하는 파서.

정규식과 달리 매일 포맷이 조금씩 달라져도(■/①/1) 등) 의미 기반으로
안정적으로 뽑아낸다.

사전 준비:
    pip install anthropic
    환경변수 ANTHROPIC_API_KEY 설정
        (Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-...")
        (Git Bash: export ANTHROPIC_API_KEY="sk-ant-...")
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import anthropic
from dotenv import load_dotenv

load_dotenv()  # 프로젝트 루트의 .env 파일을 읽어서 환경변수로 등록

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """\
너는 SSD/NAND 컨트롤러 펌웨어 및 자동차 SW 취업 준비를 위한 데일리 뉴스 \
다이제스트 이메일을 구조화된 JSON으로 변환하는 파서다.

입력 메일은 매일 형식이 조금씩 다를 수 있다 (■/①/1) 같은 기호 차이, \
섹션 제목 표현 차이 등). 기호에 의존하지 말고 내용의 의미로 판단해서 분류하라.

반드시 아래 JSON 스키마로만 응답하라. 다른 설명, 마크다운 코드펜스, \
전언은 절대 포함하지 마라. 순수 JSON 객체 하나만 출력하라.

{
  "date": "YYYY-MM-DD",
  "articles": [
    {
      "title": "기사 제목",
      "links": ["url1", "url2"],
      "summary": "요약 (원문 문장 그대로 복사하지 말고 핵심만)",
      "insight": "인사이트",
      "category": "ssd" 또는 "automotive"
    }
  ],
  "no_article_categories": ["ssd", "automotive"],
  "learning_items": [
    {"heading": "소제목", "body": "본문 내용 요약"}
  ],
  "terms": [
    {"term": "용어", "meaning": "의미", "relevance": "펌웨어/개발과의 관련성 (있으면)"}
  ]
}

규칙:
- 기사가 없다고 명시된 카테고리는 "no_article_categories"에 넣고 articles에는 넣지 마라.
- 기사에 링크가 여러 개(예: 배경 링크) 있으면 links 배열에 모두 넣어라.
- summary/insight/body는 원문을 과도하게 그대로 베끼지 말고 핵심만 정리하라.
- 날짜는 메일 제목이나 본문에서 찾은 [YYYY-MM-DD] 형식을 사용하라. 못 찾으면 null.
"""


@dataclass
class Article:
    title: str
    links: list[str] = field(default_factory=list)
    summary: str = ""
    insight: str = ""
    category: str = ""


@dataclass
class LearningItem:
    heading: str
    body: str


@dataclass
class Term:
    term: str
    meaning: str
    relevance: str = ""


@dataclass
class ParsedDigest:
    date: str | None = None
    articles: list[Article] = field(default_factory=list)
    learning_items: list[LearningItem] = field(default_factory=list)
    terms: list[Term] = field(default_factory=list)
    no_article_categories: list[str] = field(default_factory=list)


def parse_digest_with_llm(raw_text: str) -> ParsedDigest:
    """다이제스트 원문을 Claude API로 구조화한다."""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw_text}],
    )

    text = response.content[0].text.strip()

    # 혹시 모델이 코드펜스를 붙였을 경우 대비한 방어 코드
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    data = json.loads(text)

    return ParsedDigest(
        date=data.get("date"),
        articles=[Article(**a) for a in data.get("articles", [])],
        learning_items=[LearningItem(**li) for li in data.get("learning_items", [])],
        terms=[Term(**t) for t in data.get("terms", [])],
        no_article_categories=data.get("no_article_categories", []),
    )


if __name__ == "__main__":
    # fetcher/gmail_client.py 로 가져온 실제 메일 원문을 여기 붙여넣어 테스트하거나,
    # gmail_client.fetch_latest_digest()와 연결해서 사용한다.
    sample = """[2026-09-10] SSD/자동차 SW 펌웨어 데일리 브리핑

1. SSD/NAND 컨트롤러

오늘은 관련 기사가 없었습니다 (24~48시간 이내 신규 기사 없음, 6일 연속).

■ 오늘의 학습 콘텐츠 (SSD/NAND)

① NVMe 큐 구조와 컨트롤러 펌웨어 처리 흐름
NVMe는 호스트와 SSD 사이에 Submission Queue(SQ)와 Completion Queue(CQ)를 두고
커맨드를 비동기로 처리한다...
"""
    parsed = parse_digest_with_llm(sample)
    print(f"날짜: {parsed.date}")
    print(f"기사 {len(parsed.articles)}건, 학습콘텐츠 {len(parsed.learning_items)}건, 용어 {len(parsed.terms)}건")
    print(f"기사 없음 카테고리: {parsed.no_article_categories}")
    for li in parsed.learning_items:
        print(" -", li.heading)