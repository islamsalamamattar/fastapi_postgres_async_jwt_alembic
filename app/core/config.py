from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


# Load environmental variables from the .env file
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRES_MINUTES = int(os.environ.get('REFRESH_TOKEN_EXPIRES_MINUTES'))
DATABASE_URL = os.environ.get('DATABASE_URL')
debug_logs = os.environ.get('debug_logs')

class Settings(BaseSettings):
    database_url: str
    echo_sql: bool = True
    test: bool = False
    project_name: str = "My FastAPI project"
    oauth_token_secret: str = "my_dev_secret"


settings = Settings()  # type: ignore
