from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд'
    database_url: str

    class Config:
        env_file = '.env'


settings = Settings()