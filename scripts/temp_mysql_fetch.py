import os

from jcutils.client import MySqlClient

MYSQL_TEST_DB = os.getenv("MYSQL_TEST_DB", default="")
MYSQL_TEST_USER = os.getenv("MYSQL_TEST_USER", default="")
MYSQL_TEST_PASSWD = os.getenv("MYSQL_TEST_PASSWD", default="")
MYSQL_TEST_DB = os.getenv("MYSQL_TEST_DB", default="")
MYSQL_TEST_PORT = os.getenv("MYSQL_TEST_PORT", default="")

# 创建连接池客户端（此时不会创建任何连接池）
mysql_client = MySqlClient(
    host=MYSQL_TEST_DB,
    user=MYSQL_TEST_USER,
    passwd=MYSQL_TEST_PASSWD,
    db=MYSQL_TEST_DB,
    port=MYSQL_TEST_PORT,
)

# 首次普通查询时创建普通连接池
sql = "select * from user limit 1"
result = mysql_client.fetchone(sql)
print("fetchone:", result)
