#!/usr/bin/env python3
"""
沙箱代码执行器 - 在隔离容器中安全执行Python代码
"""
import sys
import io
import os
import json
import resource
import signal
import traceback
import contextlib
from typing import Dict, Any

# ========== 配置常量 ==========
MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB 输出限制
MAX_EXECUTION_TIME = 30  # 默认30秒超时
MAX_MEMORY_MB = 256  # 256MB 内存限制
ALLOWED_MODULES = {
    'math', 'random', 'datetime', 'collections', 'itertools', 'functools',
    'statistics', 'fractions', 'decimal', 'typing', 'inspect', 'hashlib',
    'string', 're', 'json', 'copy', 'pprint', 'time', 'calendar',
    'numpy', 'pandas', 'matplotlib', 'matplotlib.pyplot',
    'sklearn', 'scipy'
}

FORBIDDEN_BUILTINS = {
    'open', 'file', 'exec', 'eval', 'compile', '__import__',
    'input', 'raw_input', 'reload', 'exit', 'quit'
}

FORBIDDEN_MODULES = {
    'os', 'sys', 'subprocess', 'socket', 'urllib', 'urllib2',
    'httplib', 'ftplib', 'poplib', 'imaplib', 'smtplib',
    'requests', 'wget', 'curl', 'pty', 'tty', 'signal',
    'multiprocessing', 'threading', 'asyncio', 'concurrent',
    'ssl'  # hashlib is allowed (needed for crypto exercises)
}

# ========== 安全限制 ==========
def set_resource_limits():
    """设置进程资源限制"""
    # CPU时间限制（软限制和硬限制）
    resource.setrlimit(resource.RLIMIT_CPU, (MAX_EXECUTION_TIME, MAX_EXECUTION_TIME + 1))
    
    # 内存限制 (字节)
    max_memory_bytes = MAX_MEMORY_MB * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
    
    # 文件大小限制 (1MB)
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_SIZE, MAX_OUTPUT_SIZE))
    
    # 进程数限制 (禁止fork)
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    
    # 打开文件数限制
    resource.setrlimit(resource.RLIMIT_NOFILE, (10, 10))


class TimeoutException(Exception):
    """执行超时异常"""
    pass


def timeout_handler(signum, frame):
    """信号处理函数 - 超时"""
    raise TimeoutException("代码执行超时")


class SecureEnvironment:
    """安全执行环境"""
    
    def __init__(self):
        self.output_buffer = io.StringIO()
        self.error_buffer = io.StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def __enter__(self):
        """进入安全环境"""
        sys.stdout = self.output_buffer
        sys.stderr = self.error_buffer
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出安全环境"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        return False
    
    def get_output(self) -> str:
        """获取标准输出"""
        output = self.output_buffer.getvalue()
        if len(output) > MAX_OUTPUT_SIZE:
            output = output[:MAX_OUTPUT_SIZE] + "\n[输出已截断 - 超过1MB限制]"
        return output
    
    def get_error(self) -> str:
        """获取标准错误"""
        error = self.error_buffer.getvalue()
        if len(error) > MAX_OUTPUT_SIZE:
            error = error[:MAX_OUTPUT_SIZE] + "\n[错误输出已截断 - 超过1MB限制]"
        return error


class RestrictedImport:
    """受限的import机制"""
    
    def __init__(self, real_import):
        self.real_import = real_import
    
    def __call__(self, name, *args, **kwargs):
        # 检查模块名是否在允许列表中
        base_module = name.split('.')[0]
        
        if base_module in FORBIDDEN_MODULES:
            raise ImportError(f"导入模块 '{name}' 被禁止。不允许导入系统级模块。")
        
        # 只允许白名单中的模块
        if base_module not in ALLOWED_MODULES:
            raise ImportError(f"导入模块 '{name}' 不在允许的模块列表中。允许的模块: {sorted(ALLOWED_MODULES)}")
        
        return self.real_import(name, *args, **kwargs)


def create_restricted_globals() -> Dict[str, Any]:
    """创建受限的全局命名空间"""
    # 基础安全内置函数
    safe_builtins = {
        'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
        'bin': bin, 'bool': bool, 'bytearray': bytearray, 'bytes': bytes,
        'chr': chr, 'complex': complex, 'dict': dict, 'dir': dir,
        'divmod': divmod, 'enumerate': enumerate, 'filter': filter,
        'float': float, 'format': format, 'frozenset': frozenset,
        'hasattr': hasattr, 'hash': hash, 'hex': hex, 'id': id,
        'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
        'iter': iter, 'len': len, 'list': list, 'map': map,
        'max': max, 'min': min, 'next': next, 'oct': oct,
        'ord': ord, 'pow': pow, 'print': print, 'range': range,
        'repr': repr, 'reversed': reversed, 'round': round,
        'set': set, 'slice': slice, 'sorted': sorted, 'str': str,
        'sum': sum, 'tuple': tuple, 'type': type, 'vars': vars,
        'zip': zip, 'True': True, 'False': False, 'None': None,
        'Exception': Exception, 'BaseException': BaseException,
        'ArithmeticError': ArithmeticError, 'AssertionError': AssertionError,
        'AttributeError': AttributeError, 'IndexError': IndexError,
        'KeyError': KeyError, 'LookupError': LookupError,
        'NameError': NameError, 'RuntimeError': RuntimeError,
        'StopIteration': StopIteration, 'TypeError': TypeError,
        'ValueError': ValueError, 'ZeroDivisionError': ZeroDivisionError,
        'OverflowError': OverflowError, 'MemoryError': MemoryError,
        'RecursionError': RecursionError, 'IOError': IOError,
    }
    
    # 移除危险内置函数
    restricted_globals = {
        '__builtins__': safe_builtins,
        '__import__': RestrictedImport(__import__),
        'print': print,
    }
    
    return restricted_globals


def check_code_safety(code: str) -> tuple[bool, str]:
    """
    静态检查代码安全性
    返回: (是否安全, 错误信息)
    """
    import ast
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    
    class SafetyChecker(ast.NodeVisitor):
        def __init__(self):
            self.errors = []
            self.defined_names = set()
        
        def visit_Import(self, node):
            for alias in node.names:
                base = alias.name.split('.')[0]
                if base in FORBIDDEN_MODULES:
                    self.errors.append(f"禁止导入模块: {alias.name}")
            self.generic_visit(node)
        
        def visit_ImportFrom(self, node):
            if node.module:
                base = node.module.split('.')[0]
                if base in FORBIDDEN_MODULES:
                    self.errors.append(f"禁止从 {node.module} 导入")
            self.generic_visit(node)
        
        def visit_Call(self, node):
            # 检查危险函数调用
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_BUILTINS:
                    self.errors.append(f"禁止调用函数: {node.func.id}")
                elif node.func.id == '__import__':
                    self.errors.append("禁止动态导入模块")
            
            # 检查属性访问调用 (如 os.system)
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in ['system', 'popen', 'fork', 'exec', 'execve', 'kill']:
                    self.errors.append(f"禁止调用危险方法: {node.func.attr}")
            
            self.generic_visit(node)
        
        def visit_Attribute(self, node):
            # 检查危险属性访问
            dangerous_attrs = ['__subclasses__', '__bases__', '__globals__', 
                             '__code__', '__func__', '__closure__']
            if isinstance(node.attr, str) and node.attr in dangerous_attrs:
                self.errors.append(f"禁止访问属性: {node.attr}")
            self.generic_visit(node)
        
        def visit_Name(self, node):
            # 记录定义的名称
            if isinstance(node.ctx, ast.Store):
                self.defined_names.add(node.id)
            self.generic_visit(node)
        
        def visit_Exec(self, node):
            self.errors.append("禁止使用 exec 语句")
            self.generic_visit(node)
    
    checker = SafetyChecker()
    checker.visit(tree)
    
    if checker.errors:
        return False, "安全检查失败: " + "; ".join(checker.errors)
    
    return True, ""


def execute_code(code: str, timeout: int = MAX_EXECUTION_TIME) -> Dict[str, Any]:
    """
    执行Python代码
    
    Args:
        code: 要执行的Python代码
        timeout: 超时时间（秒）
    
    Returns:
        执行结果字典
    """
    result = {
        'success': False,
        'output': '',
        'error': None,
        'execution_time_ms': 0
    }
    
    # 1. 静态安全检查
    is_safe, error_msg = check_code_safety(code)
    if not is_safe:
        result['error'] = error_msg
        return result
    
    # 2. 设置资源限制
    try:
        set_resource_limits()
    except Exception as e:
        result['error'] = f"资源限制设置失败: {e}"
        return result
    
    # 3. 设置超时信号
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    start_time = time.time() if 'time' in globals() else 0
    
    try:
        import time as time_module
        start_time = time_module.time()
        
        # 创建受限执行环境
        restricted_globals = create_restricted_globals()
        
        with SecureEnvironment() as env:
            try:
                # 执行代码
                exec(code, restricted_globals)
                
                execution_time = (time_module.time() - start_time) * 1000
                
                result['success'] = True
                result['output'] = env.get_output()
                result['execution_time_ms'] = round(execution_time, 2)
                
            except TimeoutException:
                execution_time = (time_module.time() - start_time) * 1000
                result['error'] = f"代码执行超时（超过{timeout}秒）"
                result['execution_time_ms'] = round(execution_time, 2)
                
            except MemoryError:
                execution_time = (time_module.time() - start_time) * 1000
                result['error'] = "内存不足 - 代码使用了过多内存"
                result['execution_time_ms'] = round(execution_time, 2)
                
            except Exception as e:
                execution_time = (time_module.time() - start_time) * 1000
                error_msg = f"{type(e).__name__}: {str(e)}"
                result['error'] = error_msg
                result['output'] = env.get_output()
                result['execution_time_ms'] = round(execution_time, 2)
                
    except Exception as e:
        result['error'] = f"执行环境错误: {str(e)}"
        
    finally:
        # 取消超时
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    
    return result


def main():
    """主函数 - 从stdin读取代码并执行"""
    try:
        # 从stdin读取JSON输入
        input_data = sys.stdin.read()
        
        if not input_data.strip():
            # 如果没有输入，读取环境变量
            code = os.environ.get('SANDBOX_CODE', '')
            timeout = int(os.environ.get('SANDBOX_TIMEOUT', MAX_EXECUTION_TIME))
        else:
            try:
                data = json.loads(input_data)
                code = data.get('code', '')
                timeout = data.get('timeout', MAX_EXECUTION_TIME)
            except json.JSONDecodeError:
                # 如果不是JSON，当作原始代码处理
                code = input_data
                timeout = MAX_EXECUTION_TIME
        
        if not code.strip():
            print(json.dumps({
                'success': False,
                'output': '',
                'error': '没有提供代码',
                'execution_time_ms': 0
            }))
            sys.exit(1)
        
        # 执行代码
        result = execute_code(code, timeout)
        
        # 输出JSON结果
        print(json.dumps(result))
        sys.exit(0 if result['success'] else 1)
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'output': '',
            'error': f'沙箱执行器错误: {str(e)}',
            'execution_time_ms': 0
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
