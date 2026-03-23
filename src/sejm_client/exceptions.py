class SejmApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(SejmApiError):
    pass


class RateLimitError(SejmApiError):
    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
