from __future__ import annotations

from collections.abc import Callable, Generator
from datetime import date, timedelta
from typing import Any, TypeVar

import httpx

T = TypeVar("T")

_SEJM_API_BASE = "https://api.sejm.gov.pl/sejm"


def current_term() -> int:
    resp = httpx.get(f"{_SEJM_API_BASE}/term", headers={"Accept": "application/json"}, timeout=15)
    resp.raise_for_status()
    terms = resp.json()
    current = [t for t in terms if t.get("current") is True]
    if current:
        return max(current, key=lambda t: t["num"])["num"]

    # Fallback for older payloads that expose the end date as `to`/`till`.
    today = date.today().isoformat()
    active = [
        t for t in terms
        if not t.get("to", t.get("till")) or t.get("to", t.get("till")) >= today
    ]
    if active:
        return max(active, key=lambda t: t["num"])["num"]
    return terms[-1]["num"]


def date_range_last_n_days(days: int) -> tuple[date, date]:
    today = date.today()
    return today - timedelta(days=days), today


def paginate(
    fn: Callable[..., list[T]],
    *,
    page_size: int = 50,
    **kwargs: Any,
) -> Generator[T, None, None]:
    offset = 0
    while True:
        page = fn(limit=page_size, offset=offset, **kwargs)
        yield from page
        if len(page) < page_size:
            break
        offset += page_size
