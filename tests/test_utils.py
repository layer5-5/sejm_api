from __future__ import annotations

from sejm_client import utils


class StubResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_current_term_prefers_current_flag(monkeypatch):
    payload = [
        {"num": 9, "current": False, "to": "2023-11-12"},
        {"num": 10, "current": True},
    ]

    monkeypatch.setattr(
        utils.httpx,
        "get",
        lambda *args, **kwargs: StubResponse(payload),
        raising=False,
    )

    assert utils.current_term() == 10
