from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AI Learning Platform"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # 数据库配置 (SQLite - 零配置)
    DATABASE_URL: str = "sqlite:///./ai_learning.db"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS配置
    # 开发环境允许localhost，生产环境必须在环境变量中配置
    CORS_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True

    # JWT配置 - 生产环境必须通过环境变量设置 SECRET_KEY
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 沙箱配置
    SANDBOX_TIMEOUT: int = 30  # 代码执行超时时间（秒）
    SANDBOX_MEMORY_LIMIT: str = "256m"
    SANDBOX_CPU_LIMIT: float = 0.5

    # 沙箱镜像版本配置
    SANDBOX_IMAGE_VERSION: str = "1.0.0"  # 镜像版本号，变更时自动重新构建
    SANDBOX_IMAGE_NAME: str = "ai-learning-platform-sandbox"

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"

    model_config = {"env_file": ".env"}


settings = Settings()


# 验证 SECRET_KEY 配置
def validate_settings():
    """验证关键配置项"""
    import os

    # 检查是否在开发环境
    is_dev = settings.DEBUG or os.getenv("ENVIRONMENT", "development").lower() == "development"

    if not settings.SECRET_KEY:
        if is_dev:
            # 开发环境生成临时密钥
            import secrets

            settings.SECRET_KEY = secrets.token_hex(32)
            print("⚠️ 警告: 开发环境使用临时生成的 SECRET_KEY")
        else:
            raise ValueError(
                "❌ 错误: 生产环境必须设置 SECRET_KEY 环境变量!\n"
                "请在 .env 文件或环境变量中设置强密钥，例如:\n"
                "SECRET_KEY=$(openssl rand -hex 32)"
            )

    # 检查密钥强度
    if len(settings.SECRET_KEY) < 32:
        raise ValueError("❌ SECRET_KEY 必须至少32个字符长度")

    # 生产环境安全检查
    if not settings.DEBUG:
        # 检查CORS配置
        if "*" in settings.CORS_ORIGINS:
            raise ValueError(
                "❌ 生产环境CORS_ORIGINS不能包含通配符'*'\n"
                "请设置具体的域名，例如: CORS_ORIGINS=https://your-domain.com"
            )

        # 检查是否是默认密钥
        if settings.SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError(
                "❌ 生产环境不能使用默认SECRET_KEY\n" "请生成新的密钥: openssl rand -hex 32"
            )

        print("✅ 生产环境安全配置检查通过")


# 启动时验证
validate_settings()
