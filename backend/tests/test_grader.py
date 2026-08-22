"""grader 回归测试 — 修复 len(test_results) 替代 len(test_cases)。

原 bug：legacy str test_cases 下 len(test_cases) 算字符数，导致正确代码被判
极低分（如 3.8 分）+ passed=False。此测试锁定不再回归。
"""

from app.services.grader import CodeGrader


def test_legacy_str_all_passed_scores_100():
    """legacy str 断言脚本全部通过 → 100 分 + passed（防按字符数低估回归）。"""
    res = CodeGrader.grade_in_sandbox(
        "def is_even(n): return n % 2 == 0",
        "assert is_even(2) == True\nassert is_even(3) == False",
    )
    assert res["passed"] is True
    assert res["score"] == 100.0


def test_legacy_str_wrong_code_fails():
    """错误代码 → 未通过。"""
    res = CodeGrader.grade_in_sandbox(
        "def is_even(n): return False",
        "assert is_even(2) == True",
    )
    assert res["passed"] is False


def test_legacy_str_single_assert():
    """单条断言也能正确计分（不因字符数被低估）。"""
    res = CodeGrader.grade_in_sandbox(
        "def double(n): return n * 2",
        "assert double(4) == 8",
    )
    assert res["passed"] is True
    assert res["score"] == 100.0