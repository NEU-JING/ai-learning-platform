"""
课程系统测试
"""

from app.core.database import get_db
from app.main import app
from tests.test_auth import client, override_get_db

app.dependency_overrides[get_db] = override_get_db


class TestCourses:
    """课程系统测试类"""

    def test_list_courses(self, setup_db):
        """测试获取课程列表"""
        response = client.get("/api/v1/courses/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # 应该返回内置课程
        assert len(data) > 0

    def test_get_course_detail(self, setup_db):
        """测试获取单个课程详情"""
        # 先获取列表
        list_response = client.get("/api/v1/courses/")
        courses = list_response.json()
        if len(courses) > 0:
            course_id = courses[0]["id"]
            response = client.get(f"/api/v1/courses/{course_id}")
            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            assert "chapters" in data

    def test_get_course_not_found(self, setup_db):
        """测试获取不存在的课程"""
        response = client.get("/api/v1/courses/99999")
        assert response.status_code == 404
        assert "课程不存在" in response.json()["detail"]

    def test_get_chapter_detail(self, setup_db):
        """测试获取章节详情"""
        # 先获取课程列表
        list_response = client.get("/api/v1/courses/")
        courses = list_response.json()
        if len(courses) > 0 and len(courses[0].get("chapters", [])) > 0:
            chapter_id = courses[0]["chapters"][0]["id"]
            response = client.get(f"/api/v1/courses/chapters/{chapter_id}")
            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            assert "content" in data

    def test_get_chapter_not_found(self, setup_db):
        """测试获取不存在的章节"""
        response = client.get("/api/v1/courses/chapters/99999")
        assert response.status_code == 404
        assert "章节不存在" in response.json()["detail"]

    def test_courses_structure(self, setup_db):
        """测试课程数据结构完整性"""
        response = client.get("/api/v1/courses/")
        courses = response.json()

        for course in courses:
            assert "id" in course
            assert "title" in course
            assert "description" in course
            assert "level" in course
            assert "category" in course
            assert "duration_hours" in course
            assert "chapters" in course
            assert isinstance(course["chapters"], list)

            for chapter in course["chapters"]:
                assert "id" in chapter
                assert "title" in chapter
                assert "chapter_type" in chapter
