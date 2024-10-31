from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "dev")

    @property
    def database_url(self) -> str:
        if self.ENV == "test":
            return "sqlite:///test.db"
        return "sqlite:///database.db"


settings = Settings()
