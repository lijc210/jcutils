import os

from jcutils.client import MsSqlClient

DATABASES_MSSQL_DB_HOST = os.getenv("DATABASES_MSSQL_DB_HOST", default="")
DATABASES_MSSQL_DB_USER = os.getenv("DATABASES_MSSQL_DB_USER", default="")
DATABASES_MSSQL_DB_PASSWD = os.getenv("DATABASES_MSSQL_DB_PASSWD", default="")
DATABASES_MSSQL_DB_DB = os.getenv("DATABASES_MSSQL_DB_DB", default="")
DATABASES_MSSQL_DB_PORT = os.getenv("DATABASES_MSSQL_DB_PORT", default="")

mssql_db_client = MsSqlClient(
    host=DATABASES_MSSQL_DB_HOST,
    user=DATABASES_MSSQL_DB_USER,
    passwd=DATABASES_MSSQL_DB_PASSWD,
    db=DATABASES_MSSQL_DB_DB,
    port=DATABASES_MSSQL_DB_PORT,
)

sql = "select top 10 * from dbo.t_pur_requisition"
print(mssql_db_client.fetchall(sql))
