from pydantic import BaseSettings


def get_settings() -> object:
    return Settings()


def get_db_settings() -> object:
    return DBSettings()


class Settings(BaseSettings):
    SALT: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"


class DBSettings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    class Config:
        env_file = ".env"
