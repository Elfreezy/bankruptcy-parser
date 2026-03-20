import os
import logging

from pydantic_settings import SettingsConfigDict, BaseSettings

CURRENT_DIR = os.path.dirname(__file__)


class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(CURRENT_DIR, ".env"),
            os.path.join(CURRENT_DIR, ".env.dev"),
        ),
        extra="ignore",
    )


def configure_logging(level):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)s - %(message)s",
    )


settings = Settings()
