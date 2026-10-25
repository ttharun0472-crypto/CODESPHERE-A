import hashlib
import hmac
import logging
import os
import secrets
import smtplib
import socket
import ssl
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import EmailOtpChallenge, User
from app.utils.jwt import SECRET_KEY
from app.utils.password import hash_password

BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=BACKEND_ENV_FILE, override=False)
_BACKEND_ENV_VALUES = dotenv_values(BACKEND_ENV_FILE)

logger = logging.getLogger(__name__)

SMTP_SETTING_NAMES = (
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "SMTP_FROM_EMAIL",
)

OTP_TTL = timedelta(minutes=5)
OTP_RESEND_COOLDOWN = timedelta(seconds=60)
OTP_REQUEST_WINDOW = timedelta(hours=1)
OTP_REQUEST_LIMIT = 5
OTP_ATTEMPT_LIMIT = 5
GENERIC_REQUEST_MESSAGE = (
    "If an account exists for this address, a verification code will arrive shortly."
)
OTP_PURPOSE_LOGIN = "login"
OTP_PURPOSE_REGISTRATION = "registration"
OTP_PURPOSE_PASSWORD_RESET = "password_reset"


def _smtp_setting(name: str) -> str | None:
    value = os.getenv(name)
    if value is not None and value.strip():
        return value.strip()

    file_value = _BACKEND_ENV_VALUES.get(name)
    if file_value is not None and file_value.strip():
        return file_value.strip()
    return None


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _email_digest(email: str) -> str:
    normalized_email = email.strip().casefold()
    return hmac.new(
        SECRET_KEY.encode("utf-8"),
        normalized_email.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _otp_digest(email_digest: str, otp: str) -> str:
    return hmac.new(
        SECRET_KEY.encode("utf-8"),
        f"{email_digest}:{otp}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _clear_challenge(challenge: EmailOtpChallenge) -> None:
    challenge.otp_digest = None
    challenge.issued_at = None
    challenge.expires_at = None
    challenge.failed_attempts = 0
    challenge.verified = False
    challenge.verified_at = None


def _smtp_configuration() -> dict[str, str | int | bool]:
    values = {name: _smtp_setting(name) for name in SMTP_SETTING_NAMES}
    missing = [name for name, value in values.items() if value is None]
    if missing:
        raise HTTPException(
            status_code=503,
            detail=(
                "Email verification is not configured. Missing or empty SMTP "
                f"settings: {', '.join(missing)}. Configure them in backend/.env."
            ),
        )

    try:
        port = int(values["SMTP_PORT"])
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail="Email verification has an invalid SMTP_PORT configuration.",
        ) from exc

    if not 1 <= port <= 65535:
        raise HTTPException(
            status_code=503,
            detail="Email verification has an invalid SMTP_PORT configuration.",
        )

    host = values["SMTP_HOST"]
    sender = values["SMTP_FROM_EMAIL"]
    if any(character.isspace() for character in host):
        raise HTTPException(
            status_code=503,
            detail="Email verification has an invalid SMTP_HOST configuration.",
        )
    if parseaddr(sender)[1] != sender or "@" not in sender:
        raise HTTPException(
            status_code=503,
            detail="Email verification has an invalid SMTP_FROM_EMAIL configuration.",
        )

    use_ssl_value = (_smtp_setting("SMTP_USE_SSL") or "false").lower()
    use_tls_value = (_smtp_setting("SMTP_USE_TLS") or "true").lower()
    if use_ssl_value not in {"true", "false"} or use_tls_value not in {"true", "false"}:
        raise HTTPException(
            status_code=503,
            detail="Email verification has an invalid SMTP TLS configuration.",
        )
    use_ssl = use_ssl_value == "true"
    use_tls = use_tls_value == "true"
    if use_ssl and use_tls:
        raise HTTPException(
            status_code=503,
            detail="Configure either SMTP_USE_SSL or SMTP_USE_TLS, not both.",
        )

    return {
        "host": host,
        "port": port,
        "username": values["SMTP_USERNAME"],
        "password": values["SMTP_PASSWORD"],
        "from_email": sender,
        "use_ssl": use_ssl,
        "use_tls": use_tls,
    }


def _send_otp_email(email: str, otp: str, configuration: dict) -> None:
    message = EmailMessage()
    message["Subject"] = "Your CodeSphere AI verification code"
    message["From"] = configuration["from_email"]
    message["To"] = email
    message.set_content(
        f"Your CodeSphere AI verification code is {otp}.\n\n"
        "This code expires in 5 minutes. If you did not request this code, "
        "you can ignore this email."
    )
    message.add_alternative(
        "<html><body>"
        "<p>Your CodeSphere AI verification code is:</p>"
        f"<p style=\"font-size: 24px; font-weight: bold; letter-spacing: 4px;\">{otp}</p>"
        "<p>This code expires in 5 minutes. If you did not request this code, "
        "you can ignore this email.</p>"
        "</body></html>",
        subtype="html",
    )

    timeout = 15
    if configuration["use_ssl"]:
        with smtplib.SMTP_SSL(
            configuration["host"],
            configuration["port"],
            timeout=timeout,
            context=ssl.create_default_context(),
        ) as server:
            server.login(configuration["username"], configuration["password"])
            server.send_message(message)
        return

    with smtplib.SMTP(
        configuration["host"],
        configuration["port"],
        timeout=timeout,
    ) as server:
        if configuration["use_tls"]:
            server.starttls(context=ssl.create_default_context())
        server.login(configuration["username"], configuration["password"])
        server.send_message(message)


def _get_or_create_challenge(email_digest: str, db: Session) -> EmailOtpChallenge:
    challenge = (
        db.query(EmailOtpChallenge)
        .filter(EmailOtpChallenge.email_digest == email_digest)
        .with_for_update()
        .first()
    )
    if challenge is not None:
        return challenge

    challenge = EmailOtpChallenge(email_digest=email_digest, purpose=OTP_PURPOSE_LOGIN)
    try:
        with db.begin_nested():
            db.add(challenge)
            db.flush()
    except IntegrityError:
        challenge = (
            db.query(EmailOtpChallenge)
            .filter(EmailOtpChallenge.email_digest == email_digest)
            .with_for_update()
            .one()
        )
    return challenge


def _reset_if_purpose_changed(challenge: EmailOtpChallenge, purpose: str) -> None:
    if challenge.purpose != purpose:
        challenge.purpose = purpose
        _clear_challenge(challenge)


def request_email_otp(email: str, db: Session, purpose: str = OTP_PURPOSE_LOGIN) -> dict[str, int | str]:
    normalized_email = email.strip().casefold()
    digest = _email_digest(normalized_email)
    challenge = _get_or_create_challenge(digest, db)
    _reset_if_purpose_changed(challenge, purpose)

    now = _now()
    if challenge.last_requested_at is not None and now < challenge.last_requested_at + OTP_RESEND_COOLDOWN:
        retry_after = int((challenge.last_requested_at + OTP_RESEND_COOLDOWN - now).total_seconds())
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {max(retry_after, 1)} seconds before requesting another code.",
            headers={"Retry-After": str(max(retry_after, 1))},
        )

    if challenge.request_window_started_at is None or now >= challenge.request_window_started_at + OTP_REQUEST_WINDOW:
        challenge.request_window_started_at = now
        challenge.request_count = 0
    if challenge.request_count >= OTP_REQUEST_LIMIT:
        retry_after = int((challenge.request_window_started_at + OTP_REQUEST_WINDOW - now).total_seconds())
        raise HTTPException(
            status_code=429,
            detail="Too many verification code requests. Please try again later.",
            headers={"Retry-After": str(max(retry_after, 1))},
        )

    challenge.request_count += 1
    challenge.last_requested_at = now
    challenge.failed_attempts = 0

    user = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if user is None and purpose in {OTP_PURPOSE_LOGIN, OTP_PURPOSE_PASSWORD_RESET}:
        _clear_challenge(challenge)
        db.commit()
        return {
            "message": GENERIC_REQUEST_MESSAGE,
            "retry_after_seconds": int(OTP_RESEND_COOLDOWN.total_seconds()),
        }
    if user is not None and purpose == OTP_PURPOSE_REGISTRATION:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    otp = f"{secrets.randbelow(1_000_000):06d}"
    challenge.otp_digest = _otp_digest(digest, otp)
    challenge.issued_at = now
    challenge.expires_at = now + OTP_TTL
    challenge.verified = False
    challenge.verified_at = None
    db.commit()

    try:
        configuration = _smtp_configuration()
        _send_otp_email(normalized_email, otp, configuration)
    except smtplib.SMTPAuthenticationError as exc:
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail=(
                "The email provider rejected SMTP authentication. Check "
                "SMTP_USERNAME and SMTP_PASSWORD; Gmail requires an App Password."
            ),
        ) from exc
    except smtplib.SMTPRecipientsRefused as exc:
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="The email provider rejected the recipient address.",
        ) from exc
    except (socket.timeout, TimeoutError) as exc:
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="The connection to the email provider timed out. Check network access and SMTP_HOST/SMTP_PORT.",
        ) from exc
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, OSError) as exc:
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="Could not connect securely to the email provider. Check SMTP_HOST, SMTP_PORT, network access, and TLS settings.",
        ) from exc
    except smtplib.SMTPResponseException as exc:
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="The email provider rejected the verification email.",
        ) from exc
    except smtplib.SMTPException as exc:
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="The email provider could not accept the verification email.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error while sending OTP email")
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="The verification email could not be delivered.",
        ) from exc

    return {
        "message": GENERIC_REQUEST_MESSAGE,
        "retry_after_seconds": int(OTP_RESEND_COOLDOWN.total_seconds()),
    }


def _verify_challenge(email: str, otp: str, db: Session, purpose: str) -> EmailOtpChallenge:
    normalized_email = email.strip().casefold()
    digest = _email_digest(normalized_email)
    challenge = (
        db.query(EmailOtpChallenge)
        .filter(EmailOtpChallenge.email_digest == digest)
        .with_for_update()
        .first()
    )
    if challenge is None or challenge.purpose != purpose:
        raise HTTPException(
            status_code=400,
            detail="The verification code is invalid or expired. Request a new code.",
        )
    if challenge.failed_attempts >= OTP_ATTEMPT_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many incorrect verification attempts. Request a new code.",
        )
    if challenge.otp_digest is None:
        raise HTTPException(
            status_code=400,
            detail="The verification code is invalid or expired. Request a new code.",
        )
    if challenge.expires_at is None or _now() >= challenge.expires_at:
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="The verification code is invalid or expired. Request a new code.",
        )

    expected_digest = _otp_digest(digest, otp)
    if not hmac.compare_digest(challenge.otp_digest, expected_digest):
        challenge.failed_attempts += 1
        if challenge.failed_attempts >= OTP_ATTEMPT_LIMIT:
            _clear_challenge(challenge)
        db.commit()
        if challenge.failed_attempts >= OTP_ATTEMPT_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Too many incorrect verification attempts. Request a new code.",
            )
        raise HTTPException(
            status_code=400,
            detail="The verification code is invalid or expired. Request a new code.",
        )

    return challenge


def verify_email_otp(email: str, otp: str, db: Session) -> dict[str, str | bool]:
    challenge = _verify_challenge(email, otp, db, OTP_PURPOSE_LOGIN)

    user = db.query(User).filter(func.lower(User.email) == email.strip().casefold()).first()
    if user is None:
        _clear_challenge(challenge)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="The verification code is invalid or expired. Request a new code.",
        )

    from app.services.auth_service import create_user_tokens

    challenge.otp_digest = None
    challenge.issued_at = None
    challenge.expires_at = None
    challenge.failed_attempts = 0
    challenge.verified = False
    challenge.verified_at = None
    tokens = create_user_tokens(user, db, commit=False)
    db.commit()
    return tokens


def request_registration_otp(email: str, db: Session):
    normalized_email = email.strip().casefold()
    if db.query(User).filter(func.lower(User.email) == normalized_email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    return request_email_otp(normalized_email, db, purpose=OTP_PURPOSE_REGISTRATION)


def verify_registration_otp(email: str, otp: str, db: Session):
    challenge = _verify_challenge(email, otp, db, OTP_PURPOSE_REGISTRATION)
    challenge.verified = True
    challenge.verified_at = _now()
    challenge.failed_attempts = 0
    db.commit()
    return {"message": "Email verified successfully."}


def request_password_reset_otp(email: str, db: Session):
    normalized_email = email.strip().casefold()
    return request_email_otp(normalized_email, db, purpose=OTP_PURPOSE_PASSWORD_RESET)


def verify_password_reset_otp(email: str, otp: str, db: Session):
    challenge = _verify_challenge(email, otp, db, OTP_PURPOSE_PASSWORD_RESET)
    challenge.verified = True
    challenge.verified_at = _now()
    challenge.failed_attempts = 0
    db.commit()
    return {"message": "OTP verified. You may now set a new password."}


def reset_password_with_otp(email: str, otp: str, new_password: str, db: Session):
    normalized_email = email.strip().casefold()
    challenge = (
        db.query(EmailOtpChallenge)
        .filter(EmailOtpChallenge.email_digest == _email_digest(normalized_email))
        .with_for_update()
        .first()
    )
    if challenge is None or challenge.purpose != OTP_PURPOSE_PASSWORD_RESET:
        raise HTTPException(
            status_code=400,
            detail="The verification code is invalid or expired. Request a new code.",
        )
    if not challenge.verified:
        raise HTTPException(
            status_code=400,
            detail="Password reset verification is required before updating the password.",
        )
    if challenge.otp_digest is None or challenge.expires_at is None or _now() >= challenge.expires_at:
        _clear_challenge(challenge)
        challenge.purpose = OTP_PURPOSE_LOGIN
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="The verification code is invalid or expired. Request a new code.",
        )
    if not hmac.compare_digest(challenge.otp_digest, _otp_digest(_email_digest(normalized_email), otp)):
        challenge.failed_attempts += 1
        if challenge.failed_attempts >= OTP_ATTEMPT_LIMIT:
            _clear_challenge(challenge)
            challenge.purpose = OTP_PURPOSE_LOGIN
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="The verification code is invalid or expired. Request a new code.",
        )

    user_record = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if user_record is None:
        _clear_challenge(challenge)
        challenge.purpose = OTP_PURPOSE_LOGIN
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Account not found.",
        )

    user_record.password_hash = hash_password(new_password)
    user_record.refresh_token = None
    _clear_challenge(challenge)
    challenge.purpose = OTP_PURPOSE_LOGIN
    db.commit()
    return {"message": "Password reset successful."}
