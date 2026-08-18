"""Auth: signed JWTs only - forged/unsigned tokens must be rejected."""
import jwt as pyjwt
from datetime import datetime, timedelta, timezone


def test_missing_token_401(client):
    r = client.get("/api/auth/session")
    assert r.status_code == 401


def test_forged_token_rejected(client):
    """A token signed with a different secret must NOT be accepted (impersonation)."""
    forged = pyjwt.encode(
        {"sub": "victim-user", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "attacker-secret-key",
        algorithm="HS256",
    )
    r = client.get("/api/auth/session", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401


def test_valid_token_accepted(client):
    from conftest import make_user
    user_id, headers = make_user()
    r = client.get("/api/auth/session", headers=headers)
    assert r.status_code == 200
    assert r.json()["user"]["id"] == user_id
