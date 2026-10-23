"""
Authentication helpers: password hashing, JWT session tokens,
and a FastAPI dependency that resolves the signed-in user.
"""

import hashlib
import hmac
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import jwt
from fastapi import Header, HTTPException

PBKDF2_ITERATIONS = 310_000
TOKEN_TTL_DAYS = 7
JWT_ALGORITHM = "HS256"

_SECRET_FILE = Path(__file__).resolve().parents[2] / ".auth_secret"


def _load_secret() -> str:
    """
    Use AUTH_SECRET from the environment when set. Otherwise generate a
    random secret once and keep it in backend/.auth_secret (git-ignored)
    so sessions survive server restarts in local development.
    """
    secret = os.getenv("AUTH_SECRET")
    if secret:
        return secret
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text().strip()
    secret = secrets.token_urlsafe(48)
    try:
        _SECRET_FILE.write_text(secret)
    except OSError:
        # Read-only hosts (e.g. Vercel) can't store the file
        raise RuntimeError("AUTH_SECRET is not set. Set it as an environment variable on this host.")
    return secret


AUTH_SECRET = _load_secret()


def hash_password(password: str) -> str:
    """Hash a password as pbkdf2_sha256$iterations$salt$hash"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored: Optional[str]) -> bool:
    if not stored:
        return False
    try:
        _, iterations, salt, expected = stored.split("$")
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), expected)


def create_token(user_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(days=TOKEN_TTL_DAYS)}
    return jwt.encode(payload, AUTH_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user_id(authorization: Optional[str] = Header(default=None)) -> uuid.UUID:
    """FastAPI dependency: return the user id from a valid Bearer token or raise 401"""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=[JWT_ALGORITHM])
        return uuid.UUID(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Your session has expired. Please sign in again.")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid session. Please sign in again.")


def authorize_user(path_user_id: str, current_user_id: uuid.UUID) -> uuid.UUID:
    """Ensure the user id in the URL belongs to the signed-in user"""
    try:
        requested = uuid.UUID(path_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid user_id format: {path_user_id}")
    if requested != current_user_id:
        raise HTTPException(status_code=403, detail="You can only access your own tasks.")
    return requested
