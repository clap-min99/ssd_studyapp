"""
다이제스트 메일 원문을 Gemini API(무료 티어)로 구조화하는 파서.
llm_parser.py(Claude 버전)와 로직은 동일하고, 호출하는 API만 다르다.

사전 준비:
    pip install google-genai python-dotenv
    https://aistudio.google.com/apikey 에서 무료 API 키 발급 (카드 등록 불필요)
    .env 파일에 추가:
        GEMINI_API_KEY=여기에-키

무료 티어 한도(2026-09 기준, 모델에 따라 달라질 수 있음):
    분당 요청 수, 일일 요청 수 제한이 있지만 "하루 1회 파싱" 용도로는 충분히 넉넉함.
    한도를 초과하면 google.genai가 예외를 던지므로 다음날 다시 시도하면 됨.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# 무료 티어에서 넉넉하게 제공되는 모델. 만약 이 모델명이 만료/변경되었다는
# 오류가 나면 https://aistudio.google.com 에서 현재 사용 가능한 모델명을 확인해서
# 아래 MODEL 값만 바꿔주면 된다.
MODEL = "gemini-3.6-flash"

SYSTEM_PROMPT = """\
너는 SSD/NAND 컨트롤러 펌웨어 및 자동차 SW 취업 준비를 위한 데일리 뉴스 \
다이제스트 이메일을 구조화된 JSON으로 변환하는 파서다.

입력 메일은 매일 형식이 조금씩 다를 수 있다 (■/①/1) 같은 기호 차이, \
섹션 제목 표현 차이 등). 기호에 의존하지 말고 내용의 의미로 판단해서 분류하라.

반드시 아래 JSON 스키마로만 응답하라.

{
  "date": "YYYY-MM-DD",
  "articles": [
    {
      "title": "기사 제목",
      "links": ["url1", "url2"],
      "summary": "요약 (원문 문장 그대로 복사하지 말고 핵심만)",
      "insight": "인사이트",
      "category": "ssd" 또는 "automotive",
      "tags": ["slug1", "slug2"]
    }
  ],
    }
  ],
  "no_article_categories": ["ssd", "automotive"],
    "learning_items": [
    {"heading": "소제목", "body": "본문 내용 요약", "tags": ["slug1", "slug2"]}
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
- tags는 아래 목록의 slug 중 기사 내용에 해당하는 것을 전부 골라라 (없으면 빈 배열).

사용 가능한 태그:
  SSD: ftl, nand, interface, controller, reliability, emerging, market-ssd
  자동차: autosar, adas, semiconductor, battery, market-auto
"""


@dataclass
class Article:
    title: str
    links: list[str] = field(default_factory=list)
    summary: str = ""
    insight: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class LearningItem:
    heading: str
    body: str
    tags: list[str] = field(default_factory=list)

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


def _get_client() -> genai.Client:
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _none_to_empty(d: dict) -> dict:
    """Gemini가 선택 필드에 값 대신 null을 줄 때가 있어서, None을 정리한다.
    (DB의 TextField는 NULL을 허용하지 않는데, dataclass 기본값 ""는 명시적 None이
    들어오면 무시되고 그대로 None이 통과해버리는 문제가 있었다.)
    "links"만 리스트 필드라 None이면 빈 리스트로, 나머지는 빈 문자열로 채운다.
    """
    cleaned = {}
    for k, v in d.items():
        if v is not None:
            cleaned[k] = v
        elif k in ("links", "tags"):
            cleaned[k] = []
        else:
            cleaned[k] = ""
    return cleaned


def parse_digest_with_gemini(raw_text: str) -> ParsedDigest:
    """다이제스트 원문을 Gemini API로 구조화한다."""

    client = _get_client()

    response = client.models.generate_content(
        model=MODEL,
        contents=raw_text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    text = response.text.strip()

    # response_mime_type="application/json" 덕분에 보통은 순수 JSON만 오지만,
    # 혹시 모를 코드펜스에 대비한 방어 코드
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    data = json.loads(text)

    return ParsedDigest(
        date=data.get("date"),
        articles=[Article(**_none_to_empty(a)) for a in data.get("articles", [])],
        learning_items=[LearningItem(**_none_to_empty(li)) for li in data.get("learning_items", [])],
        terms=[Term(**_none_to_empty(t)) for t in data.get("terms", [])],
        no_article_categories=data.get("no_article_categories", []),
    )


ANSWER_CHECK_SYSTEM_PROMPT = """\
너는 SSD/NAND 컨트롤러 펌웨어 취업 준비생의 용어 복습을 도와주는 첨삭자다.

사용자에게 용어 하나가 주어지고, 사용자는 그 뜻을 자기 언어로 설명한다.
사용자의 설명을 "정답 의미"와 비교해서, 사전적으로 똑같은지가 아니라
핵심 개념을 제대로 짚었는지를 기준으로 평가하라.

반드시 아래 JSON 스키마로만 응답하라.

{
  "verdict": "correct" 또는 "partial" 또는 "wrong",
  "feedback": "한두 문장. 무엇을 잘 짚었고 무엇이 빠졌는지 구체적으로"
}

기준:
- correct: 핵심 개념을 정확히 이해하고 설명함 (표현이 다소 서툴러도 괜찮음)
- partial: 방향은 맞지만 중요한 부분이 빠졌거나 부정확함
- wrong: 핵심을 잘못 이해했거나 answer가 무관함
- feedback은 채점하듯 말하지 말고, 빠진 부분을 짚어주는 톤으로 (예: "GC의 기본 동작은 잘 짚었지만, Write Amplification과의 연관성이 빠졌어요")
"""


def check_term_answer(term: str, meaning: str, relevance: str, user_answer: str) -> dict:
    """사용자가 직접 쓴 용어 설명을 Gemini로 채점한다.

    Returns:
        {"verdict": "correct" | "partial" | "wrong", "feedback": "..."}
    """
    client = _get_client()

    prompt = (
        f"용어: {term}\n"
        f"정답 의미: {meaning}\n"
        f"펌웨어와의 관련성: {relevance or '(없음)'}\n"
        f"사용자의 설명: {user_answer}"
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=ANSWER_CHECK_SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


if __name__ == "__main__":
    sample = """[2026-09-10] SSD/자동차 SW 펌웨어 데일리 브리핑

1. SSD/NAND 컨트롤러

오늘은 관련 기사가 없었습니다 (24~48시간 이내 신규 기사 없음, 6일 연속).

■ 오늘의 학습 콘텐츠 (SSD/NAND)

① NVMe 큐 구조와 컨트롤러 펌웨어 처리 흐름
NVMe는 호스트와 SSD 사이에 Submission Queue(SQ)와 Completion Queue(CQ)를 두고
커맨드를 비동기로 처리한다...
"""
    parsed = parse_digest_with_gemini(sample)
    print(f"날짜: {parsed.date}")
    print(f"기사 {len(parsed.articles)}건, 학습콘텐츠 {len(parsed.learning_items)}건, 용어 {len(parsed.terms)}건")
    print(f"기사 없음 카테고리: {parsed.no_article_categories}")
    for li in parsed.learning_items:
        print(" -", li.heading)
        

@dataclass
class Article:
    title: str
    links: list[str] = field(default_factory=list)
    summary: str = ""
    insight: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)

TAG_SYSTEM_PROMPT = """\
너는 SSD/자동차 SW 뉴스 기사에 알맞은 태그를 골라주는 분류기다.

반드시 아래 JSON 스키마로만 응답하라.

{
  "tags": ["slug1", "slug2"]
}

사용 가능한 태그:
  SSD: ftl, nand, interface, controller, reliability, emerging, market-ssd
  자동차: autosar, adas, semiconductor, battery, market-auto

기사 내용에 해당하는 태그를 전부 골라라 (없으면 빈 배열). 목록에 없는 태그는 만들지 마라.
"""


def tag_article(title: str, summary: str, category: str) -> list[str]:
    """기존 기사(제목/요약)를 보고 알맞은 태그 slug 목록을 고른다. 백필용."""
    client = _get_client()
    prompt = f"제목: {title}\n요약: {summary}\n카테고리: {category}"

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=TAG_SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text).get("tags", [])