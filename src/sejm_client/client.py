from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .http import HttpClient
from .models.bills import Bill
from .models.common import ApplicantType, BillStatus, BillType, EliPublisher
from .models.mps import MP, Club
from .models.prints import Print
from .models.processes import Process
from .models.votings import Voting

_SEJM_BASE = "https://api.sejm.gov.pl/sejm"
_PRINT_PDF_BASE = "https://orka.sejm.gov.pl/Druki10ka.nsf/0"


class Proceeding:
    """Minimal model for a sitting/proceeding."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def number(self) -> int:
        return self._data.get("number", 0)

    @property
    def dates(self) -> list[str]:
        return self._data.get("dates", [])

    def model_dump(self) -> dict[str, Any]:
        return self._data


class SejmClient:
    """Typed client for the Polish Sejm API (api.sejm.gov.pl/sejm)."""

    def __init__(self, term: int | None = None, timeout: float = 30.0) -> None:
        self._http = HttpClient(_SEJM_BASE, timeout=timeout)
        self._term: int | None = term

    @property
    def term(self) -> int:
        if self._term is None:
            from .utils import current_term
            self._term = current_term()
        return self._term

    # ------------------------------------------------------------------ #
    # Bills
    # ------------------------------------------------------------------ #

    def get_bills(
        self,
        status: BillStatus | None = None,
        bill_type: BillType | None = None,
        applicant_type: ApplicantType | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        title: str | None = None,
        eu_related: bool | None = None,
        public_consultation: bool | None = None,
        sort: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Bill]:
        params: dict[str, Any] = {
            "status": status.value if status else None,
            "submissionType": bill_type.value if bill_type else None,
            "applicantType": applicant_type.value if applicant_type else None,
            "dateOfReceiptFrom": date_from.isoformat() if date_from else None,
            "dateOfReceiptTo": date_to.isoformat() if date_to else None,
            "title": title,
            "euRelated": str(eu_related).lower() if eu_related is not None else None,
            "publicConsultation": (
                str(public_consultation).lower()
                if public_consultation is not None
                else None
            ),
            "sort": sort,
            "limit": limit,
            "offset": offset,
        }
        data = self._http.get(f"/term{self.term}/bills", params)
        if isinstance(data, dict):
            items = data.get("items", data)
        else:
            items = data
        return [Bill.model_validate(item) for item in items]

    def get_recent_bills(self, days: int = 30) -> list[Bill]:
        from .utils import date_range_last_n_days
        date_from, date_to = date_range_last_n_days(days)
        return self.get_bills(date_from=date_from, date_to=date_to)

    def get_active_bills(self) -> list[Bill]:
        return self.get_bills(status=BillStatus.ACTIVE)

    def get_passed_bills(self) -> list[Bill]:
        return self.get_bills(status=BillStatus.ADOPTED)

    def get_bill(self, print_num: str) -> Bill:
        data = self._http.get(f"/term{self.term}/bills/{print_num}")
        return Bill.model_validate(data)

    # ------------------------------------------------------------------ #
    # Processes
    # ------------------------------------------------------------------ #

    def get_processes(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        sort: str | None = None,
        limit: int = 50,
        offset: int = 0,
        publisher: EliPublisher | None = None,
    ) -> list[Process]:
        params: dict[str, Any] = {
            "dateFrom": date_from.isoformat() if date_from else None,
            "dateTo": date_to.isoformat() if date_to else None,
            "sort": sort,
            "limit": limit,
            "offset": offset,
        }
        data = self._http.get(f"/term{self.term}/processes", params)
        if isinstance(data, dict):
            items = data.get("items", data)
        else:
            items = data
        processes = [Process.model_validate(item) for item in items]
        if publisher is not None:
            prefix = publisher.value + "/"
            processes = [p for p in processes if p.eli and p.eli.startswith(prefix)]
        return processes

    def get_process(self, print_num: str) -> Process:
        data = self._http.get(f"/term{self.term}/processes/{print_num}")
        return Process.model_validate(data)

    def get_bills_by_stage(self, stage_name: str) -> list[Process]:
        processes = self.get_processes(limit=200)
        return [
            p for p in processes
            if any(s.stage_name == stage_name for s in p.stages)
        ]

    def get_processes_since(self, since: date | datetime) -> list[Process]:
        since_date = since if isinstance(since, date) else since.date()
        return self.get_processes(date_from=since_date)

    # ------------------------------------------------------------------ #
    # Votings
    # ------------------------------------------------------------------ #

    def get_votings(self, sitting: int, date: date | None = None) -> list[Voting]:
        params: dict[str, Any] = {"date": date.isoformat() if date else None}
        data = self._http.get(f"/term{self.term}/votings/{sitting}", params)
        if isinstance(data, list):
            return [Voting.model_validate(item) for item in data]
        return [Voting.model_validate(item) for item in data.get("items", [])]

    def get_voting(self, sitting: int, voting_number: int) -> Voting:
        data = self._http.get(f"/term{self.term}/votings/{sitting}/{voting_number}")
        return Voting.model_validate(data)

    def get_voting_detail(self, sitting: int, voting_number: int) -> Voting:
        """Returns voting with individual MP votes populated."""
        return self.get_voting(sitting, voting_number)

    def get_votings_for_bill(self, print_num: str) -> list[Voting]:
        """Best-effort: finds votings whose title references the given print number."""
        self.get_process(print_num)
        results: list[Voting] = []
        for proceeding in self.get_proceedings():
            sitting_num = proceeding.number
            try:
                votings = self.get_votings(sitting_num)
            except Exception:
                continue
            for v in votings:
                if print_num in (v.title or "") or print_num in (v.topic or ""):
                    results.append(v)
        return results

    # ------------------------------------------------------------------ #
    # Prints
    # ------------------------------------------------------------------ #

    def get_prints(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Print]:
        params: dict[str, Any] = {
            "dateFrom": date_from.isoformat() if date_from else None,
            "dateTo": date_to.isoformat() if date_to else None,
            "limit": limit,
            "offset": offset,
        }
        data = self._http.get(f"/term{self.term}/prints", params)
        if isinstance(data, dict):
            items = data.get("items", data)
        else:
            items = data
        # The upstream prints endpoint currently ignores `limit` and `offset`.
        if isinstance(items, list):
            items = items[offset:offset + limit]
        return [Print.model_validate(item) for item in items]

    def get_print(self, print_num: str) -> Print:
        data = self._http.get(f"/term{self.term}/prints/{print_num}")
        return Print.model_validate(data)

    def get_print_pdf_url(self, print_num: str) -> str:
        return f"{_SEJM_BASE}/term{self.term}/prints/{print_num}/pdf"

    # ------------------------------------------------------------------ #
    # MPs & Clubs
    # ------------------------------------------------------------------ #

    def get_mps(self, active_only: bool = False) -> list[MP]:
        data = self._http.get(f"/term{self.term}/MP")
        mps = [MP.model_validate(item) for item in data]
        if active_only:
            mps = [mp for mp in mps if mp.active]
        return mps

    def get_mp(self, mp_id: int) -> MP:
        data = self._http.get(f"/term{self.term}/MP/{mp_id}")
        return MP.model_validate(data)

    def get_clubs(self) -> list[Club]:
        data = self._http.get(f"/term{self.term}/clubs")
        return [Club.model_validate(item) for item in data]

    def get_club(self, club_id: str) -> Club:
        data = self._http.get(f"/term{self.term}/clubs/{club_id}")
        return Club.model_validate(data)

    # ------------------------------------------------------------------ #
    # Proceedings
    # ------------------------------------------------------------------ #

    def get_proceedings(self) -> list[Proceeding]:
        data = self._http.get(f"/term{self.term}/proceedings")
        return [Proceeding(item) for item in data]

    def get_proceeding(self, sitting: int) -> Proceeding:
        data = self._http.get(f"/term{self.term}/proceedings/{sitting}")
        return Proceeding(data)

    # ------------------------------------------------------------------ #
    # Context manager support
    # ------------------------------------------------------------------ #

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SejmClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
