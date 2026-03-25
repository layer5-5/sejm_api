from __future__ import annotations

from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import NotFoundError, RateLimitError, SejmApiError


def _raise_for_status(response: httpx.Response) -> None:
    if response.status_code == 404:
        raise NotFoundError(f"Not found: {response.url}", status_code=404)
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        raise RateLimitError(
            "Rate limit exceeded",
            retry_after=float(retry_after) if retry_after else None,
        )
    if response.status_code >= 400:
        raise SejmApiError(
            f"HTTP {response.status_code}: {response.text[:200]}",
            status_code=response.status_code,
        )


class HttpClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        # Ensure trailing slash so httpx merges paths correctly
        if not base_url.endswith("/"):
            base_url += "/"
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        # Strip leading slash so httpx appends to base_url rather than replacing path
        clean_path = path.lstrip("/")
        filtered = {k: v for k, v in (params or {}).items() if v is not None}
        response = self._client.get(clean_path, params=filtered)
        _raise_for_status(response)
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
