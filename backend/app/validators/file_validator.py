import io
from typing import Any, Dict, Optional

from PIL import Image, UnidentifiedImageError

from ..errors.exceptions import ApiErrorException


class FileValidator:
    @staticmethod
    def validate_file(file_storage: Any, field_name: str, max_size: int, max_side: int) -> Optional[bytes]:
        if file_storage is None:
            return None

        if getattr(file_storage, "filename", None) is None:
            raise ApiErrorException("INVALID_IMAGE_TYPE", "파일 이름이 올바르지 않습니다.", details={"field": field_name})

        if not file_storage:
            raise ApiErrorException("INVALID_IMAGE_TYPE", "빈 파일은 업로드할 수 없습니다.", details={"field": field_name})

        file_content = file_storage.read()
        if not file_content:
            raise ApiErrorException("INVALID_IMAGE_TYPE", "빈 파일은 업로드할 수 없습니다.", details={"field": field_name})

        if len(file_content) > max_size:
            raise ApiErrorException("IMAGE_TOO_LARGE", "이미지 용량이 너무 큽니다.", details={"field": field_name})

        try:
            image = Image.open(io.BytesIO(file_content))
            image.verify()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ApiErrorException("BROKEN_IMAGE", "손상된 이미지입니다.", details={"field": field_name}) from exc

        try:
            image = Image.open(io.BytesIO(file_content))
            image.load()
            if image.mode in {"RGBA", "LA", "P"}:
                image = image.convert("RGB")
            exif_orientation = image.getexif().get(274)
            if exif_orientation in {3, 6, 8}:
                image = image.rotate(360 - ((exif_orientation - 1) * 90), expand=True)
            width, height = image.size
            if width > max_side or height > max_side:
                raise ApiErrorException("BROKEN_IMAGE", "이미지 크기가 너무 큽니다.", details={"field": field_name})
            if width <= 0 or height <= 0:
                raise ApiErrorException("BROKEN_IMAGE", "이미지 크기가 올바르지 않습니다.", details={"field": field_name})
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ApiErrorException("BROKEN_IMAGE", "손상된 이미지입니다.", details={"field": field_name}) from exc

        return file_content
