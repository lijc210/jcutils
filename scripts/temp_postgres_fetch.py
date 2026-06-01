import asyncio
import os

from jcutils.client import AsyncPostgresClient

POSTGRES_TEST_HOST = os.getenv("POSTGRES_TEST_HOST", default="")
POSTGRES_TEST_USER = os.getenv("POSTGRES_TEST_USER", default="")
POSTGRES_TEST_PASSWD = os.getenv("POSTGRES_TEST_PASSWD", default="")
POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB", default="")
POSTGRES_TEST_PORT = int(os.getenv("POSTGRES_TEST_PORT", default="5432"))


# 创建连接池客户端（此时不会创建任何连接池）
postgres_client = AsyncPostgresClient(
    host=POSTGRES_TEST_HOST,
    user=POSTGRES_TEST_USER,
    passwd=POSTGRES_TEST_PASSWD,
    db=POSTGRES_TEST_DB,
    port=POSTGRES_TEST_PORT,
)


async def main():
    # 首次普通查询时创建普通连接池
    sql = "select * from information_schema.sql_implementation_info limit 1"
    result = await postgres_client.fetchone(sql)
    print("fetchone:", result)


if __name__ == "__main__":
    asyncio.run(main())
