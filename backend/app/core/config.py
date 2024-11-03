from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

#class Settings(BaseSettings):
 #   api_key: str = os.environ.get("YOUR_ALPHA_VANTAGE_API_KEY")
#
 #   class Config:
  #      env_file = ".env"

class Settings(BaseSettings):
    neo4j_uri: str = "neo4j+s://1743086b.databases.neo4j.io"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "WyHIDZmBEQIHiKUktr77A3zihyUb50TxAVl6t6a0QPU"

settings = Settings()