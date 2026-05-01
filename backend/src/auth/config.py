from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    JWT_SECRET: str = 'dev-jwt-secret-change-in-prod'  # noqa: S105


auth_settings = AuthConfig()
