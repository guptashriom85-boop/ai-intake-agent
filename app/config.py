from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Intake Agent"
    database_url: str = "sqlite:///./intake.db"
    jwt_secret: str = "change-me-in-production"
    admin_email: str = "admin@example.com"
    admin_password: str = "change-me"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    cors_origins: str = "*"
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

settings = Settings()
