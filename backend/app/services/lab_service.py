import subprocess
import tempfile
import os
import signal
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Lab, LabSubmission
from app.services.grader import CodeGrader
from datetime import datetime


class LabService:
    FORBIDDEN_KEYWORDS = [
        'os.system', 'subprocess', 'eval', 'exec', '__import__',
        'open(', 'file(', 'read(', 'write(', 'socket',
        'urllib', 'http.client', 'requests', 'ftp', 'ssh'
    ]
    
    @staticmethod
    def validate_code(code: str) -> tuple[bool, Optional[str]]:
        """验证代码安全性"""
        for keyword in LabService.FORBIDDEN_KEYWORDS:
            if keyword in code:
                return False, f"代码包含禁止使用的关键字: {keyword}"
        return True, None
    
    @staticmethod
    def execute_code(code: str, timeout: int = 30) -> dict:
        """在沙箱中执行代码"""
        # 安全检查
        is_safe, error_msg = LabService.validate_code(code)
        if not is_safe:
            return {
                "status": "failed",
                "output": "",
                "error": error_msg,
                "execution_time_ms": 0
            }
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            import time
            start_time = time.time()
            
            # 使用受限环境执行
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                env={
                    'PATH': '/usr/bin:/bin',
                    'HOME': '/tmp',
                    'PYTHONPATH': ''
                }
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None,
                    "execution_time_ms": execution_time
                }
            else:
                return {
                    "status": "failed",
                    "output": result.stdout,
                    "error": result.stderr,
                    "execution_time_ms": execution_time
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "output": "",
                "error": f"代码执行超时（限制{timeout}秒）",
                "execution_time_ms": timeout * 1000
            }
        except Exception as e:
            return {
                "status": "failed",
                "output": "",
                "error": str(e),
                "execution_time_ms": 0
            }
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
    
    @staticmethod
    def submit_code(
        db: Session,
        user_id: int,
        lab_id: int,
        code: str
    ) -> LabSubmission:
        """提交实验代码并执行"""
        # 获取实验信息
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        if not lab:
            raise ValueError("实验不存在")
        
        # 创建提交记录
        submission = LabSubmission(
            user_id=user_id,
            lab_id=lab_id,
            code=code,
            status="running"
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # 执行代码
        timeout = lab.time_limit_seconds or 30
        result = LabService.execute_code(code, timeout)
        
        # 更新提交记录
        submission.status = result["status"]
        submission.output = result["output"]
        submission.error_message = result["error"]
        submission.execution_time_ms = result["execution_time_ms"]
        submission.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(submission)
        
        return submission

    @staticmethod
    def submit_with_grading(
        db: Session,
        user_id: int,
        lab_id: int,
        code: str
    ) -> dict:
        """
        提交实验代码并进行自动评测
        
        Returns:
            {
                "submission": LabSubmission,
                "grading": {
                    "passed": bool,
                    "score": int,
                    "feedback": str,
                    ...
                }
            }
        """
        from sqlalchemy.orm import Session
        
        # 获取实验信息
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        if not lab:
            raise ValueError("实验不存在")
        
        # 创建提交记录
        submission = LabSubmission(
            user_id=user_id,
            lab_id=lab_id,
            code=code,
            status="running"
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # 执行代码
        timeout = lab.time_limit_seconds or 30
        exec_result = LabService.execute_code(code, timeout)
        
        # 自动评测
        test_cases = lab.test_cases or []
        grading_result = CodeGrader.grade_submission(
            code=code,
            test_cases=test_cases,
            solution_code=lab.solution_code
        )
        
        # 生成反馈
        feedback = CodeGrader.generate_feedback(grading_result)
        
        # 更新提交记录
        submission.status = "success" if grading_result["passed"] else "failed"
        submission.output = exec_result["output"]
        submission.error_message = exec_result["error"]
        submission.execution_time_ms = exec_result["execution_time_ms"]
        submission.updated_at = datetime.utcnow()
        
        # 存储评分结果（可以通过扩展模型字段保存）
        db.commit()
        db.refresh(submission)
        
        return {
            "submission": submission,
            "grading": {
                **grading_result,
                "feedback": feedback
            }
        }


lab_service = LabService()
