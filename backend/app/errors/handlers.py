from flask import Flask, jsonify

from .exceptions import ApiErrorException


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiErrorException)
    def handle_api_error(error: ApiErrorException):
        status_code = 400 if not error.retryable else 503
        if error.error_code == "AI_AUTH_ERROR":
            status_code = 500
        return jsonify(
            {
                "success": False,
                "error": {
                    "errorCode": error.error_code,
                    "message": error.message,
                    "retryable": error.retryable,
                    "details": error.details,
                },
            }
        ), status_code

    @app.errorhandler(413)
    def handle_request_too_large(_error):
        return jsonify(
            {
                "success": False,
                "error": {
                    "errorCode": "REQUEST_TOO_LARGE",
                    "message": "요청 크기가 너무 큽니다.",
                    "retryable": False,
                    "details": {},
                },
            }
        ), 413

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify(
            {
                "success": False,
                "error": {
                    "errorCode": "SERVER_ERROR",
                    "message": "요청 경로를 찾을 수 없습니다.",
                    "retryable": False,
                    "details": {},
                },
            }
        ), 404

    @app.errorhandler(500)
    def handle_server_error(_error):
        return jsonify(
            {
                "success": False,
                "error": {
                    "errorCode": "SERVER_ERROR",
                    "message": "서버 내부 오류가 발생했습니다.",
                    "retryable": True,
                    "details": {},
                },
            }
        ), 500
