"""OpenAI Responses API를 사용하는 메일 파싱·해설·첨삭·태그 분류 모듈.

OPENAI_API_KEY 필수. OPENAI_MODEL로 기본 모델 지정 (기본 gpt-5.4-mini).
기능별 OPENAI_PARSE_MODEL / OPENAI_EXPLAIN_MODEL / OPENAI_REVIEW_MODEL /
OPENAI_TAG_MODEL 설정은 기본 모델보다 우선 적용.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from fetcher.source_order import order_from_source

from dotenv import load_dotenv
from openai import OpenAI

from fetcher.ai_schemas import AnswerOutput, DigestOutput, SourcesOutput, TagsOutput

load_dotenv()

DEFAULT_MODEL = "gpt-5.4-mini"


def get_model(task: str) -> str:
    return (os.environ.get(f"OPENAI_{task.upper()}_MODEL", "").strip()
            or os.environ.get("OPENAI_MODEL", "").strip() or DEFAULT_MODEL)


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
      "tags": ["slug1", "slug2"],
      "source_text": "메일 원문에서 이 기사에 해당하는 부분 (제목~인사이트까지, 글자 그대로 복사)"
    }
  ],
  "no_article_categories": ["ssd", "automotive"],
    "learning_items": [
    {"heading": "소제목", "body": "본문 내용 요약", "tags": ["slug1", "slug2"], "source_text": "메일 원문에서 이 학습 콘텐츠에 해당하는 부분 (소제목~본문 끝까지, 글자 그대로 복사)"}
  ],
  "terms": [
    {"term": "용어", "meaning": "의미", "relevance": "펌웨어/개발과의 관련성 (있으면)"}
  ]
}

규칙:
- 최우선은 원문의 독립된 기사·학습 항목을 빠짐없이 각각 별도 카드로 추출하는 것이다. 먼저 항목을 분리한 다음, 각 카드의 내용만 짧게 요약하라.
- 1·2·3, 1)·2)·3), ①·②·③ 등으로 구분되고 각각 고유한 제목·주제를 가진 항목은 하나당 articles 또는 learning_items의 객체 하나로 만들어라. 같은 분야나 비슷한 주제라는 이유로 여러 항목을 하나의 객체로 합치거나 누락하지 마라.
- SSD/자동차 같은 분야 제목이나 '오늘의 학습 콘텐츠' 같은 상위 섹션 제목을 카드 제목으로 삼아 그 아래 여러 항목을 한 카드에 몰아넣지 마라. title·heading에는 개별 항목의 제목을 사용하라.
- 분야별로 번호가 다시 1부터 시작해도 서로 다른 항목으로 유지하라. 단, 한 항목 본문 안의 설명 단계·예시·하위 목록은 그 항목에 포함하고 별도 카드로 쪼개지 마라.
- 분리 예시: SSD 학습 섹션에 '① NAND 구조', '② FTL 매핑', '③ GC 동작', 자동차 학습 섹션에 '① CAN 통신', '② AUTOSAR 구조'가 각각 독립된 제목과 본문으로 있으면 learning_items는 원문 순서대로 5개다. heading은 각각 'NAND 구조', 'FTL 매핑', 'GC 동작', 'CAN 통신', 'AUTOSAR 구조'이고, 분야별 2개나 통합 1개로 만들면 안 된다. 실제 항목 수는 매일 원문에 맞춰 결정하라.
- summary와 learning_items의 body는 각 개별 카드의 목록 화면용 요약이다. 해당 항목만 핵심 1~2문장, 공백 포함 150자 이내의 자연스러운 한국어로 작성하라. 요약을 위해 카드 개수를 줄이지 마라.
- 각 카드의 요약에는 해당 항목이 무엇에 관한 내용인지와 핵심 변화·개념만 담아라. 그 항목의 긴 배경 설명, 세부 절차, 예시는 요약에서 생략하되, 문장을 중간에 자르지 마라.
- insight는 개발·학습 관점의 의미를 1문장, 공백 포함 80자 이내로 작성하라. summary의 내용을 반복하지 마라.
- 짧은 요약과 별개로 source_text에는 해당 개별 항목의 제목부터 본문 끝까지 원문 전체를 보존하라. 다음 독립 항목의 제목·본문을 포함하지 마라.
- articles와 learning_items는 각각 메일 원문에 등장하는 순서를 그대로 유지하라. 카테고리/태그/중요도로 재정렬하지 마라.
- 기사가 없다고 명시된 카테고리는 "no_article_categories"에 넣고 articles에는 넣지 마라.
- 기사에 링크가 여러 개(예: 배경 링크) 있으면 links 배열에 모두 넣어라.
- source_text는 요약하거나 고치지 말고 원문 그대로 복사하라 (줄바꿈 포함).
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
    source_text: str = ""


@dataclass
class LearningItem:
    heading: str
    body: str
    tags: list[str] = field(default_factory=list)
    source_text: str = ""

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


def _get_client() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 또는 실행 환경의 Secret을 확인하세요.")
    return OpenAI(api_key=key, timeout=30.0, max_retries=2)


def _generate_json(prompt: str, schema, task: str, instructions: str = "") -> dict:
    response = _get_client().responses.parse(
        model=get_model(task), instructions=instructions,
        input=prompt, text_format=schema, store=False,
    )
    if response.status != "completed" or response.output_parsed is None:
        raise ValueError("OpenAI가 유효한 구조화 결과를 반환하지 않았습니다 (거절 또는 응답 미완료).")
    return response.output_parsed.model_dump()


def _none_to_empty(d: dict) -> dict:
    """OpenAI가 선택 필드에 값 대신 null을 줄 때가 있어서, None을 정리한다.
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


def parse_digest(raw_text: str) -> ParsedDigest:
    """다이제스트 원문을 OpenAI API로 구조화한다."""

    data = _generate_json(raw_text, DigestOutput, "parse", SYSTEM_PROMPT)

    parsed = ParsedDigest(
        date=data.get("date"),
        articles=[Article(**_none_to_empty(a)) for a in data.get("articles", [])],
        learning_items=[LearningItem(**_none_to_empty(li)) for li in data.get("learning_items", [])],
        terms=[Term(**_none_to_empty(t)) for t in data.get("terms", [])],
        no_article_categories=data.get("no_article_categories", []),
    )
    parsed.articles = order_from_source(raw_text, parsed.articles, "title")
    parsed.learning_items = order_from_source(raw_text, parsed.learning_items, "heading")
    return parsed


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
    """사용자가 직접 쓴 용어 설명을 OpenAI로 채점한다.

    Returns:
        {"verdict": "correct" | "partial" | "wrong", "feedback": "..."}
    """
    prompt = (
        f"용어: {term}\n"
        f"정답 의미: {meaning}\n"
        f"펌웨어와의 관련성: {relevance or '(없음)'}\n"
        f"사용자의 설명: {user_answer}"
    )

    return _generate_json(prompt, AnswerOutput, "review", ANSWER_CHECK_SYSTEM_PROMPT)


DEEP_DIVE_SYSTEM_PROMPT = """\
너는 SSD/NAND 컨트롤러·자동차 SW 펌웨어 취업 준비생의 공부를 도와주는 선배 엔지니어다.

다이제스트 메일 원문 전체와, 그 안의 항목 하나(기사 또는 학습 콘텐츠)가 주어진다.
이 항목을 처음 보는 사람도 이해할 수 있게 마크다운으로 풀어서 설명하라.
원문에 없는 사실을 지어내지 말고, 일반적인 배경지식은 배경지식이라고 구분해서 써라.

아래 섹션을 이 순서대로, ## 헤딩으로 작성하라.

## 쉽게 풀어보기
원문 내용을 쉬운 말로 다시 설명. 비유가 도움이 되면 사용.

## 알아야 할 배경지식
이 내용을 이해하려면 먼저 알아야 하는 개념들을 짧게 설명.

## 펌웨어 엔지니어 관점
이게 실제 펌웨어 개발(FTL, GC, 큐 처리, AUTOSAR 등 해당되는 것)에 어떤 의미인지.

## 더 공부할 거리
키워드와 "무엇을 찾아보면 좋은지"를 3~5개 bullet로. 면접에서 나올 만한 질문 1~2개 포함.
"""


def explain_item(title: str, body: str, raw_text: str) -> str:
    """카드 하나를 메일 원문 맥락과 함께 심화 해설(마크다운)로 풀어준다."""
    prompt = (
        f"[설명할 항목]\n제목: {title}\n내용: {body}\n\n"
        f"[다이제스트 메일 원문 전체]\n{raw_text}"
    )

    response = _get_client().responses.create(
        model=get_model("explain"), instructions=DEEP_DIVE_SYSTEM_PROMPT,
        input=prompt, store=False,
    )
    text = response.output_text.strip()
    if response.status != "completed" or not text:
        raise ValueError("OpenAI 해설 생성 결과가 비어 있거나 완료되지 않았습니다.")
    return text


def extract_sources(raw_text: str, titles: list[str]) -> list[str]:
    """메일 원문에서 각 항목(제목 목록)에 해당하는 부분을 원문 그대로 잘라 같은 순서로 돌려준다.
    이미 저장된 항목의 source_text를 채우는 백필용."""
    numbered = "\n".join(f"{i}. {t}" for i, t in enumerate(titles))
    prompt = (
        "아래 메일 원문에서 각 항목에 해당하는 부분(제목~그 항목 내용 끝까지)을 "
        "요약하거나 고치지 말고 줄바꿈까지 원문 그대로 잘라라. "
        "sources 필드에 항목 순서대로 문자열 배열을 담은 JSON 객체로 응답하라. 못 찾은 항목은 빈 문자열.\n\n"
        f"[항목]\n{numbered}\n\n[메일 원문]\n{raw_text}"
    )

    sources = _generate_json(prompt, SourcesOutput, "parse")["sources"]
    if len(sources) != len(titles):
        raise ValueError(f"항목 수 불일치: {len(titles)}개 요청, {len(sources)}개 응답")
    return sources


if __name__ == "__main__":
    sample = """[2026-09-10] SSD/자동차 SW 펌웨어 데일리 브리핑

1. SSD/NAND 컨트롤러

오늘은 관련 기사가 없었습니다 (24~48시간 이내 신규 기사 없음, 6일 연속).

■ 오늘의 학습 콘텐츠 (SSD/NAND)

① NVMe 큐 구조와 컨트롤러 펌웨어 처리 흐름
NVMe는 호스트와 SSD 사이에 Submission Queue(SQ)와 Completion Queue(CQ)를 두고
커맨드를 비동기로 처리한다...
"""
    parsed = parse_digest(sample)
    print(f"날짜: {parsed.date}")
    print(f"기사 {len(parsed.articles)}건, 학습콘텐츠 {len(parsed.learning_items)}건, 용어 {len(parsed.terms)}건")
    print(f"기사 없음 카테고리: {parsed.no_article_categories}")
    for li in parsed.learning_items:
        print(" -", li.heading)




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
    prompt = f"제목: {title}\n요약: {summary}\n카테고리: {category}"

    return _generate_json(prompt, TagsOutput, "tag", TAG_SYSTEM_PROMPT)["tags"]


TERM_TAG_SYSTEM_PROMPT = """\
너는 SSD/자동차 SW 용어 사전에 알맞은 태그를 골라주는 분류기다.

반드시 아래 JSON 스키마로만 응답하라.

{
  "tags": ["slug1", "slug2"]
}

사용 가능한 태그:
  SSD: ftl, nand, interface, controller, reliability, emerging, market-ssd
  자동차: autosar, adas, semiconductor, battery, market-auto

용어의 뜻풀이를 보고 가장 관련 있는 태그를 1~2개 골라라 (없으면 빈 배열). 목록에 없는 태그는 만들지 마라.
"""


def tag_term(term: str, meaning: str, relevance: str = "") -> list[str]:
    """용어 사전 항목(용어/뜻풀이)을 보고 알맞은 태그 slug 목록을 고른다. 백필용."""
    prompt = f"용어: {term}\n뜻풀이: {meaning}\n실무 연관성: {relevance}"

    return _generate_json(prompt, TagsOutput, "tag", TERM_TAG_SYSTEM_PROMPT)["tags"]
