"""Employer module API routes.

AC45: GET /verify/{cert_number} — Public certificate verification HTML page
AC46: POST /api/v1/employer/verify — Digital signature verification (API Key auth)
AC48: Rate limiting middleware (in employer service)
AC49: POST /api/v1/employer/query — Authorization code query (API Key auth)
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.employer import Employer
from app.schemas.employer import AuthCodeQueryRequest, SignatureVerifyRequest
from app.services.employer import (
    get_api_key_employer,
    log_api_call,
    query_by_code,
    render_verify_page,
    verify_signature,
)

router = APIRouter()


# ── E2: AC45 — Public certificate verification HTML page ────────────────────
# This route is also registered directly on app in main.py for priority
# over the SPA catch-all.  This router registration is for /api/v1/employer prefix.


@router.get("/verify/{cert_number}")
def employer_api_verify_page(
    cert_number: str,
    db: Session = Depends(get_db),
):
    """AC45: Certificate verification via API (fallback route under /api/v1/employer)."""
    html, status_code = render_verify_page(db, cert_number)
    return HTMLResponse(content=html, status_code=status_code)


# ── E3: AC46 — Digital signature verification API ───────────────────────────


@router.post("/verify")
def employer_verify_signature(
    request: Request,
    body: SignatureVerifyRequest,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_api_key_employer),
):
    """AC46: Verify certificate authenticity via ECDSA digital signature.

    Requires X-API-Key header authentication.
    """
    t0 = time.time()

    try:
        result = verify_signature(db, body.cert_number, body.signature)
        status_code = 200 if result.get("valid") else 400
    except Exception as e:
        result = {"valid": False, "message": str(e)}
        status_code = 500

    elapsed_ms = int((time.time() - t0) * 1000)

    # AC47: Audit log
    log_api_call(
        db=db,
        employer_id=employer.id,
        endpoint="/api/v1/employer/verify",
        status_code=status_code,
        response_time_ms=elapsed_ms,
    )

    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=result.get("message", "Verification failed"))

    return result


# ── E5: AC49 — Authorization code query API ─────────────────────────────────


@router.post("/query")
def employer_query(
    request: Request,
    body: AuthCodeQueryRequest,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_api_key_employer),
):
    """AC49: Query user data using an authorization code.

    Requires X-API-Key header authentication.
    Returns only fields permitted by the verification code's permissions.
    """
    t0 = time.time()

    try:
        result = query_by_code(db, body.verification_code, body.requested_fields)
        if result.get("error"):
            status_code = 400
        else:
            status_code = 200
    except Exception as e:
        result = {"error": str(e), "user": None}
        status_code = 500

    elapsed_ms = int((time.time() - t0) * 1000)

    # AC47: Audit log
    log_api_call(
        db=db,
        employer_id=employer.id,
        endpoint="/api/v1/employer/query",
        status_code=status_code,
        response_time_ms=elapsed_ms,
    )

    if status_code >= 400:
        detail = result.get("error", "Query failed")
        raise HTTPException(status_code=status_code, detail=detail)

    return result
