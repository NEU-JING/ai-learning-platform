"""
Phase 2 课程数据加载器
从 JSON + Markdown 文件加载课程内容到数据库
"""
import json
from pathlib import Path

PHASE2_DIR = Path(__file__).parent / "phase2"


def load_phase2_data():
    """加载Phase 2课程数据(从JSON索引+Markdown内容文件)"""
    index_path = PHASE2_DIR / "index.json"

    with open(index_path, "r", encoding="utf-8") as f:
        course_data = json.load(f)

    # Load content from markdown files
    for chapter in course_data["chapters"]:
        content_file = chapter.pop("content_file", None)
        if content_file:
            md_path = PHASE2_DIR / content_file
            if md_path.exists():
                chapter["content"] = md_path.read_text(encoding="utf-8")
            else:
                chapter["content"] = f"# {chapter['title']}\n\n内容加载中..."

        # Load lab starter_code and test_cases from files
        if chapter.get("chapter_type") == "lab":
            starter_file = chapter.pop("starter_code_file", None)
            if starter_file:
                starter_path = PHASE2_DIR / starter_file
                if starter_path.exists():
                    chapter["starter_code"] = starter_path.read_text(encoding="utf-8")

            test_file = chapter.pop("test_cases_file", None)
            if test_file:
                test_path = PHASE2_DIR / test_file
                if test_path.exists():
                    chapter["test_cases"] = test_path.read_text(encoding="utf-8")

    return course_data


def init_phase2_data(db, behavior="upsert"):
    """Initialize Phase 2 course data from JSON files.

    BEHAVIOR: upsert (default)
      - Phase 2 JSON files are the SINGLE SOURCE OF TRUTH.
      - If course exists, deletes old chapters/labs and recreates from JSON.
      - This ensures DB always matches the authoritative JSON content.

    Use behavior="create_only" to skip if course already exists.
    """
    from app.models import Course, Chapter, Lab

    course_data = load_phase2_data()
    chapters_data = course_data.pop("chapters", [])

    # Check if course already exists
    existing = db.query(Course).filter(Course.title == course_data["title"]).first()
    if existing:
        if behavior == "create_only":
            print(f"Phase 2: skipped (create_only, course exists)")
            return existing
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
        # Extract lab-specific fields from chapter data
        lab_fields = {}
        if chapter_data.get("chapter_type") == "lab":
            for field in ["starter_code", "test_cases"]:
                if field in chapter_data:
                    lab_fields[field] = chapter_data.pop(field)
            # test_cases from file is Python code string, wrap in JSON format
            if "test_cases" in lab_fields and isinstance(lab_fields["test_cases"], str):
                lab_fields["test_cases"] = [{"type": "python", "code": lab_fields["test_cases"]}]

        chapter = Chapter(course_id=course.id, **chapter_data)
        db.add(chapter)
        db.flush()

        # Create Lab record for lab-type chapters
        if chapter_data.get("chapter_type") == "lab" and lab_fields:
            lab = Lab(
                chapter_id=chapter.id,
                title=chapter_data.get("title", "Lab"),
                description=chapter_data.get("content", "")[:500] if chapter_data.get("content") else None,
                **lab_fields
            )
            db.add(lab)

    db.commit()

    chapter_count = len(chapters_data)
    lab_count = sum(1 for c in chapters_data if c.get("chapter_type") == "lab")
    print(f"Phase 2 loaded: {course_data['title']} ({chapter_count} chapters, {lab_count} labs)")

    return course
