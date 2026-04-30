from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # Secrets — override all of these in production via env vars.
    JWT_SECRET: str = 'dev-jwt-secret-change-in-prod'  # noqa: S105
    MAGIC_LINK_SECRET: str = 'dev-magic-link-secret-change-in-prod'  # noqa: S105

    RESEND_API_KEY: str = 're_test'
    # Dev: use Resend's shared testing address (delivers only to your Resend account email).
    # Prod: set to a sender on your verified domain, e.g. "Family App <noreply@yourdomain.com>".
    RESEND_FROM_EMAIL: str = 'onboarding@resend.dev'

    # Base URL of this API — used to construct the magic-link callback URL.
    API_BASE_URL: str = 'http://localhost:8000'

    # Where to redirect after a successful login.
    FRONTEND_URL: str = 'http://localhost:5173'


auth_settings = AuthConfig()
