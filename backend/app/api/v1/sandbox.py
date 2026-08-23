"""Sandbox API v1 — mixed execution sandbox (Layer A/B/C)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models import User
from app.schemas.sandbox import (
    CompleteRequest,
    CompleteResponse,
    ExecuteRequest,
    ExecuteResponse,
    ExecuteResult,
    ExternalSubmitRequest,
    ExternalSubmitResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.services.sandbox import SandboxService

router = APIRouter()


# ── S2: Layer A — Local execution (AC38) ──────────────────────────────────────


@router.post("/execute", response_model=ExecuteResponse)
def sandbox_execute(
    req: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC38: Execute code in Layer A (local subprocess)."""
    try:
        result = SandboxService.execute_layer_a(
            db=db,
            user=current_user,
            lab_id=req.lab_id,
            code=req.code,
            language=req.language,
        )
        response = ExecuteResponse(
            execution_id=result["execution_id"],
            status=result["status"],
            result=(ExecuteResult(**result["result"]) if result.get("result") else None),
            score=result.get("score"),
            passed=result.get("passed"),
            feedback=result.get("feedback"),
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}",
        )


# ── S3: Layer B — External resource submission (AC39) ─────────────────────────


@router.post("/external/submit", response_model=ExternalSubmitResponse)
def sandbox_external_submit(
    req: ExternalSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC39: Submit to external resource (Kaggle/Colab/AutoDL)."""
    try:
        result = SandboxService.submit_external(
            db=db,
            user=current_user,
            lab_id=req.lab_id,
            provider=req.provider,
            notebook_url=req.notebook_url,
            expected_output=req.expected_output,
        )
        return ExternalSubmitResponse(
            submission_id=result["submission_id"],
            status=result["status"],
            estimated_wait=result.get("estimated_wait"),
            webhook_url=result.get("webhook_url"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"External submission failed: {str(e)}",
        )


# ── S4: Layer C — Verification engine (AC40-AC41) ────────────────────────────


@router.post("/verify", response_model=VerifyResponse)
def sandbox_verify(
    req: VerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC40-AC41: Verify model artifacts."""
    try:
        result = SandboxService.verify_model(
            db=db,
            execution_request_id=req.execution_request_id,
            model_url=req.model_url,
            training_log=req.training_log,
            lab_id=req.lab_id,
        )
        return VerifyResponse(
            verification_id=result["verification_id"],
            status=result["status"],
            metrics=result.get("metrics"),
            audit=result.get("audit"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )


# ── S5: Hybrid flow completion (AC42) ────────────────────────────────────────


@router.post("/complete", response_model=CompleteResponse)
def sandbox_complete(
    req: CompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AC42: Mark hybrid flow (Layer A+B+C) as complete."""
    try:
        result = SandboxService.complete_hybrid_flow(
            db=db,
            execution_request_id=req.execution_request_id,
            layers_completed=req.layers_completed,
            final_status=req.final_status,
        )
        return CompleteResponse(
            status=result["status"],
            message=result["message"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Complete failed: {str(e)}",
        )


# ── S6: Provider health check ─────────────────────────────────────────────────


@router.get("/providers")
def sandbox_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all sandbox providers with health status."""
    return SandboxService.get_providers(db)
