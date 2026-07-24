from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ApiError(BaseModel):
    errorCode: str
    message: str
    retryable: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)
