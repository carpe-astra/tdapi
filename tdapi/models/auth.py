"""Models for auth objects"""

from pydantic import BaseModel


class EASObject(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = ""
    expires_in: int = 0
    scope: str = ""
    refresh_token_expires_in: int = 0
