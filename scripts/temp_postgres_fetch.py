from jcutils.client import PostgresClient
from jcutils.utils import app_config as CONFIG

# 创建连接池客户端（此时不会创建任何连接池）
postgres_client = PostgresClient(
    host=CONFIG.POSTGRES_TEST_DB,
    user=CONFIG.POSTGRES_TEST_USER,
    passwd=CONFIG.POSTGRES_TEST_PASSWD,
    db=CONFIG.POSTGRES_TEST_DB,
    port=CONFIG.POSTGRES_TEST_PORT,
)

# 首次普通查询时创建普通连接池
sql = "select * from information_schema.sql_implementation_info limit 1"
result = postgres_client.fetchone(sql)
print("fetchone:", result)
