"""
Auth API Endpoints
Sign up, sign in, and fetch the current user.
"""

import re
import uuid
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

import sys
from pathlib import Path

# Add the backend directory to the Python path to resolve imports
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.models.user import User
from src.services.database import get_session
from src.services.auth_service import (
    hash_password,
    verify_password,
    create_token,
    get_current_user_id,
)


router = APIRouter(prefix="/api/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def _public_user(user: User) -> Dict[str, Any]:
    return {"id": str(user.id), "name": user.username, "email": user.email}


def _session_response(user: User) -> Dict[str, Any]:
    return {"token": create_token(user.id), "user": _public_user(user)}


@router.post("/signup")
def signup(request: Dict[str, Any]):
    name = str(request.get("name", "")).strip()
    email = str(request.get("email", "")).strip().lower()
    password = str(request.get("password", ""))

    if not name or len(name) > 100:
        raise HTTPException(status_code=400, detail="Please enter your name (up to 100 characters).")
    if not EMAIL_RE.match(email) or len(email) > 255:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(status_code=400, detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")

    with next(get_session()) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists. Try signing in.")

        user = User(email=email, username=name, password_hash=hash_password(password))
        session.add(user)
        session.commit()
        session.refresh(user)
        return _session_response(user)


@router.post("/signin")
def signin(request: Dict[str, Any]):
    email = str(request.get("email", "")).strip().lower()
    password = str(request.get("password", ""))

    if not email or not password:
        raise HTTPException(status_code=400, detail="Please enter your email and password.")

    with next(get_session()) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        # Same message for unknown email and wrong password, so accounts can't be probed
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect email or password.")
        return _session_response(user)


@router.get("/me")
def me(current_user_id: uuid.UUID = Depends(get_current_user_id)):
    with next(get_session()) as session:
        user = session.get(User, current_user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Account not found. Please sign in again.")
        return {"user": _public_user(user)}
