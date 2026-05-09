from config.loader import config
from src.jcutils.client.postgres_client import PostgresClient

# 创建连接池客户端（此时不会创建任何连接池）
postgres_client = PostgresClient(conn_config=config.postgres.db1)

# 首次普通查询时创建普通连接池
sql = "select * from information_schema.sql_implementation_info limit 1"
result = postgres_client.fetchone(sql)
print("fetchone:", result)
