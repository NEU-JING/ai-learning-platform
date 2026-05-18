"""
单元测试：Phase 1/2 种子数据加载器的内容选择逻辑

覆盖场景：
- JSON inline content 比 .md 更长 → 保留 JSON
- .md 比 JSON 更长 → 使用 .md
- 两者都为空 → 占位符
- 内容仅有空白 → 正确比较 strip 后的长度
- 前导 \\n 被正确 strip
"""

import json
from pathlib import Path

import pytest

from app.data.courses_phase1 import PHASE1_DIR, load_phase1_data
from app.data.courses_phase2 import PHASE2_DIR, load_phase2_data


class TestContentSelection:
    """验证内容优先级逻辑：JSON inline > .md > placeholder"""

    def test_phase1_loads_real_data(self):
        """Phase 1 从真实数据文件加载（端到端验证）"""
        if not (PHASE1_DIR / "index.json").exists():
            pytest.skip("Phase 1 数据文件不存在")
        data = load_phase1_data()
        chapters = data["chapters"]
        assert len(chapters) >= 10
        for ch in chapters:
            # 2. 前导换行被 strip
            assert not ch["content"].startswith("\n"), f"Chapter {ch.get('id')} has leading newline"
            # 3. 内容不为空
            assert ch["content"].strip(), f"Chapter {ch.get('id')} has empty content"

    def test_phase2_loads_real_data(self):
        """Phase 2 从真实数据文件加载（端到端验证）"""
        if not (PHASE2_DIR / "index.json").exists():
            pytest.skip("Phase 2 数据文件不存在")
        data = load_phase2_data()
        chapters = data["chapters"]
        assert len(chapters) >= 10
        for ch in chapters:
            assert not ch["content"].startswith("\n"), f"Chapter {ch.get('id')} has leading newline"
            assert ch["content"].strip(), f"Chapter {ch.get('id')} has empty content"

    @pytest.fixture
    def tmp_phase_dir(self, tmp_path, monkeypatch):
        """创建临时 Phase 目录，模拟 phase1/phase2 结构"""
        phase_dir = tmp_path / "phase"
        phase_dir.mkdir()
        return phase_dir

    def _make_index(self, phase_dir, chapters):
        """写入 index.json"""
        index_path = phase_dir / "index.json"
        data = {"course_name": "test", "description": "test", "chapters": chapters}
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return index_path

    def _make_md(self, phase_dir, filename, content):
        """写入 .md 文件"""
        md_path = phase_dir / filename
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(content, encoding="utf-8")
        return md_path

    def test_json_richer_than_md_keeps_json(self, tmp_phase_dir, monkeypatch):
        """JSON inline 内容比 .md 更长 → 保留 JSON"""
        chapters = [
            {
                "id": 1,
                "title": "Test Chapter",
                "content": "# Rich JSON content\n\n" * 10,  # ~200 chars
                "content_file": "ch01.md",
            }
        ]
        self._make_index(tmp_phase_dir, chapters)
        self._make_md(tmp_phase_dir, "ch01.md", "# Short md\n")  # ~12 chars

        monkeypatch.chdir(tmp_phase_dir)
        # Monkeypatch the module-level directory
        with monkeypatch.context() as m:
            from app.data import courses_phase1

            m.setattr(courses_phase1, "PHASE1_DIR", tmp_phase_dir)

            data = courses_phase1.load_phase1_data()
            ch = data["chapters"][0]
            assert ch["content"].startswith("# Rich JSON"), "Should keep JSON"
            assert not ch["content"].startswith("# Short"), "Should NOT use .md"
            assert not ch["content"].startswith("\n"), "Should strip leading newline"

    def test_md_richer_than_json_uses_md(self, tmp_phase_dir, monkeypatch):
        """.md 内容比 JSON 更长 → 使用 .md"""
        chapters = [
            {
                "id": 2,
                "title": "MD Better",
                "content": "# Short JSON\n",
                "content_file": "ch02.md",
            }
        ]
        self._make_index(tmp_phase_dir, chapters)
        self._make_md(tmp_phase_dir, "ch02.md", "# Rich markdown\n\n" * 20)  # ~300 chars

        with monkeypatch.context() as m:
            from app.data import courses_phase1

            m.setattr(courses_phase1, "PHASE1_DIR", tmp_phase_dir)

            data = courses_phase1.load_phase1_data()
            ch = data["chapters"][0]
            assert ch["content"].startswith("# Rich markdown"), "Should use .md"
            assert not ch["content"].startswith("\n"), "Should strip leading newline"

    def test_both_empty_uses_placeholder(self, tmp_phase_dir, monkeypatch):
        """JSON 和 .md 都无实质内容 → 占位符"""
        chapters = [
            {
                "id": 3,
                "title": "Empty Chapter",
                "content": "",
                "content_file": "ch03.md",
            }
        ]
        self._make_index(tmp_phase_dir, chapters)
        # .md file doesn't exist → content_file.pop causes fallback to placeholder

        with monkeypatch.context() as m:
            from app.data import courses_phase1

            m.setattr(courses_phase1, "PHASE1_DIR", tmp_phase_dir)

            data = courses_phase1.load_phase1_data()
            ch = data["chapters"][0]
            assert "内容加载中" in ch["content"], "Should use placeholder"
            assert not ch["content"].startswith("\n"), "Should strip leading newline"

    def test_whitespace_only_json_vs_md(self, tmp_phase_dir, monkeypatch):
        """JSON 仅有空白 vs .md 有内容 → 用 .md"""
        chapters = [
            {
                "id": 4,
                "title": "Whitespace JSON",
                "content": "   \n  \n  ",  # 仅有空白
                "content_file": "ch04.md",
            }
        ]
        self._make_index(tmp_phase_dir, chapters)
        self._make_md(tmp_phase_dir, "ch04.md", "# Real content from md\n")

        with monkeypatch.context() as m:
            from app.data import courses_phase1

            m.setattr(courses_phase1, "PHASE1_DIR", tmp_phase_dir)

            data = courses_phase1.load_phase1_data()
            ch = data["chapters"][0]
            assert "Real content" in ch["content"], "Should use .md over whitespace JSON"

    def test_no_content_file_keeps_inline(self, tmp_phase_dir, monkeypatch):
        """没有 content_file 字段 → 直接使用 JSON inline 内容"""
        chapters = [
            {
                "id": 5,
                "title": "Inline Only",
                "content": "\n\n\n# Inline content only\n",
            }
        ]
        self._make_index(tmp_phase_dir, chapters)

        with monkeypatch.context() as m:
            from app.data import courses_phase1

            m.setattr(courses_phase1, "PHASE1_DIR", tmp_phase_dir)

            data = courses_phase1.load_phase1_data()
            ch = data["chapters"][0]
            assert "Inline content" in ch["content"]
            assert not ch["content"].startswith("\n"), "Should strip leading newlines"
