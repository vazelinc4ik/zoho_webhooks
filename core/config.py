from pydantic_settings import BaseSettings, SettingsConfigDict

class Base(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="ignore")

class Settings(Base):
    client_id: str
    client_secret: str

settings = Settings()
