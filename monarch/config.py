from pydantic import BaseModel, HttpUrl
import os

class Settings(BaseModel):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    GITHUB_API_URL: HttpUrl = "https://api.github.com"
    GITHUB_TOKEN: str = os.getenv("GITHUB_PAT")
    GITHUB_RATE_LIMIT_PAUSE: int = 5  # seconds
    REPO_MIGRATION_PAUSE: int = 300    # seconds
    TEMPLATE_DIR: str = os.path.dirname(os.path.realpath(__file__))

    class Config:
        env_file = ".env"