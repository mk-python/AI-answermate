from flask import Flask
from flask_cors import CORS


def init_extensions(app: Flask) -> None:
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["ALLOWED_ORIGINS"]}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"],
        supports_credentials=False,
    )
