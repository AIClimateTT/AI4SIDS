from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        # This allows loading from .env file
        env_file=".env",
        # If True, will not raise errors for missing values in .env
        env_file_optional=True,
        # If True, will allow extra fields in .env
        extra='allow',
        # Use environment variables even if they're empty
        env_ignore_empty=False,
    )
    # Database
    DATABASE_URL: str = "sqlite:///./ai4sids_demo.db"

    # Auth
    SECRET_KEY: str = "changeme-please-set-a-real-secret-in-env"
    DEFAULT_USER_EMAIL: str = "researcher@ai4sids.org"
    DEFAULT_USER_PASSWORD: str = "demo2024"
    SUPERADMIN_EMAIL: str = "admin@ai4sids.org"
    SUPERADMIN_PASSWORD: str = "change-me-now"
    SEED_DEMO_ORGS: bool = False

    # Demo settings
    DATA_CYCLE_INTERVAL: int = 15

    # API settings
    API_TITLE: str = "AI4SIDS Real-Time Flood Monitoring API"
    API_VERSION: str = "2.0.0"

    ENABLE_BACKGROUND_TASK: bool = False
    

# Create settings instance with environment-specific configs
# @lru_cache
def get_settings() -> Settings:
    """
    Get settings with environment-specific values.
    Using lru_cache to prevent multiple reads of the .env file
    """
    return Settings()

# Create a single instance to be imported
settings = get_settings()
