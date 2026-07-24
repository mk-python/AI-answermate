from flask import Blueprint, current_app, jsonify, request

from ..errors.exceptions import ApiErrorException
from ..services.analysis_service import AnalysisService

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api")
analysis_service = AnalysisService()


@analysis_bp.post("/analyze")
def analyze():
    if not request.is_json and not request.form:
        raise ApiErrorException("MISSING_FIELD", "요청 본문이 올바르지 않습니다.", details={"field": "body"})

    form_data = request.form.to_dict(flat=True)
    files = request.files.to_dict(flat=True)
    app_config = {
        "MAX_IMAGE_SIZE": current_app.config["MAX_IMAGE_SIZE"],
        "MAX_IMAGE_SIDE": current_app.config["MAX_IMAGE_SIDE"],
    }
    response = analysis_service.analyze(form_data, files, app_config)
    return jsonify(response), 200


@analysis_bp.post("/reanalyze")
def reanalyze():
    if not request.is_json and not request.form:
        raise ApiErrorException("MISSING_FIELD", "요청 본문이 올바르지 않습니다.", details={"field": "body"})

    form_data = request.form.to_dict(flat=True)
    files = request.files.to_dict(flat=True)
    app_config = {
        "MAX_IMAGE_SIZE": current_app.config["MAX_IMAGE_SIZE"],
        "MAX_IMAGE_SIDE": current_app.config["MAX_IMAGE_SIDE"],
    }
    response = analysis_service.reanalyze(form_data, files, app_config)
    return jsonify(response), 200
