from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Le decimos a Pydantic que lea las variables del archivo .env
    model_config = SettingsConfigDict(env_file=".env")

# Creamos una instancia de la configuración que usaremos en toda la app
settings = Settings()