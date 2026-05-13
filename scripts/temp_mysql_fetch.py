from jcutils.client import MySqlClient
from jcutils.utils import ConfigLoader

CONFIG = ConfigLoader.load_config()

# 创建连接池客户端（此时不会创建任何连接池）
mysql_client = MySqlClient(
    host=CONFIG.MYSQL_TEST_DB,
    user=CONFIG.MYSQL_TEST_USER,
    passwd=CONFIG.MYSQL_TEST_PASSWD,
    db=CONFIG.MYSQL_TEST_DB,
    port=CONFIG.MYSQL_TEST_PORT,
)

# 首次普通查询时创建普通连接池
sql = "select * from user limit 1"
result = mysql_client.fetchone(sql)
print("fetchone:", result)
