from pydantic import BaseModel


class AppConfig(BaseModel):
    MYSQL_TEST_CONNECT_TIMEOUT: int = 30
    MYSQL_TEST_DB: str = 'mysql'
    MYSQL_TEST_HOST: str = '127.0.0.1'
    MYSQL_TEST_MAX_CONNECTIONS: int = 10
    MYSQL_TEST_MIN_CONNECTIONS: int = 2
    MYSQL_TEST_PASSWD: str = 'passwd'
    MYSQL_TEST_PORT: int = 3306
    MYSQL_TEST_USER: str = 'user'
    POSTGRES_TEST_CONNECT_TIMEOUT: int = 30
    POSTGRES_TEST_DB: str = 'postgres'
    POSTGRES_TEST_HOST: str = '127.0.0.1'
    POSTGRES_TEST_MAX_CONNECTIONS: int = 10
    POSTGRES_TEST_MIN_CONNECTIONS: int = 2
    POSTGRES_TEST_PASSWD: str = 'passwd'
    POSTGRES_TEST_PORT: int = 5432
    POSTGRES_TEST_USER: str = 'user'
    TEST: str = 'test1'