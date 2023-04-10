from pydantic import BaseSettings


def get_settings() -> object:
    return Settings()


class Settings(BaseSettings):
    SALT: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
