from pydantic_settings import BaseSettings, SettingsConfigDict

class Base(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="ignore")

class ZohoSettings(Base):
    client_id: str
    client_secret: str
    zoho_inventory_adjustment_secret: str
    zoho_fbm_sales_secret: str

class Settings(Base):
    zoho_settings: ZohoSettings

settings = Settings()
