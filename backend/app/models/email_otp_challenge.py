from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.config.database import Base


class EmailOtpChallenge(Base):
    __tablename__ = "email_otp_challenges"

    email_digest = Column(String(64), primary_key=True)
    otp_digest = Column(String(64), nullable=True)
    purpose = Column(String(32), nullable=False, default="login")
    verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime, nullable=True)
    issued_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    request_window_started_at = Column(DateTime, nullable=True)
    request_count = Column(Integer, nullable=False, default=0)
    last_requested_at = Column(DateTime, nullable=True)
