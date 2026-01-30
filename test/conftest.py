import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from flask.ctx import RequestContext

from app import create_app
from app.db import get_db, init_db

with open(Path(__file__).parent / "data.sql", "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture(autouse=True)
def app_context() -> Generator[RequestContext, None, None]:
    with create_app().test_request_context() as ctx:
        yield ctx


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    Path(db_path).unlink()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client) -> None:
        self._client = client

    def login(self, username="test", password="test") -> Any:
        return self._client.post("/auth/login", data={"username": username, "password": password})

    def logout(self) -> Any:
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client) -> AuthActions:
    return AuthActions(client)
