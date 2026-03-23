from __future__ import annotations

from datetime import date
from typing import Any

from .http import HttpClient
from .models.acts import Act, Publisher
from .models.common import ActStatus

_ELI_BASE = "https://api.sejm.gov.pl/eli"


class EliClient:
    """Typed client for the Polish ELI API (api.sejm.gov.pl/eli)."""

    def __init__(self, timeout: float = 30.0) -> None:
        self._http = HttpClient(_ELI_BASE, timeout=timeout)

    def get_acts(
        self,
        publisher: str = "DU",
        year: int | None = None,
        status: ActStatus | None = None,
        act_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        title: str | None = None,
        sort: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Act]:
        params: dict[str, Any] = {
            "status": status.value if status else None,
            "type": act_type,
            "title": title,
            "announcementDateFrom": date_from.isoformat() if date_from else None,
            "announcementDateTo": date_to.isoformat() if date_to else None,
            "sort": sort,
            "limit": limit,
            "offset": offset,
        }
        if year is not None:
            data = self._http.get(f"/acts/{publisher}/{year}", params)
            items = self._extract_items(data)
            if self._pagination_ignored(data, items, limit, offset):
                items = items[offset:offset + limit]
            return [Act.model_validate(item) for item in items]

        publisher_data = self._http.get(f"/acts/{publisher}")
        years = publisher_data.get("years") if isinstance(publisher_data, dict) else None
        if not isinstance(years, list):
            raise ValueError(f"Publisher listing for {publisher!r} does not include yearly act indexes")

        page_params = {k: v for k, v in params.items() if k not in {"limit", "offset"}}
        remaining_offset = offset
        collected: list[dict[str, Any]] = []

        # The API only exposes act listings per year, so synthesize publisher-wide
        # iteration starting from the newest year.
        for indexed_year in reversed(years):
            year_data = self._http.get(f"/acts/{publisher}/{indexed_year}", page_params)
            year_items = self._extract_items(year_data)
            if remaining_offset >= len(year_items):
                remaining_offset -= len(year_items)
                continue
            year_items = year_items[remaining_offset:]
            remaining_offset = 0
            collected.extend(year_items)
            if len(collected) >= limit:
                break

        return [Act.model_validate(item) for item in collected[:limit]]

    def get_recent_acts(self, days: int = 30, publisher: str = "DU") -> list[Act]:
        from .utils import date_range_last_n_days
        date_from, date_to = date_range_last_n_days(days)
        return self.get_acts(publisher=publisher, date_from=date_from, date_to=date_to)

    def get_act(self, publisher: str, year: int, position: int) -> Act:
        data = self._http.get(f"/acts/{publisher}/{year}/{position}")
        return Act.model_validate(data)

    def get_act_by_eli(self, eli: str) -> Act:
        # eli format: "DU/2024/179"
        parts = eli.split("/")
        if len(parts) != 3:
            raise ValueError(f"Invalid ELI format: {eli!r}. Expected 'PUBLISHER/YEAR/POS'")
        publisher, year, pos = parts
        return self.get_act(publisher, int(year), int(pos))

    def get_act_text_url(self, eli: str, fmt: str = "pdf") -> str:
        parts = eli.split("/")
        if len(parts) != 3:
            raise ValueError(f"Invalid ELI format: {eli!r}. Expected 'PUBLISHER/YEAR/POS'")
        publisher, year, pos = parts
        ext = "PDF" if fmt.lower() == "pdf" else "HTML"
        return f"{_ELI_BASE}/acts/{publisher}/{year}/{pos}/text/{ext}"

    def get_publishers(self) -> list[Publisher]:
        data = self._http.get("/acts")
        if isinstance(data, list):
            return [Publisher.model_validate(item) for item in data]
        items = data.get("items", [])
        return [Publisher.model_validate(item) for item in items]

    @staticmethod
    def _extract_items(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]
        raise ValueError("Expected a list response or an object with an 'items' list")

    @staticmethod
    def _pagination_ignored(data: Any, items: list[dict[str, Any]], limit: int, offset: int) -> bool:
        if not isinstance(data, dict):
            return False
        response_offset = data.get("offset")
        if isinstance(response_offset, int) and response_offset != offset:
            return True
        return len(items) > limit

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "EliClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
