from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    api_key: str = os.environ.get("YOUR_ALPHA_VANTAGE_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()