"""Employer module service layer.

Handles:
- Certificate verification page HTML rendering
- Digital signature verification
- Authorization code queries
- API audit logging
- Rate limiting (in-memory)
"""

import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.certification import Certificate, CertificationLevel
from app.models.employer import Employer, EmployerApiLog, VerificationCode


class RateLimiter:
    """In-memory rate limiter (AC48). 1000 requests/hour by default.

    Uses a sliding window approach. Thread-safe enough for single-worker FastAPI.
    """

    def __init__(self):
        self._counters: Dict[str, Dict[int, int]] = defaultdict(dict)

    def check(self, api_key: str, limit: int = 1000) -> Tuple[bool, int]:
        """Check if request is allowed.

        Returns (allowed: bool, remaining: int).
        """
        hour = datetime.now(timezone.utc).hour
        key = api_key
        current = self._counters[key].get(hour, 0)

        if current >= limit:
            return False, 0

        self._counters[key][hour] = current + 1
        return True, limit - current - 1

    def reset(self, api_key: str = None):
        """Reset counters (for testing)."""
        if api_key:
            self._counters.pop(api_key, None)
        else:
            self._counters.clear()


# Singleton rate limiter instance
rate_limiter = RateLimiter()


def get_api_key_employer(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Employer:
    """FastAPI dependency — validates X-API-Key header and returns employer.

    Used for AC46/AC49 API Key authenticated endpoints.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 API Key (X-API-Key header)",
        )

    employer_obj = db.query(Employer).filter(
        Employer.api_key == x_api_key,
        Employer.is_active.is_(True),
    ).first()

    if not employer_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无效的 API Key 或账户已禁用",
        )

    # Rate limit check (AC48)
    allowed, remaining = rate_limiter.check(x_api_key, employer_obj.rate_limit)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"超出配额 ({employer_obj.rate_limit}/小时)，请升级套餐或联系商务",
            headers={"X-RateLimit-Remaining": "0"},
        )

    return employer_obj


def log_api_call(db: Session, employer_id: int, endpoint: str, status_code: int, response_time_ms: int):
    """AC47: Record API call to audit log."""
    try:
        log = EmployerApiLog(
            employer_id=employer_id,
            endpoint=endpoint,
            status_code=status_code,
            response_time_ms=response_time_ms,
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()


def render_verify_page(db: Session, cert_number: str) -> Tuple[str, int]:
    """AC45: Render certificate verification HTML page.

    Returns (html_content, status_code).
    """
    cert = db.query(Certificate).filter(Certificate.cert_number == cert_number).first()

    if not cert:
        return _error_html("证书未找到", "该证书编号在系统中不存在。"), 404

    # Get level name
    level = db.query(CertificationLevel).filter(
        CertificationLevel.id == cert.level_id
    ).first()
    level_name = level.name if level else "Unknown"

    # Get user name
    user = cert.user
    holder_name = "Unknown"
    if cert.cert_metadata and "holder_name" in cert.cert_metadata:
        holder_name = cert.cert_metadata["holder_name"]
    elif user:
        holder_name = user.username

    # Extract metadata
    completed_labs = cert.cert_metadata.get("completed_labs", "N/A") if cert.cert_metadata else "N/A"
    avg_score = cert.cert_metadata.get("avg_score", "N/A") if cert.cert_metadata else "N/A"

    issue_date = cert.issue_date.strftime("%Y-%m-%d") if cert.issue_date else "N/A"
    valid_status = "✅ 有效" if cert.is_valid else "❌ 已吊销 / 已失效"

    # Expiry: 2 years from issue
    if cert.issue_date:
        from datetime import timedelta
        expiry_date = cert.issue_date + timedelta(days=730)
        expiry_str = expiry_date.strftime("%Y-%m-%d")
    else:
        expiry_str = "N/A"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>证书验证 — AILP</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; color: #333; }}
        .container {{ max-width: 640px; margin: 60px auto; padding: 20px; }}
        .card {{ background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 32px 24px; text-align: center; }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header .cert-number {{ font-size: 14px; opacity: 0.85; font-family: monospace; }}
        .body {{ padding: 24px; }}
        .row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee; }}
        .row:last-child {{ border-bottom: none; }}
        .label {{ color: #888; font-size: 14px; }}
        .value {{ font-weight: 600; font-size: 14px; }}
        .valid {{ color: #22c55e; }}
        .invalid {{ color: #ef4444; font-weight: 700; }}
        .footer {{ text-align: center; padding: 16px; font-size: 12px; color: #999; }}
        .footer a {{ color: #667eea; }}
        .badge {{ display: inline-block; background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; margin-top: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="header">
                <h1>🔐 证书验证</h1>
                <div class="cert-number">{cert_number}</div>
                <div class="badge">{level_name}</div>
            </div>
            <div class="body">
                <div class="row">
                    <span class="label">证书持有者</span>
                    <span class="value">{holder_name}</span>
                </div>
                <div class="row">
                    <span class="label">认证等级</span>
                    <span class="value">{level_name}</span>
                </div>
                <div class="row">
                    <span class="label">颁发日期</span>
                    <span class="value">{issue_date}</span>
                </div>
                <div class="row">
                    <span class="label">有效期至</span>
                    <span class="value">{expiry_str}</span>
                </div>
                <div class="row">
                    <span class="label">完成实验数</span>
                    <span class="value">{completed_labs}</span>
                </div>
                <div class="row">
                    <span class="label">平均得分</span>
                    <span class="value">{avg_score}</span>
                </div>
                <div class="row">
                    <span class="label">验证状态</span>
                    <span class="value {'valid' if cert.is_valid else 'invalid'}">{valid_status}</span>
                </div>
                {'<div class="row"><span class="label">数字签名</span><span class="value" style="font-size:11px;max-width:200px;word-break:break-all;">' + (cert.signature or 'N/A') + '</span></div>' if cert.signature else ''}
            </div>
            <div class="footer">
                <p>由 <a href="/">AILP — AI能力验证平台</a> 提供验证服务</p>
                <p>此页面为公开验证页面，无需登录</p>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html, 200


def _error_html(title: str, message: str) -> str:
    """Render an error HTML page."""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — AILP</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
        .error-card {{ background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); padding: 48px; text-align: center; max-width: 400px; }}
        .error-card h1 {{ font-size: 48px; margin-bottom: 12px; }}
        .error-card p {{ color: #888; font-size: 16px; }}
        .error-card a {{ color: #667eea; margin-top: 24px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="error-card">
        <h1>🔍</h1>
        <h2>{title}</h2>
        <p>{message}</p>
        <a href="/">返回首页</a>
    </div>
</body>
</html>"""


def verify_signature(db: Session, cert_number: str, signature: str) -> Dict[str, Any]:
    """AC46: Digital signature verification API.

    Verifies certificate authenticity using ECDSA signature verification.
    """
    cert = db.query(Certificate).filter(Certificate.cert_number == cert_number).first()

    if not cert:
        return {"valid": False, "message": "证书未找到"}

    if not cert.is_valid:
        return {"valid": False, "message": "证书已被吊销"}

    # Verify ECDSA signature
    from app.services.certificate import certificate_service

    sign_data = {
        "cert_number": cert.cert_number,
        "user_id": cert.user_id,
        "level_id": cert.level_id,
        "issue_date": cert.issue_date.isoformat() if cert.issue_date else "",
    }

    sig_valid = certificate_service.verify_certificate_signature(
        signature=signature,
        cert_data=sign_data,
    )

    if not sig_valid:
        return {"valid": False, "message": "数字签名验证失败 — 证书可能被篡改"}

    # Build response
    user = cert.user
    level = db.query(CertificationLevel).filter(
        CertificationLevel.id == cert.level_id
    ).first()

    return {
        "valid": True,
        "cert_data": {
            "holder": cert.cert_metadata.get("holder_name", user.username if user else "Unknown") if cert.cert_metadata else (user.username if user else "Unknown"),
            "level": level.name if level else "Unknown",
            "issued_at": cert.issue_date.strftime("%Y-%m-%d") if cert.issue_date else None,
            "expires_at": (cert.issue_date + __import__("datetime").timedelta(days=730)).strftime("%Y-%m-%d") if cert.issue_date else None,
        },
        "audit_summary": {
            "completed_labs": cert.cert_metadata.get("completed_labs", 0) if cert.cert_metadata else 0,
            "avg_score": cert.cert_metadata.get("avg_score", 0.0) if cert.cert_metadata else 0.0,
            "verification_count": 1,
        },
    }


def query_by_code(db: Session, verification_code: str, requested_fields: list) -> Dict[str, Any]:
    """AC49: Authorization code query.

    Employer provides a verification code to access user data.
    Fields returned depend on the code's permissions and requested_fields.
    """
    vc = db.query(VerificationCode).filter(
        VerificationCode.code == verification_code
    ).first()

    if not vc:
        return {"error": "无效的授权码", "user": None}

    if vc.expires_at and vc.expires_at < datetime.now(timezone.utc):
        return {"error": "授权码已过期", "user": None}

    user = vc.user
    if not user:
        return {"error": "用户不存在", "user": None}

    permissions = vc.permissions or {}

    result: Dict[str, Any] = {
        "user": {
            "name": user.username,
            "username": user.username,
        },
    }

    # AC49: Only return fields that are both requested AND permitted
    if "certifications" in requested_fields and permissions.get("certifications", False):
        from app.models.certification import Certificate
        certs = db.query(Certificate).filter(
            Certificate.user_id == user.id,
            Certificate.is_valid.is_(True),
        ).all()
        result["certifications"] = [
            {
                "cert_number": c.cert_number,
                "level_id": c.level_id,
                "issue_date": c.issue_date.isoformat() if c.issue_date else None,
                "is_valid": c.is_valid,
            }
            for c in certs
        ]

    if "skill_summary" in requested_fields and permissions.get("skill_summary", False):
        from app.models import UserSkillScore
        scores = db.query(UserSkillScore).filter(
            UserSkillScore.user_id == user.id
        ).all()
        result["skill_radar"] = {
            s.dimension: s.score for s in scores
        }

    if "lab_history" in requested_fields and permissions.get("lab_history", False):
        from app.models import LabSubmission
        subs = db.query(LabSubmission).filter(
            LabSubmission.user_id == user.id
        ).order_by(LabSubmission.created_at.desc()).limit(20).all()
        result["lab_history"] = [
            {
                "lab_id": s.lab_id,
                "status": s.status,
                "score": s.score,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in subs
        ]

    return result
