from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Snap Card API"
    database_url: str = "sqlite:///./snapcard.db"
    jwt_secret_key: str = "snapcard_secret_key_dev_mode_38df72983ba019a28bc"
    jwt_expire_minutes: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
