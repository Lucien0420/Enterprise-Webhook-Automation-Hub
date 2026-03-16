"""Environment variables and app settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Manages env vars via pydantic-settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    api_key: str
    discord_webhook_url: str
    alert_threshold: float = 1000.0
    database_url: str = "sqlite:///./data/webhook_orders.db"
    rate_limit_per_minute: int = 60


settings = Settings()
