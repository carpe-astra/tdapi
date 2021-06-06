"""User config settings"""

from pydantic import BaseSettings


class UserConfig(BaseSettings):
    account_id: int
    consumer_key: str
    redirect_uri: str

    class Config:
        env_file = ".env"


user_config = UserConfig()
