from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    DATABASE_URL: str = "sqlite:///./data/app.db"
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_secret_strength(cls, v: str) -> str:
        forbidden = {
            "dev-only-secret-change-me",
            "secret",
            "changeme",
            "replace-me-with-64-hex-chars",
        }
        if v.lower() in forbidden:
            raise ValueError("Використання шаблонного або слабкого JWT_SECRET_KEY заборонено!")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
