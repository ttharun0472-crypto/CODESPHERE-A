import hashlib
import hmac

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import EmailOtpChallenge, User
from app.schemas import (
    ChangePassword,
    UserLogin,
    UserProfileUpdate,
    UserRegister,
)
from app.utils.jwt import SECRET_KEY, create_access_token, create_refresh_token, verify_refresh_token
from app.utils.password import hash_password, verify_password


def _email_digest(email: str) -> str:
    normalized_email = email.strip().casefold()
    return hmac.new(
        SECRET_KEY.encode("utf-8"),
        normalized_email.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# =========================
# REGISTER USER
# =========================

def register_user(
    user: UserRegister,
    db: Session,
):
    normalized_username = user.username.strip()
    normalized_email = user.email.strip().casefold()

    existing_username = db.query(User).filter(
        func.lower(User.username) == normalized_username.casefold()
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    existing_email = db.query(User).filter(
        func.lower(User.email) == normalized_email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    challenge = (
        db.query(EmailOtpChallenge)
        .filter(EmailOtpChallenge.email_digest == _email_digest(normalized_email))
        .first()
    )
    if challenge is None or challenge.purpose != "registration" or not challenge.verified:
        raise HTTPException(
            status_code=400,
            detail="Email verification is required before creating an account.",
        )

    hashed_password = hash_password(user.password)
    new_user = User(
        username=normalized_username,
        email=normalized_email,
        password_hash=hashed_password,
        is_admin=False,
    )

    db.add(new_user)
    db.flush()

    challenge.otp_digest = None
    challenge.issued_at = None
    challenge.expires_at = None
    challenge.failed_attempts = 0
    challenge.verified = False
    challenge.verified_at = None
    challenge.purpose = "login"

    db.commit()
    db.refresh(new_user)
    return new_user


# =========================
# LOGIN USER
# =========================

def login_user(
    user: UserLogin,
    db: Session,
):
    normalized_email = user.email.strip().casefold()
    user_record = db.query(User).filter(
        func.lower(User.email) == normalized_email
    ).first()

    if user_record is None or not verify_password(user.password, user_record.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return create_user_tokens(user_record, db)


def admin_login_user(
    user: UserLogin,
    db: Session,
):
    normalized_email = user.email.strip().casefold()
    user_record = db.query(User).filter(
        func.lower(User.email) == normalized_email
    ).first()

    if user_record is None or not verify_password(user.password, user_record.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user_record.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return create_user_tokens(user_record, db)


def create_user_tokens(
    user: User,
    db: Session,
    *,
    commit: bool = True,
) -> dict[str, str | bool]:
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    user.refresh_token = refresh_token

    if commit:
        db.commit()

    role = "admin" if user.is_admin else "user"
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "is_admin": user.is_admin,
        "role": role,
    }


# =========================
# LOGOUT USER
# =========================

def logout_user(
    current_user: User,
    db: Session,
):
    current_user.refresh_token = None
    db.commit()
    return {"message": "Logout successful"}


# =========================
# REFRESH ACCESS TOKEN
# =========================

def refresh_access_token(
    refresh_token: str,
    db: Session,
):
    user_id = verify_refresh_token(refresh_token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    if user.refresh_token != refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has been revoked",
        )

    new_access_token = create_access_token(user.id)
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


# =========================
# UPDATE PROFILE
# =========================

def update_profile(
    profile: UserProfileUpdate,
    current_user: User,
    db: Session,
):
    existing_username = db.query(User).filter(
        func.lower(User.username) == profile.username.strip().casefold(),
        User.id != current_user.id,
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    existing_email = db.query(User).filter(
        func.lower(User.email) == profile.email.strip().casefold(),
        User.id != current_user.id,
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    current_user.username = profile.username.strip()
    current_user.email = profile.email.strip().casefold()

    db.commit()
    db.refresh(current_user)
    return current_user


# =========================
# CHANGE PASSWORD
# =========================

def change_password(
    passwords: ChangePassword,
    current_user: User,
    db: Session,
):
    password_correct = verify_password(
        passwords.current_password,
        current_user.password_hash,
    )

    if not password_correct:
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    current_user.password_hash = hash_password(passwords.new_password)
    current_user.refresh_token = None
    db.commit()

    return {"message": "Password changed successfully"}