"""Mock-корпус дев-документов: офлайн-фикстуры без сети."""

from __future__ import annotations

from pydantic import BaseModel


class Doc(BaseModel):
    title: str
    kind: str
    tags: list[str] = []
    body: str


_CORPUS: list[Doc] = [
    Doc(
        title="Redis caching ADR",
        kind="adr",
        tags=["caching", "redis", "architecture"],
        body=(
            "We chose cache-aside with Redis for session data. "
            "TTL is 3600 seconds for hot keys.\n"
            "```python\nvalue = cache.get(key)\nif value is None:\n    value = db.load(key)\n```"
        ),
    ),
    Doc(
        title="Deploy README",
        kind="readme",
        tags=["deploy", "docker", "ci"],
        body=(
            "Deploy with docker compose up --build. "
            "CI runs ruff, mypy and pytest on every push.\n"
            "```bash\ndocker compose up --build\n```"
        ),
    ),
    Doc(
        title="Changelog 0.3.0",
        kind="changelog",
        tags=["caching", "release"],
        body=(
            "Added Redis cache layer with 3600s TTL. "
            "Fixed stale reads on user profiles."
        ),
    ),
    Doc(
        title="Issue #42: slow queries",
        kind="issue",
        tags=["postgres", "performance", "caching"],
        body=(
            "List queries miss indexes on created_at. "
            "Add a composite index to fix the seq scan."
        ),
    ),
]


def all_docs() -> list[Doc]:
    return list(_CORPUS)
