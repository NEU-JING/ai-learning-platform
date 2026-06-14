"""Employer module database models.

Tables:
- employers: 雇主账户 (API Key 认证)
- verification_codes: 验证授权码 (用户授权雇主查看)
- employer_api_logs: API 调用审计日志 (AC47)
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.models import Base, _utcnow


class Employer(Base):
    """雇主账户 — API Key 认证."""

    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(128), nullable=False)
    contact_email = Column(String(128), unique=True, nullable=False)
    api_key = Column(String(64), unique=True, nullable=False)
    rate_limit = Column(Integer, default=1000)  # 每小时请求数
    tier = Column(String(16), default="basic")  # basic, premium, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    verification_codes = relationship("VerificationCode", back_populates="employer")
    api_logs = relationship("EmployerApiLog", back_populates="employer")

    def __repr__(self):
        return f"<Employer(id={self.id}, company={self.company_name!r})>"


class VerificationCode(Base):
    """验证授权码 — 用户授权雇主查看数据."""

    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(32), unique=True, nullable=False)  # 8位字母数字
    permissions = Column(
        JSON,
        default={"certifications": True, "skill_summary": True, "lab_history": False},
    )
    expires_at = Column(DateTime, nullable=False)
    used_by = Column(Integer, ForeignKey("employers.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User")
    employer = relationship("Employer", back_populates="verification_codes", foreign_keys=[used_by])

    def __repr__(self):
        return f"<VerificationCode(id={self.id}, code={self.code!r})>"


class EmployerApiLog(Base):
    """API 调用审计日志 (AC47)."""

    __tablename__ = "employer_api_logs"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=True)
    endpoint = Column(String(64), nullable=True)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    employer = relationship("Employer", back_populates="api_logs")

    def __repr__(self):
        return (
            f"<EmployerApiLog(id={self.id}, endpoint={self.endpoint!r}, "
            f"status={self.status_code})>"
        )
