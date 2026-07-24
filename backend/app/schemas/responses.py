from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    studentQuestion: str
    questionAnswer: str
    errorType: str
    correctParts: List[str]
    firstError: str
    correctSolution: List[str]
    comparison: List[Dict[str, Any]]
    reviewContent: List[str]
    caution: str


class AnalysisResponse(BaseModel):
    success: bool = True
    analysisId: str
    analysis: AnalysisResult
    meta: Dict[str, Any]


class ErrorDetail(BaseModel):
    errorCode: str
    message: str
    retryable: bool
    details: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
