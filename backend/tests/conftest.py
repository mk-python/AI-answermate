import io
from typing import Any, Dict

import pytest
from PIL import Image

from app import create_app


@pytest.fixture()
def app() -> Any:
    app = create_app(testing=True)
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def client(app: Any):
    return app.test_client()


@pytest.fixture()
def sample_text_payload() -> Dict[str, str]:
    return {
        "subject": "수학",
        "unit": "함수",
        "questionType": "객관식",
        "questionText": "다음 함수의 그래프를 보고 x값을 구하시오.",
        "correctAnswer": "3",
        "studentAnswer": "2",
        "studentSolution": "계산 과정을 적었습니다.",
        "studentQuestion": "왜 틀렸나요?",
    }


@pytest.fixture()
def sample_image_bytes() -> bytes:
    image = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
