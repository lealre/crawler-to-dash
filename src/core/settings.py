from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='allow'
    )

    MONGO_HOST: str = 'localhost'
    MONGO_PORT: int = 27017
    MONGO_DATABASE: str = 'scraper_db'
    MONGO_TIMEOUT: int = 7000

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str

    USE_STORAGE_LOCAL: bool = False
    USE_STORAGE_MONGO: bool = False
    USE_STORAGE_AWS_S3: bool = False

    LOCAL_BACKUP_PATH: str

    DASH_COLLECTION: str = 'dash'


settings = Settings()
