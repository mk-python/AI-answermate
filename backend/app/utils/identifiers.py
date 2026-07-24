import uuid


def generate_analysis_id() -> str:
    return str(uuid.uuid4())
