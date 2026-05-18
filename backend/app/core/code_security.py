"""
代码安全检测模块 - 检测危险代码和恶意操作
"""

import ast
import re
from typing import Any, Dict, List, Set, Tuple

# ========== 危险模式黑名单 ==========

# 禁止的模块导入
FORBIDDEN_MODULES: Set[str] = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "urllib",
    "urllib.request",
    "urllib.parse",
    "urllib.error",
    "urllib.robotparser",
    "urllib2",
    "httplib",
    "http.client",
    "http.server",
    "ftplib",
    "poplib",
    "imaplib",
    "smtplib",
    "smtpd",
    "nntplib",
    "telnetlib",
    "xmlrpc",
    "requests",
    "urllib3",
    "aiohttp",
    "httpx",
    "pycurl",
    "wget",
    "tornado",
    "twisted",
    "gevent",
    "eventlet",
    "pty",
    "tty",
    "termios",
    "fcntl",
    "select",
    "selectors",
    "signal",
    "multiprocessing",
    "concurrent.futures",
    "asyncio",
    "threading",
    "_thread",
    "dummy_threading",
    "queue",
    "pipes",
    "platform",
    "site",
    "importlib",
    "imp",
    "runpy",
    "pkgutil",
    "modulefinder",
    "zipimport",
    "zipfile",
    "tarfile",
    "shutil",
    "pathlib",
    "path",
    "glob",
    "fnmatch",
    "linecache",
    "traceback",
    "gc",
    "weakref",
    "types",
    "inspect",
    "code",
    "codeop",
    "bdb",
    "pdb",
    "trace",
    "cProfile",
    "profile",
    "pstats",
    "timeit",
    "compileall",
    "py_compile",
    "symtable",
    "parser",
    "ast",
    "tokenize",
    "token",
    "keyword",
    "dis",
    "pickle",
    "pickletools",
    "copyreg",
    "shelve",
    "dbm",
    "dbm.gnu",
    "dbm.ndbm",
    "dbm.dumb",
    "sqlite3",
    "sqlite",
    "mimetypes",
    "base64",
    "binascii",
    "quopri",
    "uu",
    "encodings",
    "codecs",
    "unicodedata",
    "stringprep",
    "readline",
    "rlcompleter",
    "crypt",
    "spwd",
    "grp",
    "pwd",
    "termios",
    "tty",
    "pty",
    "fcntl",
    "resource",
    "nis",
    "syslog",
    "getpass",
    "curses",
    "ssl",
    "hashlib",
    "hmac",
    "secrets",
    "uuid",
    "ipaddress",
    "macpath",
    "posixpath",
    "ntpath",
    "genericpath",
    "cmd",
    "shlex",
    "pipes",
    "socketserver",
    "http",
    "http.cookies",
    "http.cookiejar",
    "wsgiref",
    "cgi",
    "cgitb",
    "wsgiref",
    "webbrowser",
    "netrc",
    "mimetools",
    "rfc822",
    "basehttpserver",
    "simplehttpserver",
    "cghttpserver",
    "cookie",
    "cookielib",
    "html",
    "html.parser",
    "html.entities",
    "xml",
    "xml.etree",
    "xml.dom",
    "xml.sax",
    "xml.parsers",
    "pyexpat",
    "plistlib",
    "xdrlib",
    "msilib",
    "msvcrt",
    "winreg",
    "winsound",
    "win32api",
    "win32con",
    "ctypes",
    "ctypes.wintypes",
    "ctypes.util",
    "_ctypes",
    "mmap",
    "msvcrt",
    "winreg",
    "winsound",
    "spwd",
    "nis",
    "syslog",
    "optparse",
    "getopt",
    "fileinput",
    "calendar",
    "collections.abc",
    "contextlib",
    "abc",
    "atexit",
    "tracemalloc",
    "faulthandler",
    "warnings",
    "linecache",
    "tracemalloc",
    "reprlib",
    "enum",
    "graphlib",
    "typing",
    "dataclasses",
    "contextvars",
    "zoneinfo",
    "_threading_local",
    "sched",
    "mailcap",
    "mailbox",
    "mhlib",
    "mimetools",
    "rfc822",
    "basehttpserver",
    "simplehttpserver",
    "sunau",
    "wave",
    "chunk",
    "colorsys",
    "imghdr",
    "sndhdr",
    "ossaudiodev",
    "sunaudiodev",
    "ossaudiodev",
    "audioop",
    "imageop",
    "rgbimg",
    "jpeg",
    "cd",
    "fl",
    "fm",
    "gl",
    "imgfile",
    "sv",
    "al",
    "ml",
    "cdrom",
    "cl",
    "sgi",
    "al",
    "sunaudiodev",
}

# 禁止的函数调用
FORBIDDEN_FUNCTIONS: Set[str] = {
    "open",
    "file",
    "exec",
    "eval",
    "compile",
    "__import__",
    "input",
    "raw_input",
    "reload",
    "exit",
    "quit",
    "os.system",
    "os.popen",
    "os.popen2",
    "os.popen3",
    "os.popen4",
    "os.spawn",
    "os.spawnl",
    "os.spawnle",
    "os.spawnlp",
    "os.spawnlpe",
    "os.spawnv",
    "os.spawnve",
    "os.spawnvp",
    "os.spawnvpe",
    "os.exec",
    "os.execl",
    "os.execle",
    "os.execlp",
    "os.execlpe",
    "os.execv",
    "os.execve",
    "os.execvp",
    "os.execvpe",
    "os.fork",
    "os.forkpty",
    "os.kill",
    "os.killpg",
    "os.wait",
    "os.waitpid",
    "os.wait3",
    "os.wait4",
    "os.waitid",
    "os.remove",
    "os.unlink",
    "os.rmdir",
    "os.removedirs",
    "os.rename",
    "os.renames",
    "os.replace",
    "os.makedirs",
    "os.mkdir",
    "os.chmod",
    "os.chown",
    "os.chroot",
    "os.fchmod",
    "os.fchown",
    "os.lchmod",
    "os.lchown",
    "os.chflags",
    "os.lchflags",
    "os.mkfifo",
    "os.mknod",
    "os.link",
    "os.symlink",
    "os.readlink",
    "os.setuid",
    "os.setgid",
    "os.seteuid",
    "os.setegid",
    "os.setreuid",
    "os.setregid",
    "os.setgroups",
    "os.initgroups",
    "os.getuid",
    "os.getgid",
    "os.geteuid",
    "os.getegid",
    "os.getgroups",
    "os.getlogin",
    "os.getloadavg",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.getoutput",
    "subprocess.getstatusoutput",
    "subprocess.list2cmdline",
    "sys.exit",
    "sys._exit",
    "sys.modules",
    "sys.path",
    "sys.argv",
    "__builtins__.__import__",
    "__builtins__.open",
    "__builtins__.exec",
    "__builtins__.eval",
    "__builtins__.compile",
    "socket.socket",
    "socket.create_connection",
    "socket.getaddrinfo",
    "socket.gethostbyname",
    "socket.gethostbyaddr",
    "builtins.open",
    "builtins.exec",
    "builtins.eval",
    "builtins.compile",
    "builtins.__import__",
}

# 禁止的属性访问
FORBIDDEN_ATTRIBUTES: Set[str] = {
    "__subclasses__",
    "__bases__",
    "__base__",
    "__mro__",
    "__globals__",
    "__code__",
    "__func__",
    "__closure__",
    "__defaults__",
    "__kwdefaults__",
    "__annotations__",
    "__module__",
    "__dict__",
    "__class__",
    "__self__",
    "__weakref__",
    "__slots__",
    "__get__",
    "__set__",
    "__delete__",
    "__getattr__",
    "__getattribute__",
    "__setattr__",
    "__delattr__",
    "__getstate__",
    "__setstate__",
    "__reduce__",
    "__reduce_ex__",
    "__getinitargs__",
    "__getnewargs__",
    "__getnewargs_ex__",
    "__hash__",
    "__call__",
    "__new__",
    "__init__",
    "__del__",
    "__enter__",
    "__exit__",
    "__iter__",
    "__next__",
    "__aiter__",
    "__anext__",
    "__await__",
    "__aenter__",
    "__aexit__",
    "func_globals",
    "gi_frame",
    "gi_code",
    "gi_yieldfrom",
    "cr_frame",
    "cr_code",
    "cr_origin",
    "tb_frame",
    "tb_next",
    "f_back",
    "f_builtins",
    "f_globals",
    "f_locals",
    "f_code",
    "f_trace",
    "f_trace_lines",
    "f_trace_opcodes",
    "co_code",
    "co_names",
    "co_varnames",
    "co_freevars",
    "co_cellvars",
}

# 正则表达式危险模式
DANGEROUS_PATTERNS: List[Tuple[str, str]] = [
    # 危险导入
    (r"import\s+os\b", "禁止导入 os 模块"),
    (r"import\s+sys\b", "禁止导入 sys 模块"),
    (r"import\s+subprocess\b", "禁止导入 subprocess 模块"),
    (r"import\s+socket\b", "禁止导入 socket 模块"),
    (r"import\s+(urllib|urllib2|httplib|ftplib)\b", "禁止导入网络模块"),
    (r"import\s+requests\b", "禁止导入 requests 模块"),
    (r"from\s+os\s+import", "禁止从 os 模块导入"),
    (r"from\s+sys\s+import", "禁止从 sys 模块导入"),
    (r"from\s+subprocess\s+import", "禁止从 subprocess 导入"),
    (r"from\s+socket\s+import", "禁止从 socket 导入"),
    # 动态导入
    (r"__import__\s*\(", "禁止使用动态导入"),
    (r"importlib\.", "禁止使用 importlib"),
    # 危险函数
    (r"os\.system\s*\(", "禁止调用 os.system"),
    (r"os\.popen\s*\(", "禁止调用 os.popen"),
    (r"os\.fork\s*\(", "禁止调用 os.fork"),
    (r"os\.exec", "禁止调用 os.exec 系列函数"),
    (r"os\.kill\s*\(", "禁止调用 os.kill"),
    (r"subprocess\.call\s*\(", "禁止调用 subprocess.call"),
    (r"subprocess\.run\s*\(", "禁止调用 subprocess.run"),
    (r"subprocess\.Popen\s*\(", "禁止调用 subprocess.Popen"),
    (r"eval\s*\(", "禁止使用 eval"),
    (r"exec\s*\(", "禁止使用 exec"),
    (r"compile\s*\(", "禁止使用 compile"),
    (r"execfile\s*\(", "禁止使用 execfile"),
    # 文件操作
    (r"open\s*\(", "禁止使用 open 函数"),
    (r"file\s*\(", "禁止使用 file 函数"),
    (r"os\.remove\s*\(", "禁止删除文件"),
    (r"os\.unlink\s*\(", "禁止删除文件"),
    (r"os\.rmdir\s*\(", "禁止删除目录"),
    (r"os\.mkdir\s*\(", "禁止创建目录"),
    (r"os\.makedirs\s*\(", "禁止创建目录"),
    (r"shutil\.", "禁止使用 shutil 模块"),
    # 网络相关
    (r"urllib\.", "禁止使用 urllib"),
    (r"requests\.", "禁止使用 requests"),
    (r"socket\.", "禁止使用 socket"),
    # 系统相关
    (r"sys\.exit\s*\(", "禁止调用 sys.exit"),
    (r"sys\.modules", "禁止访问 sys.modules"),
    (r"sys\.path", "禁止访问 sys.path"),
    # 危险字符串操作
    (r"rm\s+-rf", "禁止删除命令"),
    (r"dd\s+if=", "禁止 dd 命令"),
    (r"mkfifo", "禁止创建命名管道"),
    (r"netcat", "禁止网络工具"),
    (r"nc\s+-[lL]", "禁止监听端口"),
    # 编码/加密相关
    (r"base64\.b64decode", "谨慎使用 base64"),
    (r"marshal\.loads", "禁止使用 marshal"),
    # 特殊属性访问
    (r"__subclasses__", "禁止访问 __subclasses__"),
    (r"__bases__", "禁止访问 __bases__"),
    (r"__globals__", "禁止访问 __globals__"),
    (r"__code__", "禁止访问 __code__"),
    (r"\.func_globals", "禁止访问 func_globals"),
    (r"\.gi_frame", "禁止访问生成器帧"),
    # 多线程/进程
    (r"threading\.", "禁止使用 threading"),
    (r"multiprocessing\.", "禁止使用 multiprocessing"),
    (r"asyncio\.", "谨慎使用 asyncio"),
    # 特殊输入
    (r"input\s*\(", "禁止使用 input"),
    (r"raw_input\s*\(", "禁止使用 raw_input"),
]

# 允许的模块白名单（仅这些模块可以导入）
ALLOWED_MODULES: Set[str] = {
    "math",
    "random",
    "statistics",
    "fractions",
    "decimal",
    "numbers",
    "datetime",
    "time",
    "calendar",
    "zoneinfo",
    "collections",
    "collections.abc",
    "heapq",
    "bisect",
    "array",
    "copy",
    "pprint",
    "reprlib",
    "enum",
    "graphlib",
    "dataclasses",
    "contextvars",
    "itertools",
    "functools",
    "operator",
    "pathlib",
    "os.path",
    "re",
    "string",
    "struct",
    "difflib",
    "textwrap",
    "unicodedata",
    "stringprep",
    "readline",
    "rlcompleter",
    "json",
    "csv",
    "configparser",
    "tomllib",
    "hashlib",
    "hmac",
    "secrets",
    "inspect",
    "types",
    "typing",
    "abc",
    "atexit",
    "traceback",
    "warnings",
    "contextlib",
    "dataclasses",
    "enum",
    "numpy",
    "pandas",
    "matplotlib",
    "matplotlib.pyplot",
    "sklearn",
    "scipy",
    "scipy.stats",
    "scipy.optimize",
}


class CodeSecurityChecker:
    """代码安全检测器"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def check_code(self, code: str) -> Tuple[bool, List[str], List[str]]:
        """
        检测代码安全性

        Args:
            code: 要检测的Python代码

        Returns:
            (是否安全, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []

        if not code or not code.strip():
            self.errors.append("代码为空")
            return False, self.errors, self.warnings

        # 1. 语法检查
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.errors.append(f"语法错误: {e}")
            return False, self.errors, self.warnings

        # 2. 正则表达式模式检查
        self._check_patterns(code)

        # 3. AST静态分析
        self._analyze_ast(tree)

        is_safe = len(self.errors) == 0
        return is_safe, self.errors, self.warnings

    def _check_patterns(self, code: str):
        """使用正则表达式检查危险模式"""
        for pattern, message in DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                self.errors.append(f"检测到危险模式: {message}")

    def _analyze_ast(self, tree: ast.AST):
        """AST静态分析"""
        for node in ast.walk(tree):
            # 检查导入语句
            if isinstance(node, ast.Import):
                self._check_import(node)
            elif isinstance(node, ast.ImportFrom):
                self._check_import_from(node)

            # 检查函数调用
            elif isinstance(node, ast.Call):
                self._check_call(node)

            # 检查属性访问
            elif isinstance(node, ast.Attribute):
                self._check_attribute(node)

            # 检查名称
            elif isinstance(node, ast.Name):
                self._check_name(node)

            # 检查表达式
            elif isinstance(node, ast.Expr):
                self._check_expr(node)

    def _check_import(self, node: ast.Import):
        """检查import语句"""
        for alias in node.names:
            module_name = alias.name.split(".")[0]
            if module_name in FORBIDDEN_MODULES:
                self.errors.append(f"禁止导入模块: {alias.name}")
            elif module_name not in ALLOWED_MODULES:
                self.warnings.append(f"未在白名单中的模块: {alias.name}")

    def _check_import_from(self, node: ast.ImportFrom):
        """检查from...import语句"""
        if node.module:
            module_name = node.module.split(".")[0]
            if module_name in FORBIDDEN_MODULES:
                self.errors.append(f"禁止从 {node.module} 导入")
            elif module_name not in ALLOWED_MODULES:
                self.warnings.append(f"从未白名单的模块导入: {node.module}")

            # 检查导入的具体名称
            for alias in node.names:
                if alias.name in FORBIDDEN_FUNCTIONS:
                    self.errors.append(f"禁止导入函数: {alias.name} 从 {node.module}")

    def _check_call(self, node: ast.Call):
        """检查函数调用"""
        if isinstance(node.func, ast.Name):
            # 直接函数调用
            func_name = node.func.id
            if func_name in FORBIDDEN_FUNCTIONS:
                self.errors.append(f"禁止调用函数: {func_name}")
            elif func_name in ["eval", "exec", "compile"]:
                self.errors.append(f"禁止调用危险内置函数: {func_name}")
            elif func_name == "__import__":
                self.errors.append("禁止动态导入模块")

        elif isinstance(node.func, ast.Attribute):
            # 方法调用
            attr_name = node.func.attr
            if attr_name in [
                "system",
                "popen",
                "popen2",
                "popen3",
                "popen4",
                "spawn",
                "spawnl",
                "spawnle",
                "spawnlp",
                "spawnlpe",
                "spawnv",
                "spawnve",
                "spawnvp",
                "spawnvpe",
                "exec",
                "execl",
                "execle",
                "execlp",
                "execlpe",
                "execv",
                "execve",
                "execvp",
                "execvpe",
                "fork",
                "forkpty",
                "kill",
                "killpg",
                "wait",
                "open",
            ]:
                self.errors.append(f"禁止调用危险方法: {attr_name}")

    def _check_attribute(self, node: ast.Attribute):
        """检查属性访问"""
        if node.attr in FORBIDDEN_ATTRIBUTES:
            self.errors.append(f"禁止访问特殊属性: {node.attr}")

    def _check_name(self, node: ast.Name):
        """检查名称使用"""
        # 检查是否是危险内置函数
        if node.id in ["eval", "exec", "compile"] and isinstance(node.ctx, ast.Load):
            self.errors.append(f"禁止使用内置函数: {node.id}")

    def _check_expr(self, node: ast.Expr):
        """检查表达式语句"""
        # 这里可以添加额外的表达式检查


# 便捷函数
def check_code_security(code: str) -> Tuple[bool, str]:
    """
    检查代码安全性

    Args:
        code: 要检查的Python代码

    Returns:
        (是否安全, 错误信息)
    """
    checker = CodeSecurityChecker()
    is_safe, errors, warnings = checker.check_code(code)

    if not is_safe:
        return False, f"安全检测失败: {'; '.join(errors)}"

    if warnings:
        return True, f"警告: {'; '.join(warnings)}"

    return True, ""


def is_safe_code(code: str) -> bool:
    """快速检查代码是否安全"""
    checker = CodeSecurityChecker()
    is_safe, _, _ = checker.check_code(code)
    return is_safe


def get_security_report(code: str) -> Dict[str, Any]:
    """获取完整的安全检测报告"""
    checker = CodeSecurityChecker()
    is_safe, errors, warnings = checker.check_code(code)

    return {
        "is_safe": is_safe,
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "can_execute": is_safe,
    }
