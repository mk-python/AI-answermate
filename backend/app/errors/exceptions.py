class ApiErrorException(Exception):
    def __init__(self, error_code: str, message: str, retryable: bool = False, details: dict | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.retryable = retryable
        self.details = details or {}
