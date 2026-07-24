def test_missing_subject(client):
    response = client.post(
        "/api/analyze",
        data={"correctAnswer": "정답", "studentAnswer": "답"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_invalid_subject(client):
    response = client.post(
        "/api/analyze",
        data={"subject": "과학", "questionText": "문제", "correctAnswer": "정답", "studentAnswer": "답"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_missing_question_text_and_image(client):
    response = client.post(
        "/api/analyze",
        data={"subject": "수학", "correctAnswer": "정답", "studentAnswer": "답"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_missing_correct_answer(client):
    response = client.post(
        "/api/analyze",
        data={"subject": "수학", "questionText": "문제", "studentAnswer": "답"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_missing_student_answer(client):
    response = client.post(
        "/api/analyze",
        data={"subject": "수학", "questionText": "문제", "correctAnswer": "정답"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_invalid_question_type(client):
    response = client.post(
        "/api/analyze",
        data={"subject": "수학", "questionType": "주관식", "questionText": "문제", "correctAnswer": "정답", "studentAnswer": "답"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_text_too_long(client):
    response = client.post(
        "/api/analyze",
        data={"subject": "수학", "questionText": "a" * 8001, "correctAnswer": "정답", "studentAnswer": "답"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
