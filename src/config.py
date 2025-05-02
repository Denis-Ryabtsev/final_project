from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


#   class, include enviroment data
class Setting(BaseSettings):
    DB_POSTGRES_HOST: str
    DB_POSTGRES_PORT: str
    DB_POSTGRES_NAME: str
    DB_POSTGRES_USER: str
    DB_POSTGRES_PASS: str

    SECRET: str

    #   property for get DSN link (for sqlalchemy)
    @property
    def DB_POSTGRES_URL(self) -> str:
        return (
            f'postgresql+asyncpg://{self.DB_POSTGRES_USER}:{self.DB_POSTGRES_PASS}'\
            f'@{self.DB_POSTGRES_HOST}:{self.DB_POSTGRES_PORT}/{self.DB_POSTGRES_NAME}'
        )
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / '.env'
    )


def get_setting() -> Setting:
    return Setting()