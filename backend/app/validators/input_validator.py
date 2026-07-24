import json
from typing import Any, Dict, Optional

from ..errors.exceptions import ApiErrorException
from ..schemas.requests import AnalysisRequest, ReanalysisRequest


class InputValidator:
    @staticmethod
    def validate_analysis_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
        if not form_data.get("subject"):
            raise ApiErrorException("MISSING_FIELD", "과목을 입력해주세요.", details={"field": "subject"})

        if form_data.get("subject") not in {"국어", "수학", "영어"}:
            raise ApiErrorException("INVALID_SUBJECT", "지원하지 않는 과목입니다.", details={"field": "subject"})

        if form_data.get("questionType") and form_data.get("questionType") not in {"객관식", "단답형", "서술형"}:
            raise ApiErrorException("INVALID_QUESTION_TYPE", "지원하지 않는 문제 유형입니다.", details={"field": "questionType"})

        if not form_data.get("questionText") and not form_data.get("questionImage"):
            raise ApiErrorException("MISSING_FIELD", "문제 텍스트 또는 문제 이미지를 입력해주세요.", details={"field": "questionText"})

        if not form_data.get("correctAnswer"):
            raise ApiErrorException("MISSING_FIELD", "정답을 입력해주세요.", details={"field": "correctAnswer"})

        if not form_data.get("studentAnswer"):
            raise ApiErrorException("MISSING_FIELD", "학생 답안을 입력해주세요.", details={"field": "studentAnswer"})

        for field_name, max_length in {
            "unit": 100,
            "questionText": 8000,
            "correctAnswer": 3000,
            "studentAnswer": 3000,
            "studentSolution": 6000,
            "studentQuestion": 1500,
        }.items():
            value = form_data.get(field_name)
            if value is not None and len(value.strip()) > max_length:
                raise ApiErrorException("TEXT_TOO_LONG", f"{field_name} 길이가 너무 깁니다.", details={"field": field_name})

        try:
            AnalysisRequest(
                subject=form_data.get("subject"),
                unit=form_data.get("unit"),
                questionType=form_data.get("questionType"),
                questionText=form_data.get("questionText"),
                correctAnswer=form_data.get("correctAnswer"),
                studentAnswer=form_data.get("studentAnswer"),
                studentSolution=form_data.get("studentSolution"),
                studentQuestion=form_data.get("studentQuestion"),
            )
        except Exception as exc:
            raise ApiErrorException("MISSING_FIELD", str(exc), details={"field": "request"}) from exc

        return form_data

    @staticmethod
    def validate_reanalysis_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
        if not form_data.get("reanalysisType"):
            raise ApiErrorException("MISSING_FIELD", "재분석 유형을 입력해주세요.", details={"field": "reanalysisType"})

        if form_data.get("reanalysisType") not in {"easy", "detailed", "alternative", "reconsider", "newQuestion"}:
            raise ApiErrorException("INVALID_REANALYSIS_TYPE", "지원하지 않는 재분석 유형입니다.", details={"field": "reanalysisType"})

        previous_analysis_raw = form_data.get("previousAnalysis")
        if not previous_analysis_raw:
            raise ApiErrorException("MISSING_FIELD", "previousAnalysis를 입력해주세요.", details={"field": "previousAnalysis"})

        try:
            previous_analysis = json.loads(previous_analysis_raw) if isinstance(previous_analysis_raw, str) else previous_analysis_raw
        except json.JSONDecodeError as exc:
            raise ApiErrorException("INVALID_PREVIOUS_ANALYSIS", "previousAnalysis JSON 형식이 올바르지 않습니다.", details={"field": "previousAnalysis"}) from exc

        if not isinstance(previous_analysis, dict):
            raise ApiErrorException("INVALID_PREVIOUS_ANALYSIS", "previousAnalysis는 객체 형식이어야 합니다.", details={"field": "previousAnalysis"})

        try:
            ReanalysisRequest(
                reanalysisType=form_data.get("reanalysisType"),
                previousAnalysis=previous_analysis,
                newStudentQuestion=form_data.get("newStudentQuestion"),
            )
        except Exception as exc:
            raise ApiErrorException("INVALID_PREVIOUS_ANALYSIS", str(exc), details={"field": "previousAnalysis"}) from exc

        form_data["previousAnalysis"] = previous_analysis
        return form_data
