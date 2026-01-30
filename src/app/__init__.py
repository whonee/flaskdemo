import os
from logging.config import dictConfig
from pathlib import Path

import markdown
from flask import Flask, g, render_template, session
from werkzeug.exceptions import HTTPException

from . import auth, blog, db


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        DATABASE=Path(app.instance_path) / "app.sqlite",
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    @app.route("/health")
    def health() -> str:
        return "ok"

    @app.template_filter("markdown")
    def markdown_filter(text):
        return markdown.markdown(text, extensions=["fenced_code", "tables"])

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(Exception, handle_exception)

    return app


def handle_exception(e):  # # noqa: ARG001
    # now you're handling non-HTTP exceptions only
    # return render_template("500_generic.html", e=e), 500
    return render_template("error/500.html"), 500


def handle_http_exception(e):
    # pass through HTTP errors
    if e.code == 404:
        return render_template("error/404.html"), 404

    return render_template("error/500.html"), 500


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        },
        "custom": {
            "()": "app.utils.log.RequestFormatter",
            "format": "%(asctime)s | %(remote_addr)s - %(url)s | %(name)s | %(levelname)s \n%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
        },
        "applog": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/app.log",
            "when": "midnight",
            "backupCount": 7,
            "formatter": "custom",
        },
        "werkzeuglog": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/werkzeug.log",
            "when": "midnight",
            "backupCount": 7,
            "formatter": "custom",
        },
    },
    "loggers": {
        "app": {
            "level": "INFO",
            "handlers": ["console", "applog"],
            "propagate": False,
        },
        "werkzeug": {
            "handlers": ["werkzeuglog"],
            "level": "DEBUG",
            "propagate": True,  # 关键：保留原输出
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

dictConfig(LOGGING_CONFIG)
