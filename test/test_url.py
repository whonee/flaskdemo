from flask import url_for


def test_url() -> None:

    assert url_for("index") == "/"
    assert url_for("health") == "/health"


def test_url_for_static_directory() -> None:
    assert url_for("static", filename="js/main.js") == "/static/js/main.js"
    assert url_for("static", filename="css/style.css") == "/static/css/style.css"
