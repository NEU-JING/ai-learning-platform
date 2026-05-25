# AGENTS.md — AILP（AI Learning Platform）

## 项目信息
- name: "AILP"
- description: "AI 学习平台 — 6 阶段课程系统（Python → Math → ML → DL → LLM → Engineering），含代码执行沙盒"
- repo: "TBD"

## 技术栈
- backend: "Python/FastAPI"
- frontend: "React/TypeScript/Vite"
- database: "SQLite（开发）/ PostgreSQL（生产）"
- sandbox: "subprocess fallback（Docker 不可用）"

## 路径约定
- changes_dir: "docs/changes/"
- current_dir: "docs/current/"
- archive_dir: "docs/archive/"
- backend_dir: "backend/"
- frontend_dir: "frontend/"

## SDD 配置
- flow_engine: "sdd/sdd-orchestrator"
- default_flow_level: "Standard"

## 项目约束
- constitution: "CONSTITUTION.md"
- quirks: "QUIRKS.md"

## 自定义覆盖
- convention_overrides:
    disable_rules: ["R5"]  # 前端由后端直接服务静态文件，无独立前端变更流程
    custom_rules:
      - id: "R11"
        name: "Phase 3-6 数据保护"
        trigger: "coder-agent 修改 backend/app/data/ 目录"
        check: "检查是否修改了 courses_phase3_6.py 的 create_only 行为；Phase 3-6 深度内容仅在 DB 中，不可被种子数据覆盖"
        violation: "CRITICAL"
      - id: "R12"
        name: "数据契约不可违反"
        trigger: "coder-agent 修改 models/ 或 schemas/"
        check: "运行 pytest tests/test_data_contract.py -v，全量通过"
        violation: "CRITICAL"

## 快速命令
```bash
cd backend && source /tmp/ailp-venv/bin/activate
SERVE_STATIC=True uvicorn app.main:app --host 0.0.0.0 --port 8000
pytest tests/ -v
pytest tests/test_data_contract.py -v
```
