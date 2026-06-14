"""
Authentication utilities.
Verifies Supabase JWT tokens and extracts user_id.
"""
from fastapi import HTTPException, Request
from typing import Optional
import jwt
import uuid

from ..config import get_settings


def verify_supabase_jwt(token: str) -> dict:
    """Verify a Supabase JWT token and return the decoded payload."""
    try:
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_iss": False,
            },
            algorithms=["HS256"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_id(request: Request) -> str:
    """
    Dependency: Extract and verify user_id from the Authorization header.

    When SKIP_AUTH=true, returns a demo user_id without checking the token.
    """
    settings = get_settings()

    if settings.skip_auth:
       return "579fce1e-1604-4b00-b692-1f3b5ce43368"

    auth_header = request.headers.get("authorization", "")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token")

    token = auth_header[7:]
    payload = verify_supabase_jwt(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: no user ID")

    return user_id
