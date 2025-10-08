from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./ai4sids_demo.db"
    
    # Demo settings
    data_interval_seconds: int = 15
    
    # API settings
    api_title: str = "AI4SIDS Real-Time Demo API"
    api_version: str = "2.0.0"
    
    class Config:
        env_file = ".env"


settings = Settings()
