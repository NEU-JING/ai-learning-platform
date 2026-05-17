"""
Phase 3-6 课程数据加载器
从 courses_extended_fixed.py 加载深化后的课程内容到数据库

BEHAVIOR: create_only (default)
  - Only creates Phase 3-6 courses if they don't already exist.
  - NEVER overwrites existing chapters/labs — DB content may have been
    manually deepened or improved beyond the seed file.
  - Only updates lightweight metadata fields (description, is_published, etc.).

  Why create_only? Phase 3-6 were deepened manually in previous sessions.
  The courses_extended_fixed.py seed file is NOT the latest version.
  Overwriting would destroy improvements.

  Use behavior="upsert" to force a full rebuild from seed file (⚠️ data loss).
"""

import sys
from pathlib import Path


def load_extended_courses():
    """Load Phase 3-6 course data from courses_extended_fixed.py"""
    # Import the extended data module
    backend_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(backend_dir))
    from app.data.courses_extended_fixed import COURSES_DATA

    return COURSES_DATA


def init_phase3_6_data(db, behavior="create_only"):
    """
    Initialize Phase 3-6 course data from courses_extended_fixed.py.

    Phase 1 and 2 are loaded separately from JSON files (higher quality content).
    This function handles Phase 3-6 which only exist in courses_extended_fixed.py.

    BEHAVIOR: create_only (default)
      - If course already exists, only update metadata (never overwrite chapters/labs).
      - If course doesn't exist, create it with full chapter/lab content.
      - This protects manually-deepened content from being overwritten.

    Key behaviors:
    - Skips Phase 1/2 (handled by init_phase1_data/init_phase2_data)
    - Always sets is_published=True
    - Invalidates cache after data changes
    """
    from app.core.cache import cache_manager
    from app.models import Chapter, Course, Lab

    all_courses = load_extended_courses()

    # Skip Phase 1/2 - they have better content from JSON files
    # courses_extended_fixed has titles like "Phase 1: Python基础与AI工具链（2周/14天）"
    # which differ from our canonical titles. Skip by checking title prefix.
    import copy

    skip_prefixes = ("Phase 1:", "Phase 2:")
    courses_to_load = []
    for c in all_courses:
        title = c.get("title", "")
        if any(title.startswith(prefix) for prefix in skip_prefixes):
            continue
        # Deep copy to prevent mutating the module-level COURSES_DATA
        # (course_data.pop("chapters") would otherwise destroy the source)
        courses_to_load.append(copy.deepcopy(c))

    updated = 0
    created = 0

    # Canonical title mapping from extended data titles to DB titles
    title_map = {
        "Phase 3: 机器学习（4周/28天）": "Phase 3: 机器学习（4周/28天）",
        "Phase 4: 深度学习（2周/14天）": "Phase 4: 深度学习（2周/14天）",
        "Phase 5: LLM大模型（3周/21天）": "Phase 5: LLM大模型（3周/21天）",
        "Phase 6: AI工程化（2周/14天）": "Phase 6: AI工程化（2周/14天）",
    }

    for course_data in courses_to_load:
        chapters_data = course_data.pop("chapters", [])

        # Force is_published=True - seed data should always be visible
        course_data["is_published"] = True

        # Find existing course by title (check both original and canonical title)
        title = course_data.get("title", "")
        canonical_title = title_map.get(title, title)
        existing = db.query(Course).filter(Course.title == canonical_title).first()

        if existing:
            # Check if course is an empty shell (0 chapters)
            existing_ch_count = db.query(Chapter).filter(Chapter.course_id == existing.id).count()

            if existing_ch_count > 0 and behavior == "create_only":
                # SKIP: Course has real content — protect it
                updated += 1
                update_fields = {
                    "description",
                    "level",
                    "category",
                    "duration_hours",
                    "is_published",
                }
                for key in update_fields:
                    if key in course_data:
                        setattr(existing, key, course_data[key])
                db.flush()
                continue
            elif existing_ch_count > 0 and behavior == "upsert":
                # Full rebuild: delete existing chapters/labs
                for ch in db.query(Chapter).filter(Chapter.course_id == existing.id).all():
                    db.query(Lab).filter(Lab.chapter_id == ch.id).delete(synchronize_session=False)
                    db.delete(ch)
                db.flush()
                course = existing
                # Fall through to chapter creation below
            else:
                # Empty shell (0 chapters): fill it with seed data
                course = existing
                updated += 1
                # Fall through to chapter creation below
        else:
            course = Course(**course_data)
            db.add(course)
            db.flush()
            created += 1

        # Create chapters and labs
        for chapter_data in chapters_data:
            lab_data = chapter_data.pop("lab", None)

            chapter = Chapter(course_id=course.id, **chapter_data)
            db.add(chapter)
            db.flush()

            if lab_data:
                # Ensure hints and test_cases are properly typed
                if "hints" in lab_data and isinstance(lab_data["hints"], str):
                    import json

                    try:
                        lab_data["hints"] = json.loads(lab_data["hints"])
                    except (json.JSONDecodeError, TypeError):
                        lab_data["hints"] = [lab_data["hints"]] if lab_data["hints"] else []
                if "test_cases" in lab_data and isinstance(lab_data["test_cases"], str):
                    import json

                    try:
                        lab_data["test_cases"] = json.loads(lab_data["test_cases"])
                    except (json.JSONDecodeError, TypeError):
                        lab_data["test_cases"] = []

                lab = Lab(chapter_id=chapter.id, **lab_data)
                db.add(lab)

        db.commit()

    # Invalidate course caches after data changes
    try:
        cache_manager.delete_pattern("courses:*")
    except Exception:
        pass  # Cache invalidation failure is non-critical

    total_chapters = sum(len(c.get("chapters", [])) for c in courses_to_load)
    total_labs = sum(
        sum(1 for ch in c.get("chapters", []) if ch.get("lab")) for c in courses_to_load
    )
    print(
        f"✅ Phase 3-6 loaded: {created} created, {updated} updated "
        f"({total_chapters} chapters, {total_labs} labs)"
    )
