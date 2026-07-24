import io
from typing import Optional

from PIL import Image


class ImageService:
    @staticmethod
    def prepare_image(image_bytes: bytes, max_side: int) -> bytes:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
        if image.mode in {"RGBA", "LA", "P"}:
            image = image.convert("RGB")

        exif_orientation = image.getexif().get(274)
        if exif_orientation in {3, 6, 8}:
            image = image.rotate(360 - ((exif_orientation - 1) * 90), expand=True)

        width, height = image.size
        max_dimension = max(width, height)
        if max_dimension > max_side:
            ratio = max_side / max_dimension
            width = int(width * ratio)
            height = int(height * ratio)
            image = image.resize((width, height), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
