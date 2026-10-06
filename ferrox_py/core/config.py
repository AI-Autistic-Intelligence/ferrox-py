from pydantic_settings import BaseSettings

from ferrox_py.core.provider import injectable


@injectable()
class AppConfig(BaseSettings):
    """
    Auto-loads from .env or environment variables.
    Prefix 'FERROX_' can be used in env vars.
    """
    app_name: str = "Ferrox App"
    environment: str = "development"
    debug: bool = True
    database_url: str = "mongodb://localhost:27017"
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_prefix = "FERROX_"
        env_file = ".env"
        env_file_encoding = "utf-8"
