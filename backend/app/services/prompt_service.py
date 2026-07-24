import json
from typing import Any, Dict

from ..prompts.common import build_common_instruction
from ..prompts.subjects import build_subject_instruction


class PromptService:
    @staticmethod
    def build_analysis_prompt(data: Dict[str, Any]) -> str:
        subject = data.get("subject", "")
        common_instruction = build_common_instruction(subject)
        subject_instruction = build_subject_instruction(subject)

        prompt = f"""
{common_instruction}
{subject_instruction}

다음 정보를 분석해 주세요.
과목: {subject}
단원: {data.get('unit', '')}
문제 유형: {data.get('questionType', '')}
문제 텍스트: {data.get('questionText', '')}
정답: {data.get('correctAnswer', '')}
학생 답안: {data.get('studentAnswer', '')}
학생 풀이: {data.get('studentSolution', '')}
학생 질문: {data.get('studentQuestion', '')}

반환 형식은 다음 JSON 구조여야 합니다.
{{
  "studentQuestion": "학생 질문",
  "questionAnswer": "질문에 대한 답변",
  "errorType": "대표 오답 유형",
  "correctParts": ["맞게 이해한 부분"],
  "firstError": "처음 틀린 부분",
  "correctSolution": ["올바른 풀이 1단계", "올바른 풀이 2단계"],
  "comparison": [
    {{
      "step": 1,
      "studentStep": "학생 풀이",
      "correctStep": "올바른 풀이",
      "status": "같음",
      "questionRelated": false
    }}
  ],
  "reviewContent": ["복습할 내용"],
  "caution": "주의사항"
}}
"""
        return prompt

    @staticmethod
    def build_reanalysis_prompt(data: Dict[str, Any], reanalysis_type: str) -> str:
        previous_analysis = json.dumps(data.get("previousAnalysis", {}), ensure_ascii=False)
        prompt = f"""
다음 이전 분석 결과를 바탕으로 재분석합니다.
재분석 유형: {reanalysis_type}
이전 분석: {previous_analysis}
새로운 학생 질문: {data.get('newStudentQuestion', '')}

이전 분석을 바탕으로 더 쉽고 명확하게 또는 더 상세하게 재해석해 주세요.
반환 형식은 기존 분석 JSON 구조와 동일해야 합니다.
"""
        return prompt
