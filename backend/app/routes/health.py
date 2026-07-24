from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health() -> tuple:
    return jsonify(
        {
            "success": True,
            "status": "available",
            "service": "AI Wrong Answer Analysis API",
        }
    ), 200
