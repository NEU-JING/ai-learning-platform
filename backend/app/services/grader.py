"""Code grading system — sandbox-based evaluation.

CRITICAL: Never exec() user code in the main process. All test execution
happens inside the Docker sandbox via code_executor.
"""

import ast
import json
from typing import Any, Dict, List, Optional

from app.services.code_executor import execute_code_docker


class CodeGrader:
    """Grade user code submissions inside the sandbox."""

    @staticmethod
    def grade_in_sandbox(
        code: str,
        test_cases,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Execute grading inside the Docker sandbox.

        Supports two test_cases formats:
        - List[Dict]: structured test cases (new format)
        - str: Python script that runs asserts (legacy format)

        Returns:
            {
                "passed": bool,
                "score": float,       # 0-100
                "test_results": list, # per-test details
                "feedback": str,      # human-readable summary
            }
        """
        # 1. Syntax check (cheap, can run locally)
        syntax_ok, syntax_err = CodeGrader.check_syntax(code)
        if not syntax_ok:
            return {
                "passed": False,
                "score": 0.0,
                "test_results": [],
                "feedback": f"语法错误: {syntax_err}",
            }

        if not test_cases:
            return {
                "passed": True,
                "score": 100.0,
                "test_results": [],
                "feedback": "无测试用例，自动通过。",
            }

        # 2. Build grading script — dispatch by test_cases format
        if isinstance(test_cases, str):
            grading_code = CodeGrader._build_legacy_grading_script(code, test_cases)
        else:
            grading_code = CodeGrader._build_grading_script(code, test_cases)

        # 3. Execute in sandbox (always with security check)
        import asyncio

        try:
            result = asyncio.get_event_loop().run_until_complete(
                execute_code_docker(grading_code, timeout=timeout)
            )
        except RuntimeError:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                execute_code_docker(grading_code, timeout=timeout)
            )  # noqa: E501
            loop.close()

        if not result.get("success"):
            return {
                "passed": False,
                "score": 0.0,
                "test_results": [],
                "feedback": f"评测执行失败: {result.get('error', '未知错误')}",
            }

        # 4. Parse structured output from sandbox
        test_results = CodeGrader._parse_results(result.get("output", ""))
        if test_results is None:
            return {
                "passed": False,
                "score": 0.0,
                "test_results": [],
                "feedback": "评测输出格式异常，无法解析结果。",
            }

        # 5. Compute score
        passed_count = sum(1 for t in test_results if t.get("passed"))
        total = len(test_cases)
        score = round((passed_count / total) * 100, 1) if total > 0 else 0.0
        passed = passed_count == total and score >= 60

        # 6. Generate feedback
        feedback = CodeGrader.generate_feedback(test_results, score)

        return {
            "passed": passed,
            "score": score,
            "test_results": test_results,
            "feedback": feedback,
        }

    @staticmethod
    def check_syntax(code: str) -> tuple[bool, Optional[str]]:
        """Check code syntax via ast.parse — safe to run locally."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"行{e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def generate_feedback(test_results: list, score: float) -> str:
        """Generate human-readable grading feedback."""
        passed = sum(1 for t in test_results if t.get("passed"))
        total = len(test_results)
        lines = [f"测试通过: {passed}/{total}"]

        for t in test_results:
            icon = "✅" if t.get("passed") else "❌"
            name = t.get("name", "未命名")
            lines.append(
                f"  {icon} {name}: 期望 '{t.get('expected', '')}', 实际 '{t.get('actual', 'N/A')}'"
            )  # noqa: E501

        if score >= 80:
            lines.append("评测通过！")
        elif score >= 60:
            lines.append("部分通过，继续加油。")
        else:
            lines.append("未通过，请检查代码逻辑。")

        return "\n".join(lines)

    # ── Private helpers ────────────────────────────────────

    @staticmethod
    def _build_grading_script(user_code: str, test_cases: List[Dict]) -> str:
        """Build a self-contained Python script that runs tests and prints JSON results."""
        test_cases_json = json.dumps(test_cases, ensure_ascii=False)

        return f"""{user_code}

import json as _json

_results = []
for _i, _test in enumerate({test_cases_json}):
    _name = _test.get("name", f"test_{{_i}}")
    _ttype = _test.get("type", "output_match")
    _expected = str(_test.get("expected", ""))
    _actual = ""
    _passed = False
    _error = None
    try:
        if _ttype == "output_match":
            _func = _test.get("function")
            _args = _test.get("args", [])
            if _func:
                _fn = eval(_func)
                _raw = _fn(*_args)
                _actual = str(_raw)
            else:
                # capture print output
                import io, sys as _sys
                _old = _sys.stdout
                _buf = io.StringIO()
                _sys.stdout = _buf
                try:
                    exec(_test.get("call", ""))
                finally:
                    _sys.stdout = _old
                _actual = _buf.getvalue().strip()
            _passed = _actual == _expected
        elif _ttype == "exception":
            _func = _test.get("function")
            _args = _test.get("args", [])
            try:
                _fn = eval(_func)
                _fn(*_args)
                _actual = "no exception"
            except Exception as _e:
                _actual = type(_e).__name__
                _passed = _actual == _expected
    except Exception as _e:
        _error = str(_e)
        _actual = f"ERROR: {{type(_e).__name__}}"

    _results.append(
        {{"name": _name, "passed": _passed,
          "expected": _expected, "actual": _actual,
          "error": _error}})

print("===GRADING_RESULT_START===")
print(_json.dumps(_results, ensure_ascii=False))
print("===GRADING_RESULT_END===")
"""

    @staticmethod
    def _parse_results(output: str) -> Optional[List[Dict]]:
        """Extract test results JSON from sandbox output.

        Looks for ===GRADING_RESULT_START=== / ===GRADING_RESULT_END=== markers.
        In subprocess fallback mode, the output is wrapped in another layer of
        ===RESULT_START=== markers, so we search inside the inner output string.
        """
        marker_start = "===GRADING_RESULT_START==="
        marker_end = "===GRADING_RESULT_END==="

        idx_start = output.find(marker_start)
        idx_end = output.find(marker_end)

        if idx_start == -1 or idx_end == -1 or idx_end <= idx_start:
            return None

        json_str = output[idx_start + len(marker_start) : idx_end].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _build_legacy_grading_script(user_code: str, test_script: str) -> str:
        """Build grading script for legacy test_cases format (Python assert script).

        The test_script contains import/assert statements. We wrap it to catch
        assertion errors and report structured results.
        """
        # Escape the test script for safe embedding

        return f"""{user_code}

import json as _json
import traceback as _tb

_results = []
_test_lines = {repr(test_script.strip().split(chr(10)))}

for _i, _line in enumerate(_test_lines):
    _line = _line.strip()
    if (not _line or _line.startswith('#')
            or _line.startswith('import ')
            or _line.startswith('from ')):
        continue
    _passed = False
    _error = None
    try:
        exec(_line, globals())
        _passed = True
    except AssertionError as _e:
        _error = str(_e) or "AssertionError"
    except Exception as _e:
        _error = f"{{type(_e).__name__}}: {{_e}}"
    _name = f"line_{{_i}}: {{_line[:40]}}"
    _results.append(
        {{"name": _name, "passed": _passed,
          "expected": "assert ok",
          "actual": "ok" if _passed else "failed",
          "error": _error}})

print("===GRADING_RESULT_START===")
print(_json.dumps(_results, ensure_ascii=False))
print("===GRADING_RESULT_END===")
"""
