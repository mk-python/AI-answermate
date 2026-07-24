import io
from unittest.mock import patch


def test_normal_text_analysis_request(client, sample_text_payload):
    with patch("app.services.analysis_service.AIService.analyze", return_value={
        "studentQuestion": "왜 틀렸나요?",
        "questionAnswer": "답은 3입니다.",
        "errorType": "계산 오류",
        "correctParts": ["개념은 맞습니다."],
        "firstError": "처음 계산이 틀렸습니다.",
        "correctSolution": ["1단계", "2단계"],
        "comparison": [{"step": 1, "studentStep": "2", "correctStep": "3", "status": "차이 있음", "questionRelated": True}],
        "reviewContent": ["계산 순서를 확인하세요."],
        "caution": "주의하세요.",
    }):
        response = client.post("/api/analyze", data=sample_text_payload, content_type="multipart/form-data")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True


def test_analysis_with_question_image(client, sample_image_bytes):
    with patch("app.services.analysis_service.AIService.analyze", return_value={
        "studentQuestion": "왜 틀렸나요?",
        "questionAnswer": "답은 3입니다.",
        "errorType": "계산 오류",
        "correctParts": ["개념은 맞습니다."],
        "firstError": "처음 계산이 틀렸습니다.",
        "correctSolution": ["1단계", "2단계"],
        "comparison": [{"step": 1, "studentStep": "2", "correctStep": "3", "status": "차이 있음", "questionRelated": True}],
        "reviewContent": ["계산 순서를 확인하세요."],
        "caution": "주의하세요.",
    }):
        response = client.post(
            "/api/analyze",
            data={
                "subject": "수학",
                "questionText": "문제",
                "correctAnswer": "정답",
                "studentAnswer": "답",
                "questionImage": (io.BytesIO(sample_image_bytes), "test.png"),
            },
            content_type="multipart/form-data",
        )
        assert response.status_code == 200


def test_question_without_student_question(client, sample_text_payload):
    data = sample_text_payload.copy()
    data.pop("studentQuestion")
    with patch("app.services.analysis_service.AIService.analyze", return_value={
        "studentQuestion": "",
        "questionAnswer": "답은 3입니다.",
        "errorType": "계산 오류",
        "correctParts": ["개념은 맞습니다."],
        "firstError": "처음 계산이 틀렸습니다.",
        "correctSolution": ["1단계", "2단계"],
        "comparison": [{"step": 1, "studentStep": "2", "correctStep": "3", "status": "차이 있음", "questionRelated": True}],
        "reviewContent": ["계산 순서를 확인하세요."],
        "caution": "주의하세요.",
    }):
        response = client.post("/api/analyze", data=data, content_type="multipart/form-data")
        assert response.status_code == 200


def test_analysis_without_student_solution(client, sample_text_payload):
    data = sample_text_payload.copy()
    data.pop("studentSolution")
    with patch("app.services.analysis_service.AIService.analyze", return_value={
        "studentQuestion": "왜 틀렸나요?",
        "questionAnswer": "답은 3입니다.",
        "errorType": "계산 오류",
        "correctParts": ["개념은 맞습니다."],
        "firstError": "처음 계산이 틀렸습니다.",
        "correctSolution": ["1단계", "2단계"],
        "comparison": [{"step": 1, "studentStep": "2", "correctStep": "3", "status": "차이 있음", "questionRelated": True}],
        "reviewContent": ["계산 순서를 확인하세요."],
        "caution": "주의하세요.",
    }):
        response = client.post("/api/analyze", data=data, content_type="multipart/form-data")
        assert response.status_code == 200
