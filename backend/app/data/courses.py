"""
课程种子数据 - AI学习平台6阶段课程体系

⚠️ IMPORTANT: This file is the SINGLE SOURCE OF TRUTH for seed course titles.
  - Phase 1/2 are loaded from JSON files (phase1/, phase2/) which have BETTER content
  - Phase 3-6 are loaded from courses_extended_fixed.py which has the deepened content
  - This file only defines the 6-phase COURSE SHELLS (title + metadata) for deduplication

The old 4-course data (Python for AI, LangChain, AI Agent, AI Leadership) has been removed.
Those titles were inconsistent with our 6-phase system and caused duplicate courses.

BEHAVIOR: create_only — only creates course shells if they don't exist.
  Never overwrites existing data (DB content may have been manually improved).
  Cleans up orphan courses that don't belong to the 6-phase system.
"""

# Seed behavior constants
BEHAVIOR_CREATE_ONLY = "create_only"  # Only create if not exists; skip existing
BEHAVIOR_UPSERT = "upsert"  # Delete-and-recreate; seed file is source of truth

# Course titles used for deduplication - must match phase1/index.json, phase2/index.json,
# and courses_extended_fixed.py exactly
PHASE_TITLES = {
    1: "Phase 1: Python快速通道",
    2: "Phase 2: AI数学直觉",
    3: "Phase 3: 机器学习（4周/28天）",
    4: "Phase 4: 深度学习（2周/14天）",
    5: "Phase 5: LLM大模型（3周/21天）",
    6: "Phase 6: AI工程化（2周/14天）",
}


def init_courses_data(db, behavior=BEHAVIOR_CREATE_ONLY):
    """
    Initialize course shells for the 6-phase system.

    BEHAVIOR: create_only (default)
      - Only creates course shells if they don't already exist.
      - Never overwrites chapters/labs (DB content may be manually improved).
      - Cleans up orphan courses that don't belong to the 6-phase system.

    Use behavior=BEHAVIOR_UPSERT to force a full reset (⚠️ destroys manual edits).
    """
    from app.models import Course

    created = 0
    for phase_num, title in PHASE_TITLES.items():
        existing = db.query(Course).filter(Course.title == title).first()
        if not existing:
            level_map = {
                1: "beginner",
                2: "beginner",
                3: "intermediate",
                4: "advanced",
                5: "advanced",
                6: "expert",
            }
            category_map = {1: "python", 2: "math", 3: "ml", 4: "dl", 5: "llm", 6: "engineering"}
            duration_map = {1: 28, 2: 14, 3: 56, 4: 28, 5: 42, 6: 28}

            course = Course(
                title=title,
                description=f"Phase {phase_num} course content",
                level=level_map[phase_num],
                category=category_map[phase_num],
                duration_hours=duration_map[phase_num],
                order_index=phase_num,
                is_published=True,
            )
            db.add(course)
            created += 1
        elif behavior == BEHAVIOR_UPSERT:
            # Full refresh: update metadata
            existing.is_published = True
            existing.order_index = phase_num

    db.commit()

    # 🧹 CLEANUP: Remove any courses that don't belong to our 6-phase system
    valid_titles = set(PHASE_TITLES.values())
    orphans = db.query(Course).filter(Course.title.notin_(valid_titles)).all()
    if orphans:
        from app.models import Chapter, Lab, LabSubmission, LearningProgress

        for orphan in orphans:
            chapters = db.query(Chapter).filter(Chapter.course_id == orphan.id).all()
            for ch in chapters:
                db.query(LabSubmission).filter(
                    LabSubmission.lab_id.in_(db.query(Lab.id).filter(Lab.chapter_id == ch.id))
                ).delete(synchronize_session=False)
                db.query(Lab).filter(Lab.chapter_id == ch.id).delete(synchronize_session=False)
                db.query(LearningProgress).filter(LearningProgress.chapter_id == ch.id).delete(
                    synchronize_session=False
                )
            db.query(Chapter).filter(Chapter.course_id == orphan.id).delete(
                synchronize_session=False
            )
            db.delete(orphan)
        db.commit()
        print(f"🧹 Cleaned up {len(orphans)} orphan courses: {[o.title for o in orphans]}")

    if created:
        print(f"✅ Created {created} course shells for 6-phase system")
    else:
        print("✅ All 6-phase courses already exist")
