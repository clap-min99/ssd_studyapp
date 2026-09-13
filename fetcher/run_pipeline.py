"""
Gmail에서 최신 다이제스트 메일을 가져와 Gemini로 구조화까지 한 번에 처리.

실행:
    python fetcher/run_pipeline.py

이 스크립트가 하는 일:
    1. gmail_client.fetch_latest_digest() 로 최근 메일 원문 가져오기
    2. gemini_parser.parse_digest_with_gemini() 로 구조화
    3. 결과를 보기 좋게 출력 (다음 단계에서 여기 자리에 "DB 저장" 코드가 들어감)
"""

from __future__ import annotations

from gmail_client import fetch_latest_digest
from gemini_parser import parse_digest_with_gemini, ParsedDigest


def print_parsed_digest(parsed: ParsedDigest) -> None:
    print(f"\n{'=' * 50}")
    print(f"날짜: {parsed.date}")
    print(f"{'=' * 50}")

    if parsed.articles:
        print(f"\n[기사 {len(parsed.articles)}건]")
        for a in parsed.articles:
            print(f"\n- ({a.category}) {a.title}")
            if a.links:
                print(f"  링크: {', '.join(a.links)}")
            if a.summary:
                print(f"  요약: {a.summary}")
            if a.insight:
                print(f"  인사이트: {a.insight}")

    if parsed.no_article_categories:
        print(f"\n[기사 없음]: {', '.join(parsed.no_article_categories)}")

    if parsed.learning_items:
        print(f"\n[학습 콘텐츠 {len(parsed.learning_items)}건]")
        for li in parsed.learning_items:
            print(f"\n- {li.heading}")
            print(f"  {li.body[:100]}{'...' if len(li.body) > 100 else ''}")

    if parsed.terms:
        print(f"\n[용어 {len(parsed.terms)}건]")
        for t in parsed.terms:
            print(f"- {t.term}: {t.meaning}")
            if t.relevance:
                print(f"  (관련성: {t.relevance})")


def main() -> None:
    print("Gmail에서 최신 다이제스트 메일 확인 중...")
    digest = fetch_latest_digest()

    if digest is None:
        print("최근 다이제스트 메일을 찾지 못했습니다.")
        return

    print(f"메일 발견: {digest['subject']}")
    print("Gemini로 구조화 중...")

    parsed = parse_digest_with_gemini(digest["body"])
    print_parsed_digest(parsed)


if __name__ == "__main__":
    main()