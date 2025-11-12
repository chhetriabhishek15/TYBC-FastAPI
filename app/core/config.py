from functools import lru_cache
from pydantic import HttpUrl, computed_field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "YouCanBeChef"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENV : str
    
    # Database settings
    DATABASE_URL_DEV : Optional[str]
    DATABASE_URL_TEST : Optional[str]
    
    # Redis settings
    REDIS_URL : str

    # Security
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int


    #SMTP
    SMTP_HOST : str
    SMTP_PORT : int
    SMTP_USER : str
    SERVER_PASSWORD : str
    SMTP_FROM : str

    #URL
    BACKEND_URL : HttpUrl

    class Config:
        env_file = ".env"
        case_sensitive = True

    @computed_field
    def DATABASE_URL(self)-> str:
        """Selects the correct database URL based on the ENV setting."""
        try:
            if self.ENV == "dev":
                return self.DATABASE_URL_DEV
            
            elif self.ENV == "test":
                return self.DATABASE_URL_TEST
            
            # Handle cases where ENV is not "dev" or "test"
            else:
                raise ValueError(f"Unsupported environment: {self.ENV}. Must be 'dev' or 'test'.")

        except Exception as e:
            print(f"Error selecting database URL: {e}")
            raise


@lru_cache
def get_settings():
    return Settings()