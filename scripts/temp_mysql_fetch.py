from config.loader import mysql_db1
from src.jcutils.client.mysql_client import MySqlClient

# 创建连接池客户端（此时不会创建任何连接池）
mysql_client = MySqlClient(conn_config=mysql_db1)

# 首次普通查询时创建普通连接池
sql = "select * from user limit 1"
result = mysql_client.fetchone(sql)
print("fetchone:", result)
