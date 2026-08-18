"""
Pytest fixtures for CVBooster backend tests.

Environment variables MUST be set before any `src` module is imported:
- src/database.py reads DATABASE_PATH at import time
- routers read UPLOADS_DIR at import time
- config.load_dotenv() does not override pre-existing env vars, so the
  values set here win over the repository .env file.
"""
import os
import tempfile
import uuid

import pytest

_tmp = tempfile.mkdtemp(prefix="cvbooster-test-")
os.environ["DATABASE_PATH"] = os.path.join(_tmp, "test.db")
os.environ["UPLOADS_DIR"] = os.path.join(_tmp, "uploads")
os.environ["SKIP_AUTH"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-pytest-only-32b"
os.environ["USE_OPENROUTER"] = "false"
os.environ["LOCAL_LLM_URL"] = "http://localhost:1234"
os.environ["LOCAL_LLM_MODEL"] = "test-model"
os.environ["GOOGLE_CLIENT_ID"] = "test.apps.googleusercontent.com"
os.environ["GOOGLE_CLIENT_SECRET"] = "test"
os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost/api/auth/google/callback"

os.makedirs(os.path.join(_tmp, "uploads", "original-cvs"), exist_ok=True)
os.makedirs(os.path.join(_tmp, "uploads", "generated-cvs"), exist_ok=True)

from fastapi.testclient import TestClient  # noqa: E402
from src.main import app  # noqa: E402
from src.services import google_auth  # noqa: E402
from src.services import sqlite_storage  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def make_user(user_id: str = None):
    """Create a user and return (user_id, valid auth headers)."""
    if user_id is None:
        user_id = str(uuid.uuid4())
    token = google_auth.google_auth._generate_jwt(user_id)
    return user_id, {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def storage():
    return sqlite_storage.storage
