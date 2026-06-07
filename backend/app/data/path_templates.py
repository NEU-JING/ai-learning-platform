"""Path module seed data — 4 predefined learning path templates.

路径模板定义:
- ai-researcher: AI专家路径 (20周)
- ai-engineer: AI工程师路径 (14周)
- ai-applier: AI应用者路径 (8周)
- ai-manager: AI管理者路径 (6周)
"""

# Seed behavior constants
BEHAVIOR_CREATE_ONLY = "create_only"  # Only create if not exists; skip existing
BEHAVIOR_UPSERT = "upsert"  # Insert or update; seed file is source of truth


PATH_TEMPLATES = [
    {
        "slug": "ai-researcher",
        "name": "AI专家路径",
        "description": (
            "深入研究AI理论与前沿技术，适合追求算法创新的学习者。"
            "涵盖深度学习、大语言模型、强化学习等高级主题。"
        ),
        "duration_weeks": 20,
        "target_role": "AI专家",
        "required_courses": [1, 2, 3, 4, 5, 6],  # 6个主要课程
        "elective_courses": [7, 8],
        "capstone_count": 2,
    },
    {
        "slug": "ai-engineer",
        "name": "AI工程师路径",
        "description": (
            "侧重工程实现与系统构建，培养能独立开发AI产品的工程师。"
            "包含MLOps、模型部署、性能优化等实践技能。"
        ),
        "duration_weeks": 14,
        "target_role": "AI工程师",
        "required_courses": [1, 2, 3, 4, 5],  # 5个主要课程
        "elective_courses": [6],
        "capstone_count": 2,
    },
    {
        "slug": "ai-applier",
        "name": "AI应用者路径",
        "description": (
            "快速掌握AI工具与API应用，适合希望将AI融入现有工作的专业人士。"
            "聚焦Prompt工程、RAG应用、AI工作流。"
        ),
        "duration_weeks": 8,
        "target_role": "AI应用者",
        "required_courses": [1, 3, 5],  # 3个主要课程
        "elective_courses": [2],
        "capstone_count": 2,
    },
    {
        "slug": "ai-manager",
        "name": "AI管理者路径",
        "description": (
            "培养AI项目管理与战略规划能力，适合技术管理者与决策者。"
            "学习AI项目管理、团队搭建、ROI评估等内容。"
        ),
        "duration_weeks": 6,
        "target_role": "AI管理者",
        "required_courses": [1, 5],  # 2个主要课程
        "elective_courses": [2, 3],
        "capstone_count": 2,
    },
]


PATH_MILESTONES = [
    # AI专家路径里程碑
    {
        "template_slug": "ai-researcher",
        "name": "Python基础达成",
        "sequence_order": 1,
        "required_courses": [],
        "reward_badge": "python_foundation",
    },
    {
        "template_slug": "ai-researcher",
        "name": "数学基础达成",
        "sequence_order": 2,
        "required_courses": [],
        "reward_badge": "math_foundation",
    },
    {
        "template_slug": "ai-researcher",
        "name": "机器学习入门",
        "sequence_order": 3,
        "required_courses": [],
        "reward_badge": "ml_beginner",
    },
    {
        "template_slug": "ai-researcher",
        "name": "深度学习进阶",
        "sequence_order": 4,
        "required_courses": [],
        "reward_badge": "dl_advanced",
    },
    {
        "template_slug": "ai-researcher",
        "name": "大模型研究",
        "sequence_order": 5,
        "required_courses": [],
        "reward_badge": "llm_researcher",
    },
    # AI工程师路径里程碑
    {
        "template_slug": "ai-engineer",
        "name": "Python基础达成",
        "sequence_order": 1,
        "required_courses": [],
        "reward_badge": "python_foundation",
    },
    {
        "template_slug": "ai-engineer",
        "name": "工程能力认证",
        "sequence_order": 2,
        "required_courses": [],
        "reward_badge": "engineering_certified",
    },
    {
        "template_slug": "ai-engineer",
        "name": "模型部署实战",
        "sequence_order": 3,
        "required_courses": [],
        "reward_badge": "deployment_expert",
    },
    {
        "template_slug": "ai-engineer",
        "name": "系统架构设计",
        "sequence_order": 4,
        "required_courses": [],
        "reward_badge": "system_architect",
    },
    # AI应用者路径里程碑
    {
        "template_slug": "ai-applier",
        "name": "AI工具掌握",
        "sequence_order": 1,
        "required_courses": [],
        "reward_badge": "ai_tools_master",
    },
    {
        "template_slug": "ai-applier",
        "name": "Prompt工程认证",
        "sequence_order": 2,
        "required_courses": [],
        "reward_badge": "prompt_engineer",
    },
    {
        "template_slug": "ai-applier",
        "name": "工作流自动化",
        "sequence_order": 3,
        "required_courses": [],
        "reward_badge": "workflow_automation",
    },
    # AI管理者路径里程碑
    {
        "template_slug": "ai-manager",
        "name": "AI战略理解",
        "sequence_order": 1,
        "required_courses": [],
        "reward_badge": "ai_strategist",
    },
    {
        "template_slug": "ai-manager",
        "name": "项目管理认证",
        "sequence_order": 2,
        "required_courses": [],
        "reward_badge": "project_manager",
    },
    {
        "template_slug": "ai-manager",
        "name": "团队领导资质",
        "sequence_order": 3,
        "required_courses": [],
        "reward_badge": "team_leader",
    },
]


def seed_path_templates(db, behavior=BEHAVIOR_UPSERT):
    """Insert or update path template seed data."""
    from app.models.path import PathTemplate

    existing_slugs = {t.slug: t for t in db.query(PathTemplate).all()}

    for template_data in PATH_TEMPLATES:
        slug = template_data["slug"]
        if slug in existing_slugs and behavior == BEHAVIOR_UPSERT:
            # Update existing template
            existing = existing_slugs[slug]
            existing.name = template_data["name"]
            existing.description = template_data["description"]
            existing.duration_weeks = template_data["duration_weeks"]
            existing.target_role = template_data["target_role"]
            existing.required_courses = template_data["required_courses"]
            existing.elective_courses = template_data["elective_courses"]
            existing.capstone_count = template_data["capstone_count"]
        elif slug not in existing_slugs:
            # Create new template
            template = PathTemplate(**template_data)
            db.add(template)

    db.commit()


def seed_path_milestones(db):
    """Insert path milestone seed data if not exists."""
    from app.models.path import PathMilestone, PathTemplate

    # Get template id mapping
    templates = {t.slug: t.id for t in db.query(PathTemplate).all()}

    for milestone_data in PATH_MILESTONES:
        template_slug = milestone_data["template_slug"]
        if template_slug in templates:
            # Check if milestone already exists
            exists = (
                db.query(PathMilestone)
                .filter_by(template_id=templates[template_slug], name=milestone_data["name"])
                .first()
            )
            if not exists:
                milestone = PathMilestone(
                    template_id=templates[template_slug],
                    name=milestone_data["name"],
                    description=milestone_data.get("description"),
                    sequence_order=milestone_data["sequence_order"],
                    required_courses=milestone_data.get("required_courses"),
                    reward_badge=milestone_data.get("reward_badge"),
                )
                db.add(milestone)

    db.commit()


def seed_all_path_data(db, behavior=BEHAVIOR_UPSERT):
    """Seed all path-related data."""
    seed_path_templates(db, behavior=behavior)
    seed_path_milestones(db)
