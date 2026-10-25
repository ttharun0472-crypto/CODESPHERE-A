from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.models import User

from app.schemas import (
    AccessTokenResponse,
    ChangePassword,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserProfileUpdate,
    UserRegister,
    UserResponse,
)
from app.schemas.email_otp_schema import (
    EmailOtpRequest,
    EmailOtpRequestResponse,
    EmailOtpVerify,
    PasswordResetConfirm,
)

from app.services.auth_service import (
    admin_login_user,
    change_password,
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
    update_profile,
)
from app.services.email_otp_service import (
    request_email_otp,
    request_password_reset_otp,
    request_registration_otp,
    reset_password_with_otp,
    verify_email_otp,
    verify_password_reset_otp,
    verify_registration_otp,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    return register_user(user, db)


@router.post("/register/request-otp", response_model=EmailOtpRequestResponse, status_code=202)
def request_register_otp(request: EmailOtpRequest, db: Session = Depends(get_db)):
    return request_registration_otp(request.email, db)


@router.post("/register/verify-otp", response_model=dict[str, str])
def verify_register_otp(request: EmailOtpVerify, db: Session = Depends(get_db)):
    return verify_registration_otp(request.email, request.otp, db)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(user, db)


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(user: UserLogin, db: Session = Depends(get_db)):
    return admin_login_user(user, db)


@router.post("/otp/request", response_model=EmailOtpRequestResponse, status_code=202)
def request_login_otp(request: EmailOtpRequest, db: Session = Depends(get_db)):
    return request_email_otp(request.email, db)


@router.post("/otp/verify", response_model=TokenResponse)
def verify_login_otp(request: EmailOtpVerify, db: Session = Depends(get_db)):
    return verify_email_otp(request.email, request.otp, db)


@router.post("/password-reset/request", response_model=EmailOtpRequestResponse, status_code=202)
def request_reset_otp(request: EmailOtpRequest, db: Session = Depends(get_db)):
    return request_password_reset_otp(request.email, db)


@router.post("/password-reset/verify", response_model=dict[str, str])
def verify_reset_otp(request: EmailOtpVerify, db: Session = Depends(get_db)):
    return verify_password_reset_otp(request.email, request.otp, db)


@router.post("/password-reset", response_model=dict[str, str])
def password_reset(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return reset_password_with_otp(request.email, request.otp, request.new_password, db)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return logout_user(current_user, db)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return refresh_access_token(token_data.refresh_token, db)


@router.put("/profile", response_model=UserResponse)
def profile(profile_data: UserProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_profile(profile_data, current_user, db)


@router.put("/change-password")
def password(passwords: ChangePassword, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return change_password(passwords, current_user, db)
