"""Employer module Pydantic schemas.

AC46: Digital signature verification request/response
AC49: Authorization code query request/response
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SignatureVerifyRequest(BaseModel):
    """AC46: Digital signature verification request."""
    cert_number: str = Field(..., description="证书编号, e.g. AILP-L2-ABCD-1234")
    signature: str = Field(..., description="ECDSA base64-encoded signature")


class AuditSummary(BaseModel):
    """AC46: Audit summary in verification response."""
    completed_labs: int = 0
    avg_score: float = 0.0
    verification_count: int = 1


class CertData(BaseModel):
    """AC46: Certificate data in verification response."""
    holder: str
    level: str
    issued_at: Optional[str] = None
    expires_at: Optional[str] = None


class SignatureVerifyResponse(BaseModel):
    """AC46: Digital signature verification response."""
    valid: bool
    message: Optional[str] = None
    cert_data: Optional[CertData] = None
    audit_summary: Optional[AuditSummary] = None


class AuthCodeQueryRequest(BaseModel):
    """AC49: Authorization code query request."""
    verification_code: str = Field(..., description="8位字母数字授权码")
    requested_fields: List[str] = Field(
        default=["certifications", "skill_summary"],
        description="请求的数据字段: certifications, skill_summary, lab_history",
    )


class UserInfo(BaseModel):
    """AC49: User info in query response."""
    name: str
    username: str


class CertInfo(BaseModel):
    """AC49: Certificate info in query response."""
    cert_number: str
    level_id: int
    issue_date: Optional[str] = None
    is_valid: bool = True


class LabHistoryItem(BaseModel):
    """AC49: Lab history item in query response."""
    lab_id: int
    status: str
    score: Optional[float] = None
    created_at: Optional[str] = None


class AuthCodeQueryResponse(BaseModel):
    """AC49: Authorization code query response."""
    error: Optional[str] = None
    user: Optional[UserInfo] = None
    certifications: Optional[List[CertInfo]] = None
    skill_radar: Optional[dict] = None
    lab_history: Optional[List[LabHistoryItem]] = None
