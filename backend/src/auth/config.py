from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # Secrets — override all of these in production via env vars.
    JWT_SECRET: str = 'dev-jwt-secret-change-in-prod'  # noqa: S105
    MAGIC_LINK_SECRET: str = 'dev-magic-link-secret-change-in-prod'  # noqa: S105

    RESEND_API_KEY: str = 're_test'
    RESEND_FROM_EMAIL: str = 'Family App <noreply@example.com>'

    # Base URL of this API — used to construct the magic-link callback URL.
    API_BASE_URL: str = 'http://localhost:8000'

    # Where to redirect after a successful login.
    FRONTEND_URL: str = 'http://localhost:5173'


auth_settings = AuthConfig()
