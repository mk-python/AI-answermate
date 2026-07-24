from unittest.mock import patch


def test_reanalysis_easy(client, sample_text_payload):
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
            "/api/reanalyze",
            data={
                **sample_text_payload,
                "reanalysisType": "easy",
                "previousAnalysis": '{"studentQuestion": "x"}',
            },
            content_type="multipart/form-data",
        )
        assert response.status_code == 200


def test_reanalysis_invalid_type(client, sample_text_payload):
    response = client.post(
        "/api/reanalyze",
        data={
            **sample_text_payload,
            "reanalysisType": "unknown",
            "previousAnalysis": '{"studentQuestion": "x"}',
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_previous_analysis_missing(client, sample_text_payload):
    response = client.post(
        "/api/reanalyze",
        data={
            **sample_text_payload,
            "reanalysisType": "easy",
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_previous_analysis_json_error(client, sample_text_payload):
    response = client.post(
        "/api/reanalyze",
        data={
            **sample_text_payload,
            "reanalysisType": "easy",
            "previousAnalysis": '{bad json',
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
