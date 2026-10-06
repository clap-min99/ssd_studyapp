"""Locate extracted items in the email rather than trusting model array order."""

import re


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
