import io

from PIL import Image


def test_normal_image(client, sample_image_bytes):
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


def test_unsupported_image_type(client):
    image_bytes = b"not-an-image"
    response = client.post(
        "/api/analyze",
        data={
            "subject": "수학",
            "questionText": "문제",
            "correctAnswer": "정답",
            "studentAnswer": "답",
            "questionImage": (io.BytesIO(image_bytes), "test.txt"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_empty_file(client):
    response = client.post(
        "/api/analyze",
        data={
            "subject": "수학",
            "questionText": "문제",
            "correctAnswer": "정답",
            "studentAnswer": "답",
            "questionImage": (io.BytesIO(b""), "empty.png"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
