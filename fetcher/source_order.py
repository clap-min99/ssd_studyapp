"""Locate extracted items in the email rather than trusting model array order."""

import re


NUMBERED_HEADING = re.compile(r"(?m)^(?P<indent>[ \t]*)(?P<marker>\(\d+\)|\d+\)|\d+\.(?=[ \t])|[①-⑳])[ \t]*(?P<title>[^\r\n]+)")


def validate_numbered_sources(raw_text, items):
    """Check sibling numbered headings against located cards, ignoring indented substeps."""
    headings = list(NUMBERED_HEADING.finditer(raw_text))
    if headings and not items:
        raise ValueError("번호로 구분된 원문 항목이 있지만 추출된 카드가 없습니다.")
    starts = set()
    formats = set()
    for item in items:
        title = getattr(item, "title", None) or item.heading
        offset = source_offset(raw_text, item.source_text, title)
        if offset is None:
            continue  # order_from_source reports unlocatable items.
        start = raw_text.rfind("\n", 0, offset) + 1
        if start in starts:
            raise ValueError("여러 카드가 같은 원문 항목을 참조합니다.")
        starts.add(start)
        for heading in headings:
            if heading.start() == start:
                formats.add((heading["indent"], re.sub(r"\d+|[①-⑳]", "", heading["marker"])))
    # shortcut: 같은 들여쓰기·번호 형식의 독립 제목을 대조한다. 본문 단계도 같은 형식이면 구획 정보가 필요하다.
    missing = [heading["title"] for heading in headings
               if (heading["indent"], re.sub(r"\d+|[①-⑳]", "", heading["marker"])) in formats and heading.start() not in starts]
    if missing:
        raise ValueError(f"번호로 구분된 항목이 누락되거나 합쳐졌습니다: {', '.join(missing)}")


def source_offset(raw_text, source_text, heading):
    """Return an unambiguous source offset, allowing whitespace differences only."""
    for candidate in (source_text, heading):
        if not candidate or not candidate.strip():
            continue
        pattern = r"\s+".join(re.escape(word) for word in candidate.split())
        matches = list(re.finditer(pattern, raw_text))
        if len(matches) == 1:
            return matches[0].start()
    return None


def order_from_source(raw_text, items, title_field):
    located = []
    for item in items:
        title = getattr(item, title_field)
        offset = source_offset(raw_text, item.source_text, title)
        if offset is None:
            raise ValueError(f"원문에서 항목 위치를 유일하게 확인할 수 없습니다: {title}")
        located.append((offset, item))
    if len({offset for offset, _ in located}) != len(located):
        raise ValueError("여러 항목이 같은 원문 위치를 참조합니다.")
    return [item for _, item in sorted(located, key=lambda pair: pair[0])]
