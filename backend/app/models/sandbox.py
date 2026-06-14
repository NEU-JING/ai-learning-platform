"""Sandbox module models — execution_requests, external_executions, verification_tasks, sandbox_providers."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models import Base, _utcnow


class ExecutionRequest(Base):
    __tablename__ = "execution_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=True)
    layer = Column(String(8), nullable=False)  # A, B, C
    code = Column(Text, nullable=True)
    language = Column(String(16), default="python")
    resources = Column(JSON, nullable=True)  # {cpu: 2, memory: "4g"}
    status = Column(String(16), default="pending")  # pending, running, completed, failed
    result = Column(JSON, nullable=True)
    logs = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # relationships
    user = relationship("User")
    external_executions = relationship("ExternalExecution", back_populates="request")
    verification_tasks = relationship("VerificationTask", back_populates="request")


class ExternalExecution(Base):
    __tablename__ = "external_executions"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("execution_requests.id"), nullable=True)
    provider = Column(String(16), nullable=True)  # kaggle, colab, autodl
    external_job_id = Column(String(64), nullable=True)
    artifacts = Column(JSON, nullable=True)  # {model_url: "...", log_url: "..."}
    status = Column(String(16), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # relationships
    request = relationship("ExecutionRequest", back_populates="external_executions")


class VerificationTask(Base):
    __tablename__ = "verification_tasks"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("execution_requests.id"), nullable=True)
    model_url = Column(String(256), nullable=True)
    dataset = Column(String(64), nullable=True)
    metrics = Column(JSON, nullable=True)  # {accuracy: 0.92, loss: 0.15}
    audit_log = Column(JSON, nullable=True)
    status = Column(String(16), nullable=True)
    passed = Column(Boolean, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # relationships
    request = relationship("ExecutionRequest", back_populates="verification_tasks")


class SandboxProvider(Base):
    __tablename__ = "sandbox_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16), unique=True, nullable=False)
    layer = Column(String(8), nullable=False)
    is_healthy = Column(Boolean, default=True)
    last_health_check = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0)
    config = Column(JSON, nullable=True)
