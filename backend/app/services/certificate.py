from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.services.templates import CERTIFICATE_TEMPLATE


class CertificateService:
    """学习证书服务"""

    @staticmethod
    def generate_certificate(db: Session, user_id: int, course_id: int) -> Optional[Dict[str, Any]]:
        """
        生成课程完成证书

        Returns:
            {
                "cert_id": str,
                "html": str,
                "verified": bool,
                "signature": str | None,
            }
        """
        from app.models import Chapter, Course

        # 获取用户和课程信息
        user = CertificateService._get_user(db, user_id)
        if not user:
            return None

        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None

        # 检查是否完成所有章节
        chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
        chapter_ids = [c.id for c in chapters]
        if not chapter_ids:
            return None

        completion = CertificateService._check_course_completion(
            db, user_id, chapter_ids, len(chapters)
        )
        if not completion["complete"]:
            return {
                "verified": False,
                "message": f"课程未完成 ({completion['completed_count']}/{len(chapters)} 章节)",
                "progress_percentage": completion["progress_percentage"],
            }

        # 生成证书 payload
        cert_id, html, level_badge = CertificateService._build_cert_payload(user, course)
        issue_date_iso = datetime.now(timezone.utc).isoformat()

        # T19: ECDSA signing — ensure cert level and sign
        level = CertificateService._ensure_cert_level(db, level_badge, course.title)

        sign_data = {
            "cert_number": cert_id,
            "user_id": user_id,
            "level_id": level.id,
            "issue_date": issue_date_iso,
        }
        signature = CertificateService.sign_certificate(sign_data)

        # Persist certificate record
        certificate = CertificateService._create_cert_db_record(
            db, user_id, level.id, cert_id, course, level_badge, signature
        )

        return CertificateService._format_api_response(
            cert_id, html, user_id, course, issue_date_iso, signature, certificate.id
        )

    @staticmethod
    def _get_user(db: Session, user_id: int):
        from app.models import User

        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def _check_course_completion(
        db: Session, user_id: int, chapter_ids: list, total_chapters: int
    ) -> dict:
        from app.models import LearningProgress

        completed_count = (
            db.query(LearningProgress)
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.chapter_id.in_(chapter_ids),
                LearningProgress.status == "completed",
            )
            .count()
        )
        return {
            "complete": completed_count >= total_chapters,
            "completed_count": completed_count,
            "progress_percentage": round(completed_count / total_chapters * 100, 2),
        }

    @staticmethod
    def _build_cert_payload(user, course) -> tuple:
        """Build cert_id, html, and level_badge for a completed course.

        Returns (cert_id, html, level_badge).
        """
        cert_id = f"AI-{course.id}-{user.id}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

        level_badges = {
            "beginner": "入门认证",
            "intermediate": "进阶认证",
            "advanced": "高级认证",
            "expert": "专家认证",
        }
        level_badge = level_badges.get(course.level, "学习认证")

        html = CERTIFICATE_TEMPLATE.format(
            username=user.username or user.email.split("@")[0],
            course_title=course.title,
            level_badge=level_badge,
            issue_date=datetime.now(timezone.utc).strftime("%Y年%m月%d日"),
            cert_id=cert_id,
        )

        return cert_id, html, level_badge

    @staticmethod
    def _ensure_cert_level(db: Session, level_badge: str, course_title: str):
        """Find or create a CertificationLevel matching the given badge name."""
        from app.models.certification import CertificationLevel

        level = (
            db.query(CertificationLevel)
            .filter(
                CertificationLevel.name == level_badge,
                CertificationLevel.is_active.is_(True),
            )
            .first()
        )
        if not level:
            level = CertificationLevel(
                name=level_badge,
                description=f"Auto-created for {course_title}",
                required_courses=[],
                min_average_score=70.0,
                order=1,
                is_active=True,
            )
            db.add(level)
            db.flush()

        return level

    @staticmethod
    def _create_cert_db_record(
        db: Session,
        user_id: int,
        level_id: int,
        cert_id: str,
        course,
        level_badge: str,
        signature: str,
    ):
        """Create and persist a Certificate database record."""
        from app.models.certification import Certificate

        certificate = Certificate(
            user_id=user_id,
            level_id=level_id,
            cert_number=cert_id,
            issue_date=datetime.now(timezone.utc),
            cert_metadata={
                "course_id": course.id,
                "course_title": course.title,
                "level": course.level,
                "level_badge": level_badge,
            },
            signature=signature,
            is_valid=True,
        )
        db.add(certificate)
        db.commit()
        db.refresh(certificate)
        return certificate

    @staticmethod
    def _format_api_response(
        cert_id: str,
        html: str,
        user_id: int,
        course,
        issue_date_iso: str,
        signature: str,
        cert_db_id: int,
    ) -> Dict[str, Any]:
        """Format the certificate generation API response dict."""
        return {
            "cert_id": cert_id,
            "html": html,
            "verified": True,
            "user_id": user_id,
            "course_id": course.id,
            "course_title": course.title,
            "issue_date": issue_date_iso,
            "level": course.level,
            "signature": signature,
            "certificate_id": cert_db_id,
        }

    @staticmethod
    def verify_certificate(cert_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """验证证书真伪 — with ECDSA signature verification.

        When db is provided, performs full ECDSA signature verification
        against the stored certificate record.
        """
        try:
            # 解析证书ID
            parts = cert_id.split("-")
            if len(parts) != 4 or parts[0] != "AI":
                return {"valid": False, "message": "无效的证书编号格式"}

            result = {
                "valid": True,
                "cert_id": cert_id,
                "course_id": parts[1],
                "user_id": parts[2],
                "issue_date": parts[3],
                "message": "证书ID格式有效",
                "signature_verified": None,
            }

            # ── T19: ECDSA signature verification ────────────────────────
            if db is not None:
                cert_record = CertificateService._find_certificate(db, cert_id)

                if cert_record is None:
                    result["valid"] = False
                    result["message"] = "证书未在系统中找到"
                    result["signature_verified"] = False
                    return result

                if not cert_record.is_valid:
                    result["valid"] = False
                    result["message"] = "证书已被吊销"
                    result["signature_verified"] = False
                    return result

                sig_valid, sig_msg = CertificateService._validate_signature(cert_record)
                result["signature_verified"] = sig_valid
                if not sig_valid:
                    result["valid"] = False
                    result["message"] = sig_msg

            return result
        except Exception as e:
            return {"valid": False, "message": str(e), "signature_verified": False}

    @staticmethod
    def _find_certificate(db: Session, cert_id: str):
        """Look up a Certificate by cert_number; returns the record or None."""
        from app.models.certification import Certificate

        return db.query(Certificate).filter(Certificate.cert_number == cert_id).first()

    @staticmethod
    def _validate_signature(cert_record) -> tuple:
        """Verify the ECDSA signature on a certificate record.

        Returns (is_valid: bool, message: str).
        """
        if not cert_record.signature or not cert_record.cert_metadata:
            return False, "ECDSA 签名验证失败 — 证书可能被篡改"

        sign_data = {
            "cert_number": cert_record.cert_number,
            "user_id": cert_record.user_id,
            "level_id": cert_record.level_id,
            "issue_date": (cert_record.issue_date.isoformat() if cert_record.issue_date else ""),
        }
        sig_valid = CertificateService.verify_certificate_signature(
            signature=cert_record.signature,
            cert_data=sign_data,
        )
        if sig_valid:
            return True, ""
        return False, "ECDSA 签名验证失败 — 证书可能被篡改"

    # ── T19: ECDSA Certificate Signature ──────────────────────────────────

    _signing_key = None  # Module-level cache for the persistent signing key

    @classmethod
    def _get_signing_key(cls):
        """Load or generate the ECDSA SECP256r1 private key.

        Loads the key from ECDSA_PRIVATE_KEY_PATH if it exists;
        otherwise generates a new key and persists it to disk.
        Returns (private_key, key_bytes_pem).
        """
        import os

        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec

        if cls._signing_key is not None:
            return cls._signing_key

        from app.core.config import settings

        key_path = settings.ECDSA_PRIVATE_KEY_PATH

        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                pem_data = f.read()
            private_key = serialization.load_pem_private_key(pem_data, password=None)
        else:
            private_key = ec.generate_private_key(ec.SECP256R1())
            pem_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            os.makedirs(os.path.dirname(key_path) or ".", exist_ok=True)
            with open(key_path, "wb") as f:
                f.write(pem_data)

        cls._signing_key = private_key
        return private_key

    @staticmethod
    def _serialize_public_key(private_key) -> str:
        """Export the public key as a PEM string for distribution."""
        from cryptography.hazmat.primitives import serialization

        public_key = private_key.public_key()
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    @classmethod
    def sign_certificate(cls, cert_data: Dict[str, Any]) -> str:
        """AC37: Sign certificate data with ECDSA-SHA256.

        Builds a canonical message from cert_number, user_id, level_id,
        and issue_date, then signs it with the persistent SECP256r1 key.

        Returns a base64-encoded DER signature string.
        """
        import base64

        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec

        private_key = cls._get_signing_key()

        # Build canonical signing payload
        payload = (
            f"cert_number:{cert_data['cert_number']}|"
            f"user_id:{cert_data['user_id']}|"
            f"level_id:{cert_data['level_id']}|"
            f"issue_date:{cert_data['issue_date']}"
        )

        signature_der = private_key.sign(
            payload.encode("utf-8"),
            ec.ECDSA(hashes.SHA256()),
        )

        return base64.b64encode(signature_der).decode("ascii")

    @classmethod
    def verify_certificate_signature(
        cls,
        signature: str,
        cert_data: Dict[str, Any],
    ) -> bool:
        """AC37: Verify an ECDSA-SHA256 certificate signature.

        Reconstructs the canonical payload and verifies the signature
        against the persistent public key.

        Returns True if valid, False if tampered or invalid.
        """
        import base64

        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec

        private_key = cls._get_signing_key()
        public_key = private_key.public_key()

        payload = (
            f"cert_number:{cert_data['cert_number']}|"
            f"user_id:{cert_data['user_id']}|"
            f"level_id:{cert_data['level_id']}|"
            f"issue_date:{cert_data['issue_date']}"
        )

        try:
            signature_der = base64.b64decode(signature)
            public_key.verify(signature_der, payload.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
            return True
        except (InvalidSignature, Exception):
            return False

    @staticmethod
    def auto_evaluate_l1(db: Session, user_id: int, level_id: int) -> Dict[str, Any]:
        """T17: L1 自动评定 — AC30.

        检查必修课程完成情况 + 平均分阈值。
        通过则自动创建 certification_application 记录（status="approved"）。
        """
        from app.models.certification import CertificationLevel

        # 1. 获取认证级别
        level = db.query(CertificationLevel).filter(CertificationLevel.id == level_id).first()
        if not level:
            return {"status": "error", "reason": "Certification level not found"}

        required_course_ids = level.required_courses or []

        # Edge case: no required courses → trivially approved
        if not required_course_ids:
            return CertificateService._create_trivial_approval(db, user_id, level_id)

        # 2. 逐课程检查完成度和得分
        course_details, all_completed, total_weighted_score, total_score_count = (
            CertificateService._evaluate_required_courses(db, user_id, required_course_ids)
        )

        # 3. 计算总体平均分
        avg_score = (
            round(total_weighted_score / total_score_count, 2) if total_score_count > 0 else 0.0
        )

        # 4. 判定并创建 application record
        return CertificateService._create_evaluation_result(
            db,
            user_id,
            level_id,
            level.min_average_score,
            course_details,
            all_completed,
            avg_score,
        )

    @staticmethod
    def _create_trivial_approval(db: Session, user_id: int, level_id: int) -> Dict[str, Any]:
        """Create auto-approved application when level has no required courses."""
        from app.models.certification import CertificationApplication

        application = CertificationApplication(
            user_id=user_id,
            level_id=level_id,
            status="approved",
            evaluation_data={
                "avg_score": 0.0,
                "all_completed": True,
                "course_details": [],
            },
            evaluator_notes="Auto-approved: no required courses",
        )
        db.add(application)
        db.commit()
        return {
            "status": "approved",
            "all_completed": True,
            "avg_score": 0.0,
            "course_details": [],
            "application_id": application.id,
        }

    @staticmethod
    def _evaluate_required_courses(db: Session, user_id: int, required_course_ids: list):
        """Check completion and scores for all required courses.

        Returns (course_details, all_completed, total_weighted_score, total_score_count).
        """
        course_details = []
        all_completed = True
        total_weighted_score = 0.0
        total_score_count = 0

        for course_id in required_course_ids:
            cd, completed, w_score, s_count = CertificateService._evaluate_single_course(
                db, user_id, course_id
            )
            course_details.append(cd)
            if not completed:
                all_completed = False
            total_weighted_score += w_score
            total_score_count += s_count

        return course_details, all_completed, total_weighted_score, total_score_count

    @staticmethod
    def _evaluate_single_course(db: Session, user_id: int, course_id: int):
        """Evaluate a single course: check chapter completion and compute average score.

        Returns (course_detail_dict, is_completed, weighted_score_sum, score_count).
        """
        from app.models import Chapter

        chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
        chapter_ids = [ch.id for ch in chapters]

        if not chapter_ids:
            return (
                {
                    "course_id": course_id,
                    "completed": True,
                    "total_chapters": 0,
                    "completed_chapters": 0,
                    "avg_course_score": None,
                },
                True,
                0.0,
                0,
            )

        completed_count, course_completed = CertificateService._check_course_completion(
            db, user_id, chapter_ids, len(chapters)
        )
        course_score, w_score, s_count = CertificateService._calc_course_score(
            db, user_id, chapter_ids
        )

        return (
            {
                "course_id": course_id,
                "completed": course_completed,
                "total_chapters": len(chapters),
                "completed_chapters": completed_count,
                "avg_course_score": (round(course_score, 2) if course_score is not None else None),
            },
            course_completed,
            w_score,
            s_count,
        )

    @staticmethod
    def _check_course_completion(db: Session, user_id: int, chapter_ids: list, total_chapters: int):
        """Count completed chapters and determine if course is completed.

        Returns (completed_count: int, course_completed: bool).
        """
        from app.models import LearningProgress

        completed_count = (
            db.query(LearningProgress)
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.chapter_id.in_(chapter_ids),
                LearningProgress.status == "completed",
            )
            .count()
        )
        return completed_count, completed_count >= total_chapters

    @staticmethod
    def _calc_course_score(db: Session, user_id: int, chapter_ids: list):
        """Calculate the average course score from lab submissions.

        Returns (course_score: float | None, weighted_score_sum: float, score_count: int).
        """
        from app.models import Lab, LabSubmission

        labs = db.query(Lab).filter(Lab.chapter_id.in_(chapter_ids)).all()
        lab_ids = [lab.id for lab in labs]

        if not lab_ids:
            return None, 0.0, 0

        submissions = (
            db.query(LabSubmission)
            .filter(
                LabSubmission.user_id == user_id,
                LabSubmission.lab_id.in_(lab_ids),
                LabSubmission.score.isnot(None),
            )
            .all()
        )
        if not submissions:
            return None, 0.0, 0

        scores = [s.score for s in submissions if s.score is not None]
        if not scores:
            return None, 0.0, 0

        return sum(scores) / len(scores), sum(scores), len(scores)

    @staticmethod
    def _create_evaluation_result(
        db: Session,
        user_id: int,
        level_id: int,
        min_average_score: float,
        course_details: list,
        all_completed: bool,
        avg_score: float,
    ) -> Dict[str, Any]:
        """Create certification application and return evaluation result."""
        # Not all courses completed
        if not all_completed:
            return CertificateService._handle_incomplete_result(
                db, user_id, level_id, avg_score, course_details
            )

        # Average score below threshold
        if avg_score < min_average_score:
            return CertificateService._handle_low_score_result(
                db, user_id, level_id, avg_score, min_average_score, course_details
            )

        # Auto-approve
        return CertificateService._handle_auto_approve_result(
            db, user_id, level_id, avg_score, course_details
        )

    @staticmethod
    def _handle_incomplete_result(
        db: Session,
        user_id: int,
        level_id: int,
        avg_score: float,
        course_details: list,
    ) -> Dict[str, Any]:
        """Handle rejection due to incomplete courses."""
        from app.models.certification import CertificationApplication

        application = CertificationApplication(
            user_id=user_id,
            level_id=level_id,
            status="rejected",
            evaluation_data={
                "avg_score": avg_score,
                "all_completed": False,
                "course_details": course_details,
            },
            evaluator_notes="Auto-evaluated: not all required courses completed",
        )
        db.add(application)
        db.commit()
        completed_count = sum(1 for c in course_details if c["completed"])
        return {
            "status": "failed",
            "all_completed": False,
            "avg_score": avg_score,
            "course_details": course_details,
            "reason": (
                f"Not all required courses completed "
                f"({completed_count}/{len(course_details)} courses completed)"
            ),
            "application_id": application.id,
        }

    @staticmethod
    def _handle_low_score_result(
        db: Session,
        user_id: int,
        level_id: int,
        avg_score: float,
        min_average_score: float,
        course_details: list,
    ) -> Dict[str, Any]:
        """Handle rejection due to average score below threshold."""
        from app.models.certification import CertificationApplication

        application = CertificationApplication(
            user_id=user_id,
            level_id=level_id,
            status="rejected",
            evaluation_data={
                "avg_score": avg_score,
                "all_completed": True,
                "course_details": course_details,
            },
            evaluator_notes=(
                f"Auto-evaluated: average score {avg_score} " f"below threshold {min_average_score}"
            ),
        )
        db.add(application)
        db.commit()
        return {
            "status": "failed",
            "all_completed": True,
            "avg_score": avg_score,
            "course_details": course_details,
            "reason": (
                f"Average score {avg_score} below required " f"threshold {min_average_score}"
            ),
            "application_id": application.id,
        }

    @staticmethod
    def _handle_auto_approve_result(
        db: Session,
        user_id: int,
        level_id: int,
        avg_score: float,
        course_details: list,
    ) -> Dict[str, Any]:
        """Handle auto-approval when all conditions are met."""
        from app.models.certification import CertificationApplication

        application = CertificationApplication(
            user_id=user_id,
            level_id=level_id,
            status="approved",
            evaluation_data={
                "avg_score": avg_score,
                "all_completed": True,
                "course_details": course_details,
            },
            evaluator_notes="Auto-approved: all courses completed and score threshold met",
        )
        db.add(application)
        db.commit()
        return {
            "status": "approved",
            "all_completed": True,
            "avg_score": avg_score,
            "course_details": course_details,
            "application_id": application.id,
        }

    # ── T18: L2 Capstone Review ────────────────────────────────────────────

    @staticmethod
    def submit_capstone(
        db: Session,
        user_id: int,
        level_id: int,
        title: str,
        description: Optional[str] = None,
        repository_url: Optional[str] = None,
        submission_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """AC31: Submit a capstone project for L2 certification review.

        Creates a CapstoneSubmission record with status='submitted'.
        Then triggers AI review automatically.

        Returns submission dict.
        Raises ValueError on invalid input.
        """
        from app.models.certification import CapstoneSubmission, CertificationLevel

        # Validation
        if not title or not title.strip():
            raise ValueError("title is required")

        level = db.query(CertificationLevel).filter(CertificationLevel.id == level_id).first()
        if not level:
            raise ValueError(f"Certification level {level_id} not found")

        submission = CapstoneSubmission(
            user_id=user_id,
            level_id=level_id,
            title=title.strip(),
            description=description,
            repository_url=repository_url,
            submission_data=submission_data or {},
            status="submitted",
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        return {
            "id": submission.id,
            "user_id": submission.user_id,
            "level_id": submission.level_id,
            "title": submission.title,
            "description": submission.description,
            "repository_url": submission.repository_url,
            "submission_data": submission.submission_data,
            "status": submission.status,
            "created_at": submission.created_at.isoformat() if submission.created_at else None,
        }

    @staticmethod
    def ai_review_capstone(db: Session, submission_id: int) -> Dict[str, Any]:
        """AC31: AI初审 — automatic analysis of capstone submission quality.

        Analyzes submission content, description, and repository for:
        - quality_score (0-100): code/implementation quality
        - complexity_score (0-100): technical complexity
        - completeness_score (0-100): how complete the submission is
        - summary: brief review summary

        Sets submission status to 'reviewed' after analysis.
        If already reviewed, returns existing review.
        """
        from app.models.certification import CapstoneSubmission

        submission = (
            db.query(CapstoneSubmission).filter(CapstoneSubmission.id == submission_id).first()
        )
        if not submission:
            raise ValueError(f"Capstone submission {submission_id} not found")

        # If already reviewed, return existing
        if submission.ai_review:
            return {
                "status": "reviewed",
                "submission_id": submission.id,
                "ai_review": submission.ai_review,
            }

        # AI analysis based on submission content
        ai_review = CertificateService._analyze_capstone(submission)

        submission.ai_review = ai_review
        submission.status = "reviewed"
        db.commit()
        db.refresh(submission)

        return {
            "status": "reviewed",
            "submission_id": submission.id,
            "ai_review": ai_review,
        }

    @staticmethod
    def _analyze_capstone(submission: Any) -> Dict[str, Any]:
        """Internal: analyze capstone submission without LLM dependency.

        Uses heuristics based on:
        - Description length and detail → quality indicator
        - Repository URL presence → completeness indicator
        - submission_data richness → complexity indicator
        """
        quality_score = 50
        complexity_score = 50
        completeness_score = 50

        # Quality heuristic: description detail
        if submission.description:
            desc_len = len(submission.description)
            if desc_len > 500:
                quality_score = 90
            elif desc_len > 200:
                quality_score = 80
            elif desc_len > 100:
                quality_score = 70
            elif desc_len > 50:
                quality_score = 60

        # Completeness heuristic: repository URL + submission data
        if submission.repository_url:
            completeness_score += 20
        if submission.submission_data:
            data_keys = len(submission.submission_data) if submission.submission_data else 0
            completeness_score += min(data_keys * 10, 30)
        completeness_score = min(completeness_score, 100)

        # Complexity heuristic: submission_data richness
        if submission.submission_data:
            if isinstance(submission.submission_data, dict):
                complexity_score = min(50 + len(submission.submission_data) * 10, 100)
                # Bonus for known frameworks
                frameworks = submission.submission_data.get("framework", "")
                if frameworks and frameworks.lower() in ("pytorch", "tensorflow", "jax"):
                    complexity_score = min(complexity_score + 10, 100)

        total_score = round((quality_score + completeness_score + complexity_score) / 3, 1)

        return {
            "quality_score": quality_score,
            "complexity_score": complexity_score,
            "completeness_score": completeness_score,
            "overall_score": total_score,
            "summary": (
                f"Quality: {quality_score}/100, Complexity: {complexity_score}/100, "
                f"Completeness: {completeness_score}/100. Overall: {total_score}/100"
            ),
        }

    @staticmethod
    def approve_capstone(
        db: Session,
        submission_id: int,
        reviewer_id: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """AC31: 人工抽检 — reviewer approves a capstone submission.

        Sets status='approved' and records reviewer info.
        """
        from app.models.certification import CapstoneSubmission

        submission = (
            db.query(CapstoneSubmission).filter(CapstoneSubmission.id == submission_id).first()
        )
        if not submission:
            raise ValueError(f"Capstone submission {submission_id} not found")

        if submission.status == "approved":
            raise ValueError("Submission has already been approved")

        submission.status = "approved"
        submission.reviewer_id = reviewer_id
        submission.reviewer_notes = notes
        db.commit()
        db.refresh(submission)

        return {
            "status": "approved",
            "submission_id": submission.id,
            "reviewer_id": submission.reviewer_id,
            "reviewer_notes": submission.reviewer_notes,
        }

    @staticmethod
    def reject_capstone(
        db: Session,
        submission_id: int,
        reviewer_id: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """AC31: 人工抽检 — reviewer rejects a capstone submission.

        Sets status='rejected' and records reviewer info.
        """
        from app.models.certification import CapstoneSubmission

        submission = (
            db.query(CapstoneSubmission).filter(CapstoneSubmission.id == submission_id).first()
        )
        if not submission:
            raise ValueError(f"Capstone submission {submission_id} not found")

        if submission.status == "approved":
            raise ValueError("Submission has already been approved")

        submission.status = "rejected"
        submission.reviewer_id = reviewer_id
        submission.reviewer_notes = notes
        db.commit()
        db.refresh(submission)

        return {
            "status": "rejected",
            "submission_id": submission.id,
            "reviewer_id": submission.reviewer_id,
            "reviewer_notes": submission.reviewer_notes,
        }


certificate_service = CertificateService()
