from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(alias="mongo_url")
    DB_NAME: str = Field(alias="mongo_database")
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Le decimos a Pydantic que lea las variables del archivo .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Creamos una instancia de la configuración que usaremos en toda la app
settings = Settings()
