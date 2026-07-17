"""
Google OAuth authentication service for CVBooster.
Handles Google sign-in and JWT token generation.
"""
import os
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import httpx

from ..config import get_settings
from ..database import get_db, Profile
from ..services.sqlite_storage import storage


class GoogleAuthService:
    """Service for Google OAuth authentication."""
    
    def __init__(self):
        self.settings = get_settings()
        self.google_client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
        self.google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
        self.google_redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "")
        self.jwt_secret = os.environ.get("JWT_SECRET", "cvbooster-secret-key-change-in-production")
        self.jwt_expiry_hours = 24
    
    def get_google_auth_url(self) -> str:
        """Generate Google OAuth authorization URL."""
        scope = "email profile"
        state = str(uuid.uuid4())
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={self.google_client_id}&"
            f"redirect_uri={self.google_redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"state={state}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        return auth_url
    
    async def verify_google_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google OAuth code and exchange for user info.
        
        Args:
            code: Authorization code from Google callback
            
        Returns:
            User info dict or None if verification fails
        """
        try:
            # Exchange code for tokens
            token_url = "https://oauth2.googleapis.com/token"
            
            response = httpx.post(
                token_url,
                data={
                    "code": code,
                    "client_id": self.google_client_id,
                    "client_secret": self.google_client_secret,
                    "redirect_uri": self.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"[Google Auth] Token exchange failed: {response.text}")
                return None
            
            token_data = response.json()
            id_token_str = token_data.get("id_token")
            
            if not id_token_str:
                print("[Google Auth] No id_token in response")
                return None
            
            # Verify ID token
            try:
                payload = id_token.verify_oauth2_token(
                    id_token_str,
                    google_requests.Request(),
                    self.google_client_id
                )
            except ValueError as e:
                print(f"[Google Auth] Token verification failed: {e}")
                return None
            
            # Extract user info
            user_id = payload.get("sub")
            email = payload.get("email")
            name = payload.get("name")
            picture = payload.get("picture")
            
            if not user_id:
                print("[Google Auth] No user_id in token")
                return None
            
            # Create/update profile in database
            profile = storage.create_profile(
                user_id=user_id,
                full_name=name or "",
                avatar_url=picture or "",
                provider="google",
                email=email
            )
            
            # Generate JWT token for session
            jwt_token = self._generate_jwt(user_id)
            
            return {
                "user": profile,
                "access_token": jwt_token,
                "token_type": "bearer",
                "expires_in": self.jwt_expiry_hours * 3600,
            }
            
        except Exception as e:
            print(f"[Google Auth] Error verifying token: {e}")
            return None
    
    def _generate_jwt(self, user_id: str) -> str:
        """Generate JWT token for user."""
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours),
            "type": "access_token",
        }
        
        token = jwt.encode(
            payload,
            self.jwt_secret,
            algorithm="HS256"
        )
        
        return token
    
    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            print("[Google Auth] JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"[Google Auth] Invalid JWT token: {e}")
            return None


# Singleton instance
google_auth = GoogleAuthService()
