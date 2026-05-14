# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-24

### Added

#### Core Features
- 完整课程体系：4阶段从Python入门到AI团队领导力
- 在线代码执行环境：基于Docker的安全沙箱
- 实验自动评测系统：测试用例 + 代码风格检查
- 学习进度追踪：可视化学习路径和成就系统
- 学习证书系统：HTML证书生成与验证

#### API & Backend
- FastAPI后端架构
- JWT认证系统
- 课程管理API
- 代码执行API
- 学习进度API
- 证书管理API
- 讨论区API

#### Frontend
- 单页应用(SPA)架构
- Monaco Editor代码编辑器集成
- 响应式设计
- 主题切换支持
- 代码自动保存

#### Infrastructure
- Docker容器化部署
- 代码执行沙箱
- nginx反向代理配置
- PostgreSQL支持
- Redis缓存

#### Documentation
- 完整README文档
- API文档(Swagger UI)
- 部署文档
- 运维手册

### Security
- CORS配置优化
- JWT密钥管理
- 生产环境安全检查
- 代码执行安全限制

### Changed
- 前端架构从多页应用迁移到单页应用
- CORS配置从通配符改为显式域名配置

### Fixed
- DEBUG模式默认开启问题
- CORS过于宽松的配置

## [0.9.0] - 2026-04-22

### Added
- 初始版本发布
- 基础课程管理
- 用户认证系统
- SQLite数据库支持

### Known Issues
- 需要完善生产环境配置
- 前端页面需要统一
