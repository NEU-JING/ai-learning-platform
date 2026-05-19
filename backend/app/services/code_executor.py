"""
代码执行服务 - 使用Docker沙箱安全执行Python代码
支持Docker模式和本地回退模式
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict

from app.core.code_security import check_code_security, get_security_report
from app.core.config import settings

# ========== 配置常量 ==========
SANDBOX_IMAGE_NAME = settings.SANDBOX_IMAGE_NAME
SANDBOX_IMAGE_VERSION = settings.SANDBOX_IMAGE_VERSION
SANDBOX_IMAGE_TAG = f"{SANDBOX_IMAGE_NAME}:{SANDBOX_IMAGE_VERSION}"
SANDBOX_CONTAINER_PREFIX = "sandbox-"
DEFAULT_TIMEOUT = 30  # 默认30秒
MAX_TIMEOUT = 300  # 最大300秒
MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB 输出限制
MAX_CODE_SIZE = 100 * 1024  # 100KB 代码大小限制
MAX_MEMORY_MB = 256  # 256MB 内存限制
MAX_CPU = 0.5  # 0.5核 CPU限制

# Docker资源限制
DOCKER_RESOURCE_LIMITS = {
    "mem_limit": "256m",  # 256MB 内存
    "memswap_limit": "256m",  # 禁用swap
    "cpu_quota": 50000,  # 0.5核 CPU (50000/100000)
    "cpu_period": 100000,
    "pids_limit": 50,  # 限制进程数
    "network_mode": "none",  # 禁用网络
}

# Docker安全选项
DOCKER_SECURITY_OPTS = [
    "no-new-privileges:true",  # 禁止获取新权限
    "seccomp=unconfined",  # 可以使用自定义seccomp配置
]

# 尝试导入docker
DOCKER_AVAILABLE = False
try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    docker = None


def check_docker_available() -> bool:
    """检查Docker是否可用"""
    if not DOCKER_AVAILABLE or docker is None:
        return False
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


# 镜像检查锁，防止并发构建
_image_check_lock = asyncio.Lock()
_image_checked = False
_image_exists = False


async def ensure_sandbox_image(force_rebuild: bool = False) -> bool:
    """
    确保沙箱镜像存在，支持版本管理

    Args:
        force_rebuild: 是否强制重新构建镜像

    Returns:
        bool: 镜像是否可用
    """
    global _image_checked, _image_exists

    if not DOCKER_AVAILABLE or docker is None:
        print("⚠️ Docker不可用，将使用本地回退模式")
        return False

    async with _image_check_lock:
        # 如果已经检查过且镜像存在，直接返回（除非强制重建）
        if _image_checked and _image_exists and not force_rebuild:
            return True

        try:
            client = docker.from_env()

            # 检查带版本标签的镜像
            try:
                image = client.images.get(SANDBOX_IMAGE_TAG)
                # 验证镜像版本标签
                labels = image.labels or {}
                image_version = labels.get("sandbox.version", "unknown")

                if image_version == SANDBOX_IMAGE_VERSION:
                    print(f"✅ 沙箱镜像 {SANDBOX_IMAGE_TAG} 已存在且版本匹配")
                    _image_checked = True
                    _image_exists = True
                    return True
                else:
                    print(
                        f"⚠️ 镜像版本不匹配 (当前: {image_version}, 期望: {SANDBOX_IMAGE_VERSION})"
                    )
                    # 继续执行重新构建
            except docker.errors.ImageNotFound:
                print(f"ℹ️ 沙箱镜像 {SANDBOX_IMAGE_TAG} 未找到，需要构建")

            # 检查是否存在旧版本镜像（带latest标签的）
            needs_rebuild = force_rebuild
            if not needs_rebuild:
                try:
                    old_image = client.images.get(SANDBOX_IMAGE_NAME)
                    old_labels = old_image.labels or {}
                    old_version = old_labels.get("sandbox.version", "unknown")
                    if old_version != SANDBOX_IMAGE_VERSION:
                        print(
                            f"⚠️ 检测到旧版本镜像 (v{old_version})，将重新构建 v{SANDBOX_IMAGE_VERSION}"  # noqa: E501
                        )
                        needs_rebuild = True
                except docker.errors.ImageNotFound:
                    needs_rebuild = True

            # 构建镜像
            sandbox_dir = Path(__file__).parent.parent.parent.parent.parent / "sandbox"
            if not sandbox_dir.exists():
                print(f"❌ 沙箱目录不存在: {sandbox_dir}")
                _image_checked = True
                _image_exists = False
                return False

            if not (sandbox_dir / "Dockerfile").exists():
                print(f"❌ Dockerfile 不存在: {sandbox_dir / 'Dockerfile'}")
                _image_checked = True
                _image_exists = False
                return False

            print(f"🔨 正在构建沙箱镜像 {SANDBOX_IMAGE_TAG}...")
            print(f"   构建目录: {sandbox_dir}")
            print(f"   版本: {SANDBOX_IMAGE_VERSION}")

            try:
                # 构建镜像
                image, build_logs = client.images.build(
                    path=str(sandbox_dir),
                    tag=SANDBOX_IMAGE_TAG,
                    buildargs={"SANDBOX_VERSION": SANDBOX_IMAGE_VERSION},
                    rm=True,
                    forcerm=True,
                    labels={
                        "sandbox.version": SANDBOX_IMAGE_VERSION,
                        "sandbox.name": "ai-learning-platform",
                        "sandbox.built_at": str(int(time.time())),
                    },
                )

                # 同时打 latest 标签便于兼容
                image.tag(SANDBOX_IMAGE_NAME, "latest")

                print(f"✅ 沙箱镜像 {SANDBOX_IMAGE_TAG} 构建完成")
                print(f"   镜像ID: {image.id[:12]}")

                _image_checked = True
                _image_exists = True
                return True

            except docker.errors.BuildError as e:
                print("❌ 镜像构建失败:")
                for log in e.build_log:
                    if "stream" in log:
                        print(f"   {log['stream'].strip()}")
                    if "error" in log:
                        print(f"   ERROR: {log['error']}")
                _image_checked = True
                _image_exists = False
                return False

        except Exception as e:
            print(f"❌ 检查/构建沙箱镜像失败: {e}")
            _image_checked = True
            _image_exists = False
            return False


def get_sandbox_image_info() -> dict:
    """
    获取当前沙箱镜像信息

    Returns:
        dict: 包含镜像状态、版本等信息的字典
    """
    info = {
        "image_name": SANDBOX_IMAGE_NAME,
        "image_version": SANDBOX_IMAGE_VERSION,
        "image_tag": SANDBOX_IMAGE_TAG,
        "docker_available": check_docker_available(),
        "image_exists": False,
        "image_details": None,
    }

    if not DOCKER_AVAILABLE or docker is None:
        return info

    try:
        client = docker.from_env()

        # 检查带版本标签的镜像
        try:
            image = client.images.get(SANDBOX_IMAGE_TAG)
            info["image_exists"] = True
            info["image_details"] = {
                "id": image.id,
                "short_id": image.short_id,
                "tags": image.tags,
                "created": image.attrs.get("Created"),
                "size": image.attrs.get("Size", 0),
                "labels": image.labels,
            }
        except docker.errors.ImageNotFound:
            pass

        # 也检查 latest 标签
        try:
            latest_image = client.images.get(f"{SANDBOX_IMAGE_NAME}:latest")
            if not info["image_exists"]:
                info["image_exists"] = True
                info["image_details"] = {
                    "id": latest_image.id,
                    "short_id": latest_image.short_id,
                    "tags": latest_image.tags,
                    "created": latest_image.attrs.get("Created"),
                    "size": latest_image.attrs.get("Size", 0),
                    "labels": latest_image.labels,
                }
        except docker.errors.ImageNotFound:
            pass

    except Exception as e:
        info["error"] = str(e)

    return info


def validate_code(code: str, timeout: int) -> tuple[bool, str]:
    """
    验证代码输入

    Args:
        code: Python代码
        timeout: 超时时间

    Returns:
        (是否有效, 错误信息)
    """
    # 检查代码大小
    if len(code) > MAX_CODE_SIZE:
        return False, f"代码大小超过限制 ({len(code)} > {MAX_CODE_SIZE} bytes)"

    # 检查超时时间
    if timeout <= 0 or timeout > MAX_TIMEOUT:
        return False, f"超时时间无效 (1-{MAX_TIMEOUT}秒)"

    # 检查代码是否为空
    if not code.strip():
        return False, "代码为空"

    return True, ""


async def execute_code_subprocess_fallback(code: str, timeout: int = DEFAULT_TIMEOUT) -> Dict:
    """
    使用subprocess本地执行Python代码（Docker不可用时回退）
    使用资源限制和安全包装
    """
    start_time = time.time()
    temp_file = None

    try:
        # 包装代码，限制资源和输出
        # 包装代码，限制资源和输出
        # 用户代码通过 exec() 执行，避免函数外 return/yield 导致 SyntaxError
        indented_code = chr(10).join("    " + line for line in code.split(chr(10)))
        wrapped_code = f"""import sys
import io
import resource
import signal

# 设置资源限制
def set_limits():
    try:
        # CPU时间限制
        resource.setrlimit(resource.RLIMIT_CPU, ({timeout}, {timeout} + 1))
        # 内存限制 256MB
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
        # 文件大小限制 1MB
        resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
        # 进程数限制
        resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    except Exception:
        pass

set_limits()

# 重定向输出
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

# 执行用户代码（通过 exec 避免缩进陷阱）
_user_code = {repr(code)}
try:
    exec(_user_code)
except Exception as e:
    import traceback
    print(f"Error: {{e}}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)

# 获取输出
output = sys.stdout.getvalue()
error = sys.stderr.getvalue()
sys.stdout = old_stdout
sys.stderr = old_stderr

# 限制输出大小
MAX_OUTPUT = 10000
if len(output) > MAX_OUTPUT:
    output = output[:MAX_OUTPUT] + "\\n[输出已截断]"
if len(error) > MAX_OUTPUT:
    error = error[:MAX_OUTPUT] + "\\n[错误输出已截断]"

import json
result = {{
    "success": len(error) == 0,
    "output": output,
    "error": error if error else None
}}
print("===RESULT_START===")
print(json.dumps(result))
print("===RESULT_END===")
"""

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(wrapped_code)
            temp_file = f.name

        # 使用subprocess执行
        process = await asyncio.create_subprocess_exec(
            "python3",
            temp_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=1024 * 1024,  # 限制缓冲区大小1MB
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            execution_time_ms = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "output": "",
                "error": f"代码执行超时（超过{timeout}秒）",
                "execution_time_ms": execution_time_ms,
            }

        execution_time_ms = int((time.time() - start_time) * 1000)

        # 解析输出
        stdout_str = stdout.decode("utf-8", errors="replace")
        stderr_str = stderr.decode("utf-8", errors="replace")

        # 尝试从输出中提取JSON结果
        output = ""
        error = ""
        success = process.returncode == 0

        if "===RESULT_START===" in stdout_str and "===RESULT_END===" in stdout_str:
            try:
                start = stdout_str.index("===RESULT_START===") + len("===RESULT_START===")
                end = stdout_str.index("===RESULT_END===")
                json_str = stdout_str[start:end].strip()
                result = json.loads(json_str)
                success = result.get("success", False)
                output = result.get("output", "")
                error = result.get("error", "")
            except Exception:
                output = stdout_str
                error = stderr_str
        else:
            output = stdout_str[:10000]
            error = stderr_str[:10000] if stderr_str else None

        return {
            "success": success,
            "output": output,
            "error": error,
            "execution_time_ms": execution_time_ms,
        }

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "output": "",
            "error": f"执行错误: {str(e)}",
            "execution_time_ms": execution_time_ms,
        }
    finally:
        if temp_file:
            try:
                os.unlink(temp_file)
            except Exception:
                pass


async def execute_code_docker(code: str, timeout: int = DEFAULT_TIMEOUT, *, skip_security: bool = False) -> Dict:
    """
    使用Docker沙箱执行Python代码

    Args:
        code: 要执行的Python代码
        timeout: 执行超时时间（秒）
        skip_security: 跳过安全检查（用于系统内部代码如 grader 评测脚本）

    Returns:
        {
            'success': bool,
            'output': str,
            'error': str or None,
            'execution_time_ms': int
        }
    """
    start_time = time.time()

    # 1. 输入验证
    is_valid, error_msg = validate_code(code, timeout)
    if not is_valid:
        return {
            "success": False,
            "output": "",
            "error": f"输入验证失败: {error_msg}",
            "execution_time_ms": 0,
        }

    # 2. Security check (skip for system-generated code like grader scripts)
    is_safe, security_error = check_code_security(code, skip_security=skip_security)
    if not is_safe:
        return {"success": False, "output": "", "error": security_error, "execution_time_ms": 0}

    # 3. 检查Docker是否可用
    if not check_docker_available():
        # 回退到subprocess模式
        return await execute_code_subprocess_fallback(code, timeout)

    # 4. 确保镜像存在
    if not await ensure_sandbox_image():
        # 回退到subprocess模式
        return await execute_code_subprocess_fallback(code, timeout)

    # 5. 在Docker容器中执行代码
    return await _run_in_container(code, timeout, start_time)


async def _run_in_container(code: str, timeout: int, start_time: float) -> Dict:
    """在Docker容器中运行代码"""
    client = docker.from_env()
    container = None

    try:
        # 准备执行数据
        exec_data = {"code": code, "timeout": timeout}

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(exec_data, f)
            temp_input_file = f.name

        # 生成唯一容器名
        container_name = (
            f"{SANDBOX_CONTAINER_PREFIX}{int(time.time() * 1000)}-{os.urandom(4).hex()}"
        )

        # 准备挂载
        mounts = []
        if os.path.exists(temp_input_file):
            mounts.append(
                {
                    "type": "bind",
                    "source": temp_input_file,
                    "target": "/tmp/input.json",
                    "read_only": True,
                }
            )

        # 创建并启动容器
        container = client.containers.run(
            SANDBOX_IMAGE_NAME,
            name=container_name,
            command=["python", "/home/sandbox/runner.py"],
            stdin_open=True,
            detach=True,
            **DOCKER_RESOURCE_LIMITS,
            security_opt=DOCKER_SECURITY_OPTS,
            cap_drop=["ALL"],  # 丢弃所有能力
            cap_add=["SETUID", "SETGID"],  # 仅保留最小必要能力
            read_only=True,  # 只读根文件系统
            volumes={"/tmp": {"bind": "/home/sandbox/tmp", "mode": "rw"}},
        )

        # 通过stdin发送代码
        container_stdin = container.attach_socket(params={"stdin": 1, "stream": 1})
        container_stdin.send(json.dumps(exec_data).encode("utf-8"))
        container_stdin.close()

        # 等待执行完成或超时
        try:
            # 使用asyncio等待容器完成
            loop = asyncio.get_event_loop()

            # 等待容器退出
            _result = await asyncio.wait_for(  # noqa: F841
                loop.run_in_executor(None, _wait_for_container, container),
                timeout=timeout + 5,  # 额外5秒缓冲
            )

            execution_time_ms = int((time.time() - start_time) * 1000)

            # 获取容器日志
            logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")

            # 清理容器
            try:
                container.remove(force=True)
            except Exception:
                pass

            # 清理临时文件
            try:
                os.unlink(temp_input_file)
            except Exception:
                pass

            # 解析结果
            return _parse_execution_result(logs, execution_time_ms)

        except asyncio.TimeoutError:
            # 执行超时
            execution_time_ms = int((time.time() - start_time) * 1000)

            # 强制停止容器
            try:
                container.kill()
                container.remove(force=True)
            except Exception:
                pass

            # 清理临时文件
            try:
                os.unlink(temp_input_file)
            except Exception:
                pass

            return {
                "success": False,
                "output": "",
                "error": f"代码执行超时（超过{timeout}秒）",
                "execution_time_ms": execution_time_ms,
            }

    except docker.errors.ContainerError as e:
        execution_time_ms = int((time.time() - start_time) * 1000)

        # 清理容器
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass

        # 清理临时文件
        try:
            os.unlink(temp_input_file)
        except Exception:
            pass

        return {
            "success": False,
            "output": "",
            "error": f"容器执行错误: {str(e)}",
            "execution_time_ms": execution_time_ms,
        }

    except docker.errors.ImageNotFound:
        execution_time_ms = int((time.time() - start_time) * 1000)

        return {
            "success": False,
            "output": "",
            "error": "沙箱镜像未找到",
            "execution_time_ms": execution_time_ms,
        }

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)

        # 清理容器
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass

        # 清理临时文件
        try:
            os.unlink(temp_input_file)
        except Exception:
            pass

        return {
            "success": False,
            "output": "",
            "error": f"执行错误: {str(e)}",
            "execution_time_ms": execution_time_ms,
        }


def _wait_for_container(container):
    """等待容器执行完成"""
    result = container.wait()
    return result


def _parse_execution_result(logs: str, execution_time_ms: int) -> Dict:
    """解析执行结果"""
    try:
        # 尝试解析JSON输出
        # 日志可能包含多行，找到JSON部分
        lines = logs.strip().split("\n")
        result_line = None

        for line in reversed(lines):
            line = line.strip()
            if line and (line.startswith("{") or line.startswith("[")):
                result_line = line
                break

        if result_line:
            result = json.loads(result_line)
            result["execution_time_ms"] = execution_time_ms
            return result
        else:
            # 没有找到JSON，返回原始日志
            return {
                "success": True,
                "output": logs,
                "error": None,
                "execution_time_ms": execution_time_ms,
            }

    except json.JSONDecodeError:
        # JSON解析失败，返回原始日志
        return {
            "success": True,
            "output": logs,
            "error": None,
            "execution_time_ms": execution_time_ms,
        }


def cleanup_old_containers(max_age_seconds: int = 3600):
    """清理旧的沙箱容器"""
    if not DOCKER_AVAILABLE or docker is None:
        return
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)

        for container in containers:
            if container.name.startswith(SANDBOX_CONTAINER_PREFIX):
                try:
                    # 检查容器状态
                    if container.status == "exited":
                        container.remove(force=True)
                        print(f"已清理容器: {container.name}")
                except Exception as e:
                    print(f"清理容器 {container.name} 失败: {e}")

    except Exception as e:
        print(f"清理容器失败: {e}")


# 兼容旧接口
async def execute_code_sandbox(code: str, timeout: int = DEFAULT_TIMEOUT) -> Dict:
    """
    在沙箱环境中执行Python代码 (兼容接口)

    Args:
        code: 要执行的Python代码
        timeout: 执行超时时间（秒）

    Returns:
        {
            'success': bool,
            'output': str,
            'error': str or None,
            'execution_time_ms': int
        }
    """
    return await execute_code_docker(code, timeout)


# 获取安全报告
async def get_code_security_report(code: str) -> Dict:
    """获取代码安全报告"""
    return get_security_report(code)


# 测试代码
if __name__ == "__main__":

    async def test():
        print("=" * 50)
        print("代码沙箱测试")
        print("=" * 50)

        # 测试1: 正常代码
        print("\n测试1 - 正常代码:")
        result = await execute_code_sandbox('print("Hello, World!")')
        print(f"结果: {result}")

        # 测试2: 危险代码
        print("\n测试2 - 危险代码 (os.system):")
        result = await execute_code_sandbox('import os; os.system("ls")')
        print(f"结果: {result}")

        # 测试3: 计算代码
        print("\n测试3 - 计算代码:")
        result = await execute_code_sandbox("""
import math
result = sum(range(1, 101))
print(f"1到100的和: {result}")
print(f"平方根: {math.sqrt(result)}")
""")
        print(f"结果: {result}")

        # 测试4: 超时测试
        print("\n测试4 - 超时测试:")
        result = await execute_code_sandbox(
            """
import time
time.sleep(60)
print("这行不会执行")
""",
            timeout=3,
        )
        print(f"结果: {result}")

        # 测试5: 错误代码
        print("\n测试5 - 错误代码:")
        result = await execute_code_sandbox("print(undefined_variable)")
        print(f"结果: {result}")

        # 测试6: 使用numpy
        print("\n测试6 - 使用numpy:")
        result = await execute_code_sandbox("""
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"数组: {arr}")
print(f"平均值: {np.mean(arr)}")
""")
        print(f"结果: {result}")

    asyncio.run(test())
