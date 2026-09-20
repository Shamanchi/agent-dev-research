"""Unit-тесты поиска и брифа: без сети, детерминированы."""

import pytest

from app.services.corpus import all_docs
from app.services.research import build_brief, extract_snippet, search_docs


def test_search_ranks_adr_first() -> None:
    results = search_docs("caching redis", max_docs=3)
    assert [doc.title for doc in results] == [
        "Redis caching ADR",
        "Changelog 0.3.0",
        "Issue #42: slow queries",
    ]
    assert results[0].score == 6.0
    assert results[0].kind == "adr"


def test_empty_query_rejected() -> None:
    with pytest.raises(ValueError):
        search_docs("   ")


def test_snippet_extraction() -> None:
    adr = next(doc for doc in all_docs() if doc.title == "Redis caching ADR")
    snippet = extract_snippet(adr)
    assert snippet is not None
    assert snippet.language == "python"
    assert "cache.get(key)" in snippet.code
    changelog = next(doc for doc in all_docs() if doc.title == "Changelog 0.3.0")
    assert extract_snippet(changelog) is None


def test_brief_shape() -> None:
    brief = build_brief("caching redis", max_docs=2)
    assert len(brief.docs) == 2
    assert len(brief.key_points) == 2
    assert "[1]" in brief.key_points[0]
    assert len(brief.snippets) == 1
    assert "## Snippets" in brief.brief_md
    assert "## Read next" in brief.brief_md


def test_brief_no_match() -> None:
    brief = build_brief("quantum knitting", max_docs=3)
    assert brief.docs == []
    assert "No docs matched" in brief.brief_md
