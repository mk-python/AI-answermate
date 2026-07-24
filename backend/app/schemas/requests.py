from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    subject: str
    unit: Optional[str] = None
    questionType: Optional[str] = None
    questionText: Optional[str] = None
    correctAnswer: Optional[str] = None
    studentAnswer: Optional[str] = None
    studentSolution: Optional[str] = None
    studentQuestion: Optional[str] = None

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        allowed = {"국어", "수학", "영어"}
        if value not in allowed:
            raise ValueError("subject must be one of 국어, 수학, 영어")
        return value.strip()

    @field_validator("questionType")
    @classmethod
    def validate_question_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        allowed = {"객관식", "단답형", "서술형"}
        if value not in allowed:
            raise ValueError("questionType must be one of 객관식, 단답형, 서술형")
        return value.strip()

    @field_validator("unit", "questionText", "correctAnswer", "studentAnswer", "studentSolution", "studentQuestion")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("value must be a string")
        return value.strip()


class ReanalysisRequest(BaseModel):
    reanalysisType: str
    previousAnalysis: dict
    newStudentQuestion: Optional[str] = None

    @field_validator("reanalysisType")
    @classmethod
    def validate_reanalysis_type(cls, value: str) -> str:
        allowed = {"easy", "detailed", "alternative", "reconsider", "newQuestion"}
        if value not in allowed:
            raise ValueError("reanalysisType is invalid")
        return value.strip()
