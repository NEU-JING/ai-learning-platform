"""Tests for code security checker."""


class TestCodeSecurity:
    def test_safe_code_passes(self):
        from app.core.code_security import check_code_security

        is_safe, msg = check_code_security("print('hello world')")
        assert is_safe is True

    def test_os_system_blocked(self):
        from app.core.code_security import check_code_security

        is_safe, msg = check_code_security("import os\nos.system('whoami')")
        assert is_safe is False

    def test_subprocess_blocked(self):
        from app.core.code_security import check_code_security

        is_safe, msg = check_code_security("import subprocess\nsubprocess.run(['ls'])")
        assert is_safe is False

    def test_eval_blocked(self):
        from app.core.code_security import check_code_security

        is_safe, msg = check_code_security("eval('__import__(\"os\").system(\"whoami\")')")
        assert is_safe is False

    def test_exec_blocked(self):
        from app.core.code_security import check_code_security

        is_safe, msg = check_code_security("exec('import os')")
        assert is_safe is False

    def test_allowed_imports_pass(self):
        from app.core.code_security import check_code_security

        is_safe, msg = check_code_security("import math\nprint(math.sqrt(4))")
        assert is_safe is True

    def test_syntax_error_detected(self):
        from app.core.code_security import check_code_security

        is_safe, msg = check_code_security("def foo(")
        assert is_safe is False

    def test_is_safe_code_convenience(self):
        from app.core.code_security import is_safe_code

        assert is_safe_code("x = 1 + 2") is True
        assert is_safe_code("import os") is False


class TestGrader:
    def test_check_syntax_valid(self):
        from app.services.grader import CodeGrader

        ok, err = CodeGrader.check_syntax("x = 1 + 2")
        assert ok is True
        assert err is None

    def test_check_syntax_invalid(self):
        from app.services.grader import CodeGrader

        ok, err = CodeGrader.check_syntax("def foo(")
        assert ok is False
        assert err is not None

    def test_generate_feedback(self):
        from app.services.grader import CodeGrader

        test_results = [
            {"name": "test1", "passed": True, "expected": "hello", "actual": "hello"},
            {"name": "test2", "passed": False, "expected": "world", "actual": "WRONG"},
        ]
        feedback = CodeGrader.generate_feedback(test_results, 50.0)
        assert "1/2" in feedback
        assert "✅" in feedback
        assert "❌" in feedback

    def test_grader_no_exec_in_main_process(self):
        """Verify grader module has no exec() of user code in main process."""
        import inspect
        import app.services.grader as grader_module

        source = inspect.getsource(grader_module)
        # The grader should NOT contain exec(code or exec(user_code patterns
        # It may contain exec() for test infrastructure, but not exec(code
        assert "exec(code" not in source
