import pytest
from fastapi import testclient

from pilates.interfaces.api import app


@pytest.fixture()
def api_client() -> testclient.TestClient:
    return testclient.TestClient(app.app)
