#!/usr/bin/env python3
"""
测试运行器 - 使用项目venv运行测试
"""
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 使用venv的python
venv_python = os.path.join(os.path.dirname(__file__), 'backend', 'venv', 'bin', 'python')

# 运行pytest
os.execv(venv_python, [venv_python, '-m', 'pytest', 'tests/test_complete.py', '-v', '--tb=short'])