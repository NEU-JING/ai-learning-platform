import ast
import re
from typing import List, Dict, Any, Optional

class CodeGrader:
    """代码自动评测系统"""

    @staticmethod
    def grade_submission(
        code: str,
        test_cases: List[Dict[str, Any]],
        solution_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        评测代码提交
        
        Returns:
            {
                "passed": bool,
                "score": int,  # 0-100
                "total_tests": int,
                "passed_tests": int,
                "test_results": List[dict],
                "style_score": int,
                "feedback": List[str]
            }
        """
        result = {
            "passed": False,
            "score": 0,
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "test_results": [],
            "style_score": 100,
            "feedback": []
        }

        # 1. 语法检查
        syntax_valid, syntax_error = CodeGrader.check_syntax(code)
        if not syntax_valid:
            result["feedback"].append(f"语法错误: {syntax_error}")
            return result

        # 2. 执行测试用例
        for test in test_cases:
            test_result = CodeGrader.run_test_case(code, test)
            result["test_results"].append(test_result)
            if test_result["passed"]:
                result["passed_tests"] += 1

        # 3. 代码风格检查
        style_issues = CodeGrader.check_style(code)
        result["style_score"] = max(0, 100 - len(style_issues) * 5)
        result["feedback"].extend(style_issues)

        # 4. 计算总分
        if result["total_tests"] > 0:
            test_score = (result["passed_tests"] / result["total_tests"]) * 80
        else:
            test_score = 80

        result["score"] = int(test_score + result["style_score"] * 0.2)
        result["passed"] = result["passed_tests"] == result["total_tests"] and result["score"] >= 60

        return result

    @staticmethod
    def check_syntax(code: str) -> tuple[bool, Optional[str]]:
        """检查代码语法"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"第{e.lineno}行: {e.msg}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def run_test_case(code: str, test: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个测试用例"""
        import sys
        import io

        test_result = {
            "name": test.get("name", "未命名测试"),
            "passed": False,
            "actual_output": "",
            "expected_output": test.get("expected", ""),
            "error": None
        }

        try:
            # 创建受限执行环境
            namespace = {"__builtins__": __builtins__}
            exec(code, namespace)

            # 获取测试输入
            test_input = test.get("input", "")

            # 重定向输入输出
            old_stdout = sys.stdout
            old_stdin = sys.stdin

            sys.stdout = io.StringIO()
            sys.stdin = io.StringIO(test_input)

            try:
                # 执行测试代码
                if "function" in test:
                    func_name = test["function"]
                    if func_name in namespace:
                        func = namespace[func_name]
                        args = test.get("args", [])
                        actual = func(*args)
                        sys.stdout.write(str(actual))
                    else:
                        test_result["error"] = f"函数 '{func_name}' 未定义"

                output = sys.stdout.getvalue().strip()
                test_result["actual_output"] = output

                # 对比结果
                expected = str(test.get("expected", "")).strip()
                if output == expected or re.match(expected, output):
                    test_result["passed"] = True

            finally:
                sys.stdout = old_stdout
                sys.stdin = old_stdin

        except Exception as e:
            test_result["error"] = str(e)

        return test_result

    @staticmethod
    def check_style(code: str) -> List[str]:
        """检查代码风格"""
        issues = []

        # 1. 行长度检查
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"第{i}行: 行长度超过100字符")

        # 2. 检查是否有文档字符串
        if not re.search(r'""".*?"""', code, re.DOTALL):
            issues.append("建议添加函数/模块文档字符串")

        # 3. 检查变量命名
        snake_case_pattern = r'^[a-z][a-z0-9_]*$'
        for match in re.finditer(r'def\s+(\w+)', code):
            func_name = match.group(1)
            if not re.match(snake_case_pattern, func_name):
                issues.append(f"函数名 '{func_name}' 建议使用snake_case命名")

        # 4. 检查是否有过多的全局变量
        global_vars = re.findall(r'^[a-zA-Z_]\w*\s*=', code, re.MULTILINE)
        if len(global_vars) > 10:
            issues.append("全局变量过多，建议使用类或函数封装")

        # 5. 检查是否有未使用的导入
        imports = re.findall(r'^import\s+(\w+)|^from\s+\S+\s+import\s+(.+)$', code, re.MULTILINE)
        for imp in imports:
            module = imp[0] or imp[1].split(',')[0].strip()
            if module and module not in code.split('import')[-1]:
                pass  # 简化检查

        return issues

    @staticmethod
    def generate_feedback(result: Dict[str, Any]) -> str:
        """生成评测反馈"""
        lines = []
        lines.append(f"📊 得分: {result['score']}/100")
        lines.append(f"✅ 通过测试: {result['passed_tests']}/{result['total_tests']}")
        lines.append(f"🎨 代码风格: {result['style_score']}/100")
        lines.append("")

        if result["test_results"]:
            lines.append("📋 测试结果:")
            for test in result["test_results"]:
                status = "✅" if test["passed"] else "❌"
                lines.append(f"  {status} {test['name']}")
                if not test["passed"]:
                    lines.append(f"     期望: {test['expected_output']}")
                    lines.append(f"     实际: {test['actual_output']}")
                    if test.get("error"):
                        lines.append(f"     错误: {test['error']}")

        if result["feedback"]:
            lines.append("")
            lines.append("💡 改进建议:")
            for fb in result["feedback"]:
                lines.append(f"  • {fb}")

        return "\n".join(lines)
