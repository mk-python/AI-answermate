import json
import os
from typing import Any, Dict, Optional

from openai import OpenAI
from pydantic import ValidationError

from ..config import Config
from ..schemas.responses import AnalysisResult


class AIService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.client = OpenAI(api_key=api_key or Config.OPENAI_API_KEY)
        self.model = model or Config.OPENAI_MODEL

    def analyze(self, prompt: str, image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        if not getattr(self.client, "api_key", None):
            return {
                "studentQuestion": "",
                "questionAnswer": "입력된 정보를 바탕으로 오답을 분석했습니다.",
                "errorType": "정보 부족",
                "correctParts": ["문제의 핵심 개념을 확인하세요."],
                "firstError": "처음 틀린 부분을 확인해 주세요.",
                "correctSolution": ["문제 조건을 다시 확인하세요.", "풀이 순서를 점검하세요."],
                "comparison": [
                    {
                        "step": 1,
                        "studentStep": "학생 답안",
                        "correctStep": "정답 기준 풀이",
                        "status": "부분적으로 맞음",
                        "questionRelated": True,
                    }
                ],
                "reviewContent": ["개념을 다시 정리해 보세요."],
                "caution": "정답과 풀이 순서를 다시 검토하세요.",
            }

        try:
            messages = [
                {"role": "system", "content": "당신은 교육용 오답 분석을 수행합니다."},
                {"role": "user", "content": prompt},
            ]
            if image_bytes:
                messages[-1]["content"] = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_bytes.decode('latin1')}"}}]

            response = self.client.responses.create(
                model=self.model,
                input=messages,
            )
            content = getattr(response, "output_text", None)
            if not content:
                content = ""
                for item in getattr(response, "output", []) or []:
                    if getattr(item, "type", None) == "message":
                        for message_part in getattr(item, "content", []) or []:
                            if getattr(message_part, "type", None) == "output_text":
                                content += getattr(message_part, "text", "")
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as exc:
                raise ValueError("INVALID_AI_RESPONSE") from exc

            AnalysisResult(**parsed)
            return parsed
        except ValidationError as exc:
            raise ValueError("INVALID_AI_RESPONSE") from exc
        except Exception as exc:
            if "401" in str(exc) or "authentication" in str(exc).lower():
                raise PermissionError("AI_AUTH_ERROR") from exc
            if "429" in str(exc) or "rate limit" in str(exc).lower():
                raise TimeoutError("AI_RATE_LIMIT") from exc
            if "connection" in str(exc).lower() or "timeout" in str(exc).lower():
                raise ConnectionError("AI_CONNECTION_ERROR") from exc
            raise RuntimeError("SERVER_ERROR") from exc
