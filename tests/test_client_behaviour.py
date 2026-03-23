from __future__ import annotations

from sejm_client.client import SejmClient
from sejm_client.eli_client import EliClient


class StubHttpClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def get(self, path, params=None):
        self.calls.append((path, params))
        return self.responses[path]

    def close(self):
        return None


def test_get_prints_applies_client_side_pagination_when_api_returns_full_list():
    client = SejmClient(term=10)
    client._http = StubHttpClient(
        {
            "/term10/prints": [
                {"number": "1", "term": 10, "title": "first"},
                {"number": "2", "term": 10, "title": "second"},
                {"number": "3", "term": 10, "title": "third"},
            ]
        }
    )

    prints = client.get_prints(limit=1, offset=1)

    assert [item.num for item in prints] == ["2"]


def test_get_acts_uses_items_payload_and_client_side_slice_when_offset_is_ignored():
    client = EliClient()
    client._http = StubHttpClient(
        {
            "/acts/DU/2024": {
                "count": 3,
                "offset": 0,
                "totalCount": 3,
                "items": [
                    {
                        "ELI": "DU/2024/3",
                        "address": "WDU20240000003",
                        "displayAddress": "Dz.U. 2024 poz. 3",
                        "publisher": "DU",
                        "year": 2024,
                        "pos": 3,
                        "title": "third",
                        "type": "Ustawa",
                        "status": "bez statusu",
                    },
                    {
                        "ELI": "DU/2024/2",
                        "address": "WDU20240000002",
                        "displayAddress": "Dz.U. 2024 poz. 2",
                        "publisher": "DU",
                        "year": 2024,
                        "pos": 2,
                        "title": "second",
                        "type": "Ustawa",
                        "status": "bez statusu",
                    },
                    {
                        "ELI": "DU/2024/1",
                        "address": "WDU20240000001",
                        "displayAddress": "Dz.U. 2024 poz. 1",
                        "publisher": "DU",
                        "year": 2024,
                        "pos": 1,
                        "title": "first",
                        "type": "Ustawa",
                        "status": "bez statusu",
                    },
                ],
            }
        }
    )

    acts = client.get_acts(publisher="DU", year=2024, limit=1, offset=1)

    assert [item.eli for item in acts] == ["DU/2024/2"]


def test_get_acts_without_year_walks_publisher_years_newest_first():
    client = EliClient()
    client._http = StubHttpClient(
        {
            "/acts/DU": {"years": [2023, 2024]},
            "/acts/DU/2024": {
                "count": 2,
                "offset": 0,
                "totalCount": 2,
                "items": [
                    {
                        "ELI": "DU/2024/2",
                        "address": "WDU20240000002",
                        "displayAddress": "Dz.U. 2024 poz. 2",
                        "publisher": "DU",
                        "year": 2024,
                        "pos": 2,
                        "title": "2024 second",
                        "type": "Ustawa",
                        "status": "bez statusu",
                    },
                    {
                        "ELI": "DU/2024/1",
                        "address": "WDU20240000001",
                        "displayAddress": "Dz.U. 2024 poz. 1",
                        "publisher": "DU",
                        "year": 2024,
                        "pos": 1,
                        "title": "2024 first",
                        "type": "Ustawa",
                        "status": "bez statusu",
                    },
                ],
            },
            "/acts/DU/2023": {
                "count": 1,
                "offset": 0,
                "totalCount": 1,
                "items": [
                    {
                        "ELI": "DU/2023/1",
                        "address": "WDU20230000001",
                        "displayAddress": "Dz.U. 2023 poz. 1",
                        "publisher": "DU",
                        "year": 2023,
                        "pos": 1,
                        "title": "2023 first",
                        "type": "Ustawa",
                        "status": "bez statusu",
                    }
                ],
            },
        }
    )

    acts = client.get_acts(publisher="DU", limit=2)

    assert [item.eli for item in acts] == ["DU/2024/2", "DU/2024/1"]
