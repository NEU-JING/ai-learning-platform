"""
Phase 1 课程数据加载器
从 JSON + Markdown 文件加载课程内容到数据库
"""

import json
from pathlib import Path

PHASE1_DIR = Path(__file__).parent / "phase1"


def load_phase1_data():
    """加载Phase 1课程数据(从JSON索引+Markdown内容文件)"""
    index_path = PHASE1_DIR / "index.json"

    with open(index_path, "r", encoding="utf-8") as f:
        course_data = json.load(f)

    # Load content from markdown files
    for chapter in course_data["chapters"]:
        content_file = chapter.pop("content_file", None)
        if content_file:
            md_path = PHASE1_DIR / content_file
            if md_path.exists():
                chapter["content"] = md_path.read_text(encoding="utf-8")
            else:
                chapter["content"] = f"# {chapter['title']}\n\n内容加载中..."

        # Load lab starter_code and test_cases from files
        lab = chapter.get("lab")
        if lab:
            starter_file = lab.pop("starter_code_file", None)
            if starter_file:
                starter_path = PHASE1_DIR / starter_file
                if starter_path.exists():
                    lab["starter_code"] = starter_path.read_text(encoding="utf-8")

            test_file = lab.pop("test_cases_file", None)
            if test_file:
                test_path = PHASE1_DIR / test_file
                if test_path.exists():
                    lab["test_cases"] = test_path.read_text(encoding="utf-8")

    return course_data


def init_phase1_data(db, behavior="upsert"):
    """Initialize Phase 1 course data from JSON files.

    BEHAVIOR: upsert (default)
      - Phase 1 JSON files are the SINGLE SOURCE OF TRUTH.
      - If course exists, deletes old chapters/labs and recreates from JSON.
      - This ensures DB always matches the authoritative JSON content.

    Use behavior="create_only" to skip if course already exists.
    """
    from app.models import Chapter, Course, Lab

    course_data = load_phase1_data()
    chapters_data = course_data.pop("chapters", [])

    # Check if course already exists
    existing = db.query(Course).filter(Course.title == course_data["title"]).first()
    if existing:
        if behavior == "create_only":
            # Skip — existing data may be better
            print("Phase 1: skipped (create_only, course exists)")
            return existing
        # upsert: update course fields and rebuild chapters
        for key, value in course_data.items():
            if key != "id":
                setattr(existing, key, value)
        db.flush()
        course = existing
        # Delete old chapters and labs
        for ch in db.query(Chapter).filter(Chapter.course_id == course.id).all():
            db.query(Lab).filter(Lab.chapter_id == ch.id).delete(synchronize_session=False)
            db.delete(ch)
        db.flush()
    else:
        course = Course(**course_data)
        db.add(course)
        db.flush()

    # Create chapters and labs
    for chapter_data in chapters_data:
        lab_data = chapter_data.pop("lab", None)

        chapter = Chapter(course_id=course.id, **chapter_data)
        db.add(chapter)
        db.flush()

        if lab_data:
            lab = Lab(chapter_id=chapter.id, **lab_data)
            db.add(lab)

    db.commit()

    chapter_count = len(chapters_data)
    lab_count = sum(
        1 for c in chapters_data if "lab" in str(c.get("chapter_type", "")) or c.get("lab")
    )
    print(f"Phase 1 loaded: {course_data['title']} ({chapter_count} chapters, {lab_count} labs)")

    return course
