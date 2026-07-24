from collections import defaultdict
from time import time

from flask import Flask, request

from .config import Config
from .errors.exceptions import ApiErrorException
from .errors.handlers import register_error_handlers
from .extensions import init_extensions
from .routes.analysis import analysis_bp
from .routes.health import health_bp


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["TESTING"] = testing

    init_extensions(app)
    register_error_handlers(app)

    request_log: dict[str, list[float]] = defaultdict(list)

    @app.before_request
    def enforce_rate_limit() -> None:
        if app.config["TESTING"]:
            return
        client_ip = request.remote_addr or "unknown"
        now = time()
        history = request_log[client_ip]
        history[:] = [timestamp for timestamp in history if now - timestamp < app.config["RATE_LIMIT_WINDOW"]]
        if len(history) >= app.config["RATE_LIMIT_COUNT"]:
            raise ApiErrorException("TOO_MANY_REQUESTS", "요청 횟수가 너무 많습니다.", retryable=True)
        history.append(now)

    app.register_blueprint(health_bp)
    app.register_blueprint(analysis_bp)

    return app
