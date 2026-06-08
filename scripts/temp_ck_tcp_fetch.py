import os

from jcutils.client import ClickhouseClient

DATABASES_CK1_DB_HOST = os.getenv("DATABASES_CK1_DB_HOST", default="")
DATABASES_CK1_DB_USER = os.getenv("DATABASES_CK1_DB_USER", default="")
DATABASES_CK1_DB_PASSWD = os.getenv("DATABASES_CK1_DB_PASSWD", default="")
DATABASES_CK1_DB_DB = os.getenv("DATABASES_CK1_DB_DB", default="")
DATABASES_CK1_DB_PORT = os.getenv("DATABASES_CK1_DB_PORT", default="")


# 创建连接池客户端（此时不会创建任何连接池）
mysql_client = ClickhouseClient(
    host=DATABASES_CK1_DB_HOST,
    user=DATABASES_CK1_DB_USER,
    passwd=DATABASES_CK1_DB_PASSWD,
    db=DATABASES_CK1_DB_DB,
    port=int(DATABASES_CK1_DB_PORT),
)

# 首次普通查询时创建普通连接池
sql = """
select member_code_all
from dm_member_info_label_ext b
where version >='20260608000000' and is_delete =0
limit 10
"""
result = mysql_client.fetchall(sql)
print("fetchall:", result)
