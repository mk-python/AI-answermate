import json
import uuid
from typing import Any, Dict, Optional

from ..errors.exceptions import ApiErrorException
from ..validators.file_validator import FileValidator
from ..validators.input_validator import InputValidator
from .ai_service import AIService
from .image_service import ImageService
from .prompt_service import PromptService


class AnalysisService:
    def __init__(self) -> None:
        self.ai_service = AIService()

    def analyze(self, form_data: Dict[str, Any], files: Dict[str, Any], app_config: Dict[str, Any]) -> Dict[str, Any]:
        InputValidator.validate_analysis_form(form_data)

        question_image = files.get("questionImage")
        solution_image = files.get("solutionImage")

        question_image_bytes = FileValidator.validate_file(question_image, "questionImage", app_config["MAX_IMAGE_SIZE"], app_config["MAX_IMAGE_SIDE"])
        solution_image_bytes = FileValidator.validate_file(solution_image, "solutionImage", app_config["MAX_IMAGE_SIZE"], app_config["MAX_IMAGE_SIDE"])

        if question_image_bytes is not None:
            question_image_bytes = ImageService.prepare_image(question_image_bytes, app_config["MAX_IMAGE_SIDE"])
        if solution_image_bytes is not None:
            solution_image_bytes = ImageService.prepare_image(solution_image_bytes, app_config["MAX_IMAGE_SIDE"])

        payload = {
            "subject": form_data.get("subject"),
            "unit": form_data.get("unit"),
            "questionType": form_data.get("questionType"),
            "questionText": form_data.get("questionText"),
            "correctAnswer": form_data.get("correctAnswer"),
            "studentAnswer": form_data.get("studentAnswer"),
            "studentSolution": form_data.get("studentSolution"),
            "studentQuestion": form_data.get("studentQuestion"),
        }
        prompt = PromptService.build_analysis_prompt(payload)

        try:
            ai_result = self.ai_service.analyze(prompt, question_image_bytes)
        except PermissionError as exc:
            if self.ai_service.client.api_key:
                raise ApiErrorException("AI_AUTH_ERROR", "AI 인증에 실패했습니다.", retryable=False) from exc
            raise ApiErrorException("AI_AUTH_ERROR", "AI 인증에 실패했습니다.", retryable=False) from exc
        except TimeoutError as exc:
            raise ApiErrorException("AI_RATE_LIMIT", "AI 요청 한도에 도달했습니다.", retryable=True) from exc
        except ConnectionError as exc:
            raise ApiErrorException("AI_CONNECTION_ERROR", "AI 서버 연결에 실패했습니다.", retryable=True) from exc
        except ValueError as exc:
            raise ApiErrorException("INVALID_AI_RESPONSE", "AI 응답 형식이 올바르지 않습니다.", retryable=False) from exc
        except RuntimeError as exc:
            raise ApiErrorException("SERVER_ERROR", "서버 내부 오류가 발생했습니다.", retryable=True) from exc

        response = {
            "success": True,
            "analysisId": str(uuid.uuid4()),
            "analysis": ai_result,
            "meta": {"subject": form_data.get("subject"), "reanalyzed": False},
        }
        return response

    def reanalyze(self, form_data: Dict[str, Any], files: Dict[str, Any], app_config: Dict[str, Any]) -> Dict[str, Any]:
        InputValidator.validate_reanalysis_form(form_data)

        payload = {
            "subject": form_data.get("subject"),
            "unit": form_data.get("unit"),
            "questionType": form_data.get("questionType"),
            "questionText": form_data.get("questionText"),
            "correctAnswer": form_data.get("correctAnswer"),
            "studentAnswer": form_data.get("studentAnswer"),
            "studentSolution": form_data.get("studentSolution"),
            "studentQuestion": form_data.get("studentQuestion"),
            "previousAnalysis": form_data.get("previousAnalysis"),
            "newStudentQuestion": form_data.get("newStudentQuestion"),
        }
        prompt = PromptService.build_reanalysis_prompt(payload, form_data.get("reanalysisType"))

        try:
            ai_result = self.ai_service.analyze(prompt, None)
        except PermissionError as exc:
            raise ApiErrorException("AI_AUTH_ERROR", "AI 인증에 실패했습니다.", retryable=False) from exc
        except TimeoutError as exc:
            raise ApiErrorException("AI_RATE_LIMIT", "AI 요청 한도에 도달했습니다.", retryable=True) from exc
        except ConnectionError as exc:
            raise ApiErrorException("AI_CONNECTION_ERROR", "AI 서버 연결에 실패했습니다.", retryable=True) from exc
        except ValueError as exc:
            raise ApiErrorException("INVALID_AI_RESPONSE", "AI 응답 형식이 올바르지 않습니다.", retryable=False) from exc
        except RuntimeError as exc:
            raise ApiErrorException("SERVER_ERROR", "서버 내부 오류가 발생했습니다.", retryable=True) from exc

        response = {
            "success": True,
            "analysisId": str(uuid.uuid4()),
            "analysis": ai_result,
            "meta": {"subject": form_data.get("subject"), "reanalyzed": True, "reanalysisType": form_data.get("reanalysisType")},
        }
        return response
