"""10维技能雷达种子数据.

T6: Radar 模块数据库表 — 技能维度定义
涵盖：硬技能、软技能、路径特化维度
"""

from sqlalchemy.orm import Session


def get_skill_dimensions_seed():
    """返回10维技能维度种子数据."""
    return [
        # 硬技能维度 (Hard Skills)
        {
            "slug": "coding_thinking",
            "name": "编程思维",
            "name_en": "Coding Thinking",
            "description": "代码逻辑、调试能力、代码质量意识",
            "category": "hard",
            "weight_formula": "avg(lab_scores) * time_decay",
            "max_score": 100.0,
        },
        {
            "slug": "algorithm_understanding",
            "name": "算法理解",
            "name_en": "Algorithm Understanding",
            "description": "算法原理理解、复杂度分析、算法选择能力",
            "category": "hard",
            "weight_formula": "avg(algorithm_lab_scores) * time_decay",
            "max_score": 100.0,
        },
        {
            "slug": "system_design",
            "name": "系统设计",
            "name_en": "System Design",
            "description": "架构设计、模块划分、可扩展性考虑",
            "category": "hard",
            "weight_formula": "project_scores * design_review_scores",
            "max_score": 100.0,
        },
        {
            "slug": "engineering_practice",
            "name": "工程实践",
            "name_en": "Engineering Practice",
            "description": "代码规范、版本控制、CI/CD、测试覆盖",
            "category": "hard",
            "weight_formula": "code_quality * test_coverage * cicd_adoption",
            "max_score": 100.0,
        },
        {
            "slug": "data_analysis",
            "name": "数据分析",
            "name_en": "Data Analysis",
            "description": "数据清洗、特征工程、数据可视化",
            "category": "hard",
            "weight_formula": "avg(data_lab_scores) * project_complexity",
            "max_score": 100.0,
        },
        # 软技能维度 (Soft Skills)
        {
            "slug": "problem_solving",
            "name": "问题解决",
            "name_en": "Problem Solving",
            "description": "问题分解、方案评估、迭代优化",
            "category": "soft",
            "weight_formula": "challenge_completion_rate * solution_quality",
            "max_score": 100.0,
        },
        {
            "slug": "ai_collaboration",
            "name": "AI协作",
            "name_en": "AI Collaboration",
            "description": "提示词工程、AI工具使用、人机协作效率",
            "category": "soft",
            "weight_formula": "ai_tutor_interaction_quality * prompt_effectiveness",
            "max_score": 100.0,
        },
        {
            "slug": "research_depth",
            "name": "研究深度",
            "name_en": "Research Depth",
            "description": "论文阅读、前沿跟踪、理论深度",
            "category": "soft",
            "weight_formula": "paper_reading_count * implementation_depth",
            "max_score": 100.0,
        },
        # 路径特化维度 (Path Specialization)
        {
            "slug": "ai_application",
            "name": "AI应用",
            "name_en": "AI Application",
            "description": "业务场景识别、AI方案设计、落地能力",
            "category": "specialized",
            "weight_formula": "scenario_project_scores * business_impact",
            "max_score": 100.0,
        },
        {
            "slug": "prompt_engineering",
            "name": "提示工程",
            "name_en": "Prompt Engineering",
            "description": "提示词设计、链式思考、输出控制",
            "category": "specialized",
            "weight_formula": "prompt_lab_scores * llm_interaction_efficiency",
            "max_score": 100.0,
        },
    ]


def seed_skill_dimensions(db: Session):
    """Seed 10维技能维度数据."""
    from app.models.radar import SkillDimension

    # 检查是否已有数据
    existing_count = db.query(SkillDimension).count()
    if existing_count > 0:
        return  # 已有数据，跳过

    dimensions = get_skill_dimensions_seed()
    for dim_data in dimensions:
        dimension = SkillDimension(**dim_data)
        db.add(dimension)

    db.commit()


def get_dimension_by_slug(db: Session, slug: str):
    """根据 slug 获取技能维度."""
    from app.models.radar import SkillDimension

    return db.query(SkillDimension).filter(SkillDimension.slug == slug).first()


def get_all_dimensions(db: Session):
    """获取所有技能维度."""
    from app.models.radar import SkillDimension

    return db.query(SkillDimension).order_by(SkillDimension.category, SkillDimension.id).all()


def get_dimensions_by_category(db: Session, category: str):
    """按类别获取技能维度."""
    from app.models.radar import SkillDimension

    return db.query(SkillDimension).filter(SkillDimension.category == category).all()
