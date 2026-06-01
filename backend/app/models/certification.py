"""Certification database models — T16.

Tables:
- certification_levels: 认证级别定义 (L1/L2/L3/L4)
- certification_applications: 用户认证申请
- certificates: 已颁发证书
- capstone_submissions: 顶点项目提交 (L2)
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models import Base, _utcnow


class CertificationLevel(Base):
    """认证级别定义 — L1/L2/L3/L4."""

    __tablename__ = "certification_levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    required_courses = Column(JSON, default=list)  # JSON list of course IDs
    min_average_score = Column(Float, default=70.0)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    applications = relationship("CertificationApplication", back_populates="level")
    certificates = relationship("Certificate", back_populates="level")
    capstone_submissions = relationship("CapstoneSubmission", back_populates="level")

    def __repr__(self):
        return f"<CertificationLevel(id={self.id}, name={self.name!r})>"


class CertificationApplication(Base):
    """用户认证申请."""

    __tablename__ = "certification_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("certification_levels.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending / approved / rejected
    evaluation_data = Column(JSON, nullable=True)
    evaluator_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User", back_populates="certification_applications")
    level = relationship("CertificationLevel", back_populates="applications")

    def __repr__(self):
        return (
            f"<CertificationApplication(id={self.id}, user_id={self.user_id}, "
            f"status={self.status!r})>"
        )


class Certificate(Base):
    """已颁发证书."""

    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("certification_levels.id"), nullable=False)
    cert_number = Column(String(100), unique=True, nullable=False, index=True)
    issue_date = Column(DateTime, nullable=True)  # 由 service 设置
    cert_metadata = Column(JSON, nullable=True)
    signature = Column(String(500), nullable=True)  # ECDSA signature
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User", back_populates="certificates")
    level = relationship("CertificationLevel", back_populates="certificates")

    def __repr__(self):
        return f"<Certificate(id={self.id}, cert_number={self.cert_number!r})>"


class CapstoneSubmission(Base):
    """顶点项目提交 — L2 认证."""

    __tablename__ = "capstone_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("certification_levels.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    repository_url = Column(String(500), nullable=True)
    submission_data = Column(JSON, nullable=True)
    status = Column(String(20), default="submitted")  # submitted / reviewing / approved / rejected
    ai_review = Column(JSON, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="capstone_submissions")
    level = relationship("CertificationLevel", back_populates="capstone_submissions")
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<CapstoneSubmission(id={self.id}, title={self.title!r}, status={self.status!r})>"
