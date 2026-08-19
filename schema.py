from pydantic import BaseModel


class AppConfig(BaseModel):
    APP_ID: str
    ENV: str
    PYTHONPATH: str