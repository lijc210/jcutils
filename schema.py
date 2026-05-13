from pydantic import BaseModel
from typing import Optional


class AppConfig(BaseModel):
    APP_NAME: str = ""
    ENV: str = ""
    MYSQL_TEST_CONNECT_TIMEOUT: Optional[int] = None
    MYSQL_TEST_DB: Optional[str] = None
    MYSQL_TEST_HOST: Optional[str] = None
    MYSQL_TEST_MAX_CONNECTIONS: Optional[int] = None
    MYSQL_TEST_MIN_CONNECTIONS: Optional[int] = None
    MYSQL_TEST_PASSWD: Optional[str] = None
    MYSQL_TEST_PORT: Optional[int] = None
    MYSQL_TEST_USER: Optional[str] = None
    POSTGRES_TEST_CONNECT_TIMEOUT: Optional[int] = None
    POSTGRES_TEST_DB: Optional[str] = None
    POSTGRES_TEST_HOST: Optional[str] = None
    POSTGRES_TEST_MAX_CONNECTIONS: Optional[int] = None
    POSTGRES_TEST_MIN_CONNECTIONS: Optional[int] = None
    POSTGRES_TEST_PASSWD: Optional[str] = None
    POSTGRES_TEST_PORT: Optional[int] = None
    POSTGRES_TEST_USER: Optional[str] = None