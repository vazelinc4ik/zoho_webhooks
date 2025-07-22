from pydantic_settings import BaseSettings, SettingsConfigDict

class Base(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="ignore")

class ZohoSettings(Base):
    client_id: str
    client_secret: str
    zoho_inventory_adjustment_secret: str
    zoho_fbm_sales_secret: str
    zoho_purchase_secret: str
    zoho_transfer_secret: str
    zoho_callback_uri: str
    zoho_warehouse_id: str
    ecwid_customer_id: str

class DatabaseSettings(Base):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

class EcwidSettings(Base):
    ecwid_app_secret: str
    ecwid_store_id: int

class Settings:
    zoho_settings = ZohoSettings()
    database_settings = DatabaseSettings()
    ecwid_settings = EcwidSettings()

settings = Settings()
