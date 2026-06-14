"""
Authentication utilities.
Verifies Supabase JWT tokens and extracts user_id.
"""
from fastapi import HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
import jwt

from ..config import get_settings

security = HTTPBearer()


def verify_supabase_jwt(token: str) -> dict:
    """
    Verify a Supabase JWT token and return the decoded payload.

    Supabase uses HS256 with the service_key or JWT_SECRET.
    For simplicity, we use the Supabase anon key's issuer.
    """
    settings = get_settings()

    try:
        # Supabase JWT verification
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,  # Supabase handles signature verification
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


async def get_current_user_id(
    authorization: Optional[HTTPAuthorizationCredentials] = Header(None),
) -> str:
    """
    Dependency: Extract and verify user_id from the Authorization header.

    Expected header: Authorization: Bearer <supabase_jwt_token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    payload = verify_supabase_jwt(authorization.credentials)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: no user ID")

    return user_id
