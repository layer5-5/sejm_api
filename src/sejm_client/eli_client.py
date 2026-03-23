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
        path = f"/acts/{publisher}/{year}" if year else f"/acts/{publisher}"
        data = self._http.get(path, params)
        items = data.get("items", data) if isinstance(data, dict) else data
        return [Act.model_validate(item) for item in items]

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

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "EliClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
