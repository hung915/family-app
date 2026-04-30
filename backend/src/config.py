from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    ENV: str = 'local'  # local | staging | production
    DATABASE_URL: str = 'postgresql+asyncpg://localhost/family_app'
    SECRET_KEY: str = 'change-me-in-production'  # noqa: S105
    CORS_ORIGINS: list[str] = ['http://localhost:5173']


settings = Config()
