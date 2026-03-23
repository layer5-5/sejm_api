from __future__ import annotations

from collections.abc import Callable, Generator
from datetime import date, timedelta
from typing import Any, TypeVar

T = TypeVar("T")

_SEJM_API_BASE = "https://api.sejm.gov.pl/sejm"


def current_term() -> int:
    import httpx

    resp = httpx.get(f"{_SEJM_API_BASE}/term", headers={"Accept": "application/json"}, timeout=15)
    resp.raise_for_status()
    terms = resp.json()
    # Find current (active) term — no 'till' date or till > today
    today = date.today().isoformat()
    current = [t for t in terms if not t.get("till") or t["till"] >= today]
    if not current:
        return terms[-1]["num"]
    return max(current, key=lambda t: t["num"])["num"]


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
