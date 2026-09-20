"""Поиск по корпусу, сниппеты и бриф."""

from __future__ import annotations

import re

from pydantic import BaseModel

from app.services.corpus import Doc, all_docs

_WORD_RE = re.compile(r"[a-zA-Z]+")
_CODE_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)


class ScoredDoc(BaseModel):
    n: int
    title: str
    kind: str
    score: float


class Snippet(BaseModel):
    n: int
    language: str
    code: str


class DevBrief(BaseModel):
    query: str
    docs: list[ScoredDoc]
    key_points: list[str]
    snippets: list[Snippet]
    brief_md: str


def _terms(query: str) -> set[str]:
    return set(_WORD_RE.findall(query.lower()))


def score_doc(doc: Doc, terms: set[str]) -> float:
    """Скор: 2 балла за тег + 1 за слово из заголовка. Детерминировано."""
    tag_hits = len(terms & {tag.lower() for tag in doc.tags})
    title_hits = len(terms & set(_WORD_RE.findall(doc.title.lower())))
    return round(tag_hits * 2.0 + title_hits * 1.0, 2)


def search_docs(query: str, max_docs: int = 3, min_score: float = 1.0) -> list[ScoredDoc]:
    """Найти топ документов по запросу."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    terms = _terms(query)
    scored = [
        (score_doc(doc, terms), doc)
        for doc in all_docs()
        if score_doc(doc, terms) >= min_score
    ]
    scored.sort(key=lambda pair: (-pair[0], pair[1].title))
    return [
        ScoredDoc(n=n, title=doc.title, kind=doc.kind, score=score)
        for n, (score, doc) in enumerate(scored[: max(max_docs, 0)], start=1)
    ]


def extract_snippet(doc: Doc) -> Snippet | None:
    """Вытащить первый ```блок кода из документа."""
    match = _CODE_RE.search(doc.body)
    if not match:
        return None
    return Snippet(n=0, language=match.group(1) or "text", code=match.group(2).strip())


def build_brief(query: str, max_docs: int = 3, min_score: float = 1.0) -> DevBrief:
    """Собрать бриф: тезисы + сниппеты + очередь чтения."""
    docs = search_docs(query, max_docs, min_score)
    by_title = {doc.title: doc for doc in all_docs()}
    key_points: list[str] = []
    snippets: list[Snippet] = []
    for scored in docs:
        doc = by_title[scored.title]
        first = doc.body.split(". ")[0].rstrip(".")
        key_points.append(f"{doc.title}: {first} [{scored.n}]")
        snippet = extract_snippet(doc)
        if snippet is not None:
            snippets.append(Snippet(n=scored.n, language=snippet.language, code=snippet.code))
    lines = [f"# Dev brief: {query.strip()}", ""]
    if not docs:
        lines.append("No docs matched the query.")
        return DevBrief(query=query.strip(), docs=[], key_points=[], snippets=[], brief_md="\n".join(lines) + "\n")
    lines.append("## Key points")
    lines.extend(f"- {point}" for point in key_points)
    lines.append("")
    if snippets:
        lines.append("## Snippets")
        for snippet in snippets:
            lines.append(f"[{snippet.n}] ```{snippet.language}")
            lines.append(snippet.code)
            lines.append("```")
        lines.append("")
    lines.append("## Read next")
    lines.extend(f"[{doc.n}] {doc.title} ({doc.kind})" for doc in docs)
    return DevBrief(
        query=query.strip(),
        docs=docs,
        key_points=key_points,
        snippets=snippets,
        brief_md="\n".join(lines) + "\n",
    )
