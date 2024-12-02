from fastapi import HTTPException
from typing import Any, Optional

class KKDataDException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict[str, str]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class QuotaExceededException(KKDataDException):
    def __init__(self) -> None:
        super().__init__(
            status_code=429,
            detail="API quota exceeded"
        )

class InvalidAPIKeyException(KKDataDException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            detail="Invalid API key"
        )

class DatabaseConnectionError(KKDataDException):
    def __init__(self) -> None:
        super().__init__(
            status_code=503,
            detail="Database connection error"
        ) 