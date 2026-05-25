"""
学习路径种子数据 — 多路径课程体系 V3

定义了 4 条学习路径，每条路径由不同课程模块组成，满足不同角色需求：
  - ai_expert: AI 专家（全链路 6 阶段）
  - ai_engineer: AI 工程师（聚焦应用开发）
  - ai_practitioner: AI 应用者（业务角色）
  - ai_manager: AI 管理者（战略决策）

课程 ID 映射（Phase → course_id）：
  Phase 1 (P1 Python)       → id=5
  Phase 2 (P2 数学)          → id=6
  Phase 3 (P3 ML)            → id=7
  Phase 4 (P4 DL)            → id=8
  Phase 5 (P5 LLM)           → id=9
  Phase 6 (P6 工程化)         → id=10
"""

# Seed behavior constants
BEHAVIOR_CREATE_ONLY = "create_only"  # Only create if not exists; skip existing
BEHAVIOR_UPSERT = "upsert"  # Insert or update; seed file is source of truth

LEARNING_PATHS = [
    {
        "path_id": "ai_expert",
        "title": "AI 专家",
        "subtitle": "从开发者到 AI 全栈",
        "description": (
            "系统掌握 AI 全链路：Python → 数学 → ML → DL → LLM → 工程化。"
            "从 Python 基础开始，逐步深入机器学习、深度学习、大语言模型，"
            "最终掌握 AI 工程化部署和产品化能力。适合想深入 AI 核心技术的开发者，"
            "目标岗位为 ML Engineer / AI Researcher。"
        ),
        "target_role": "ML Engineer / AI Researcher",
        "estimated_weeks": 16,
        "order_index": 1,
        "modules": [
            {"course_id": 5, "requirement": "required"},  # P1 Python
            {"course_id": 6, "requirement": "required"},  # P2 数学
            {"course_id": 7, "requirement": "required"},  # P3 ML
            {"course_id": 8, "requirement": "required"},  # P4 DL
            {"course_id": 9, "requirement": "required"},  # P5 LLM
            {"course_id": 10, "requirement": "required"},  # P6 工程化
        ],
    },
    {
        "path_id": "ai_engineer",
        "title": "AI 工程师",
        "subtitle": "用 AI 提升 10x 开发效率",
        "description": (
            "聚焦 AI 应用开发能力：Python 基础 → 数学直觉 → LLM 大模型应用 → AI 工程化实践。"
            "跳过深度学习底层原理，专注用 AI 工具（LLM API、RAG、Agent）提升开发效率。"
            "适合想快速将 AI 能力融入日常开发工作的全栈工程师，"
            "目标岗位为 AI Engineer / 全栈+AI。"
        ),
        "target_role": "AI Engineer / 全栈+AI",
        "estimated_weeks": 10,
        "order_index": 2,
        "modules": [
            {"course_id": 5, "requirement": "required"},  # P1 Python
            {"course_id": 6, "requirement": "required"},  # P2 数学
            {"course_id": 7, "requirement": "optional"},  # P3 ML（选学）
            {"course_id": 9, "requirement": "required"},  # P5 LLM
            {"course_id": 10, "requirement": "required"},  # P6 工程化
        ],
    },
    {
        "path_id": "ai_practitioner",
        "title": "AI 应用者",
        "subtitle": "用 AI 解决业务问题",
        "description": (
            "面向业务角色的 AI 应用路径：Python 入门 → LLM 应用实践，零数学门槛。"
            "学会用 AI 解决数据分析、内容生成、流程自动化等实际业务问题。"
            "不需要深入技术底层，重点是会用、能用、用好 AI 工具。"
            "适合产品经理、数据分析师、运营等非技术岗位。"
        ),
        "target_role": "数据分析师 / 产品经理 / 运营",
        "estimated_weeks": 6,
        "order_index": 3,
        "modules": [
            {"course_id": 5, "requirement": "required"},  # P1 Python
            {"course_id": 9, "requirement": "required"},  # P5 LLM
            {"course_id": 10, "requirement": "recommended"},  # P6 工程化
        ],
    },
    {
        "path_id": "ai_manager",
        "title": "AI 管理者",
        "subtitle": "制定 AI 战略，管理 AI 团队",
        "description": (
            "面向技术管理者的 AI 战略路径：了解 AI 技术全貌、评估 AI 技术方案、"
            "管理 AI 团队、制定 AI 落地战略。不要求亲自写代码，重点是技术判断力和决策力。"
            "学会评估 AI 项目的可行性、合理配置资源、推动 AI 在组织内的落地。"
            "适合 CTO、技术总监、AI 产品负责人等管理岗位。"
        ),
        "target_role": "CTO / AI 产品负责人 / 技术总监",
        "estimated_weeks": 4,
        "order_index": 4,
        "modules": [
            {"course_id": 5, "requirement": "optional"},  # P1 Python（选学）
            {"course_id": 9, "requirement": "recommended"},  # P5 LLM
            {"course_id": 10, "requirement": "required"},  # P6 工程化
        ],
    },
]


def init_learning_paths(db, behavior=BEHAVIOR_UPSERT):
    """创建或更新学习路径种子数据。upsert by path_id。返回统计。

    Args:
        db: SQLAlchemy Session
        behavior: BEHAVIOR_UPSERT (default) — insert or update each path.
                  Set to BEHAVIOR_CREATE_ONLY to skip existing paths (won't update).

    Returns:
        dict: {"created": N, "updated": N, "modules_created": N, "modules_updated": N}
    """
    from app.models import Course, LearningPath, LearningPathModule

    stats = {"created": 0, "updated": 0, "modules_created": 0, "modules_updated": 0}

    for path_data in LEARNING_PATHS:
        path_id = path_data["path_id"]
        existing = db.query(LearningPath).filter(LearningPath.path_id == path_id).first()

        if existing:
            if behavior == BEHAVIOR_UPSERT:
                # Update existing path
                existing.title = path_data["title"]
                existing.subtitle = path_data["subtitle"]
                existing.description = path_data["description"]
                existing.target_role = path_data["target_role"]
                existing.estimated_weeks = path_data["estimated_weeks"]
                existing.is_published = True
                existing.order_index = path_data["order_index"]
                stats["updated"] += 1

                # Remove old modules and recreate
                db.query(LearningPathModule).filter(LearningPathModule.path_id == path_id).delete(
                    synchronize_session=False
                )
            else:
                # CREATE_ONLY: skip entirely
                continue
        else:
            # Create new path
            path = LearningPath(
                path_id=path_id,
                title=path_data["title"],
                subtitle=path_data["subtitle"],
                description=path_data["description"],
                target_role=path_data["target_role"],
                estimated_weeks=path_data["estimated_weeks"],
                is_published=True,
                order_index=path_data["order_index"],
            )
            db.add(path)
            stats["created"] += 1

        # Upsert modules (create or recreate)
        for idx, mod in enumerate(path_data["modules"]):
            course = db.query(Course).filter(Course.id == mod["course_id"]).first()
            if not course:
                continue  # Skip if course doesn't exist yet

            module = LearningPathModule(
                path_id=path_id,
                course_id=mod["course_id"],
                requirement=mod["requirement"],
                order_index=idx,
            )
            db.add(module)
            stats["modules_created"] += 1

    db.commit()

    if stats["created"]:
        print(f"✅ Created {stats['created']} learning paths")
    if stats["updated"]:
        print(f"✅ Updated {stats['updated']} learning paths")
    if stats["modules_created"]:
        print(f"✅ Created {stats['modules_created']} learning path modules")

    return stats
