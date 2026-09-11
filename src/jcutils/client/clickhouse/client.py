"""
@File    :   clickhouse_client.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :
ClickHouse 连接客户端，内部使用 with 上下文管理器自动管理连接
支持普通查询和流式查询
"""

import os
from typing import Any, Dict, Generator, Optional, Sequence, Tuple, Union

try:
    from clickhouse_driver import connect  # type: ignore
    from clickhouse_driver.dbapi.extras import DictCursor  # type: ignore
except ModuleNotFoundError:
    raise ImportError("请先安装：pip install clickhouse-driver or uv add clickhouse-driver")
except Exception as e:
    raise ImportError(f"clickhouse_driver 导入失败: {e}")


class ClickhouseClient:
    def __init__(
        self,
        host: str = "",
        user: str = "",
        passwd: str = "",
        db: str = "",
        port: int = 9000,
        charset: str = "utf8",
        cursorclass: str = "dict",
        max_execution_time: int = 420,
    ) -> None:
        """
        ClickHouse 连接客户端

        :param host: 主机地址
        :param user: 用户名
        :param passwd: 密码
        :param db: 数据库名
        :param port: 端口号，默认 9000
        :param charset: 字符集，默认 utf8
        :param cursorclass: 游标类型，dict/普通
        :param max_execution_time: 最大执行时间（秒）
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.charset = charset
        self.port = port
        self.cursorclass = cursorclass
        self.max_execution_time = max_execution_time

    def get_connection(self) -> Any:
        """
        获取一个数据库连接

        :return: 连接对象
        """
        conn = connect(
            host=self.host,
            user=self.user,
            password=self.passwd,
            database=self.db,
            port=self.port,
            settings={"max_execution_time": self.max_execution_time},
        )
        return conn

    def get_cursor(self, conn: Any) -> Any:
        """
        根据配置获取游标

        :param conn: 数据库连接
        :return: 游标对象
        """
        if self.cursorclass == "dict":
            cursor = conn.cursor(DictCursor)
        else:
            cursor = conn.cursor()
        return cursor

    def fetchone(
        self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Optional[Union[Dict[str, Any], Tuple[Any, ...]]]:
        """
        查询单条记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 单条记录
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                result = cursor.fetchone()
                return result
            finally:
                cursor.close()

    def fetchmany(
        self, sql: str, batch_size: int = 100, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Generator[Any, None, None]:
        """
        分批获取所有数据，每批返回一次

        :param sql: SQL 语句
        :param batch_size: 每批的数量，默认 100
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，每次返回一批数据
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                while True:
                    batch = cursor.fetchmany(batch_size)
                    if not batch:
                        break
                    yield batch
            finally:
                cursor.close()

    def fetchall(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> Sequence[Any]:
        """
        查询所有记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                results = cursor.fetchall()
                return results
            finally:
                cursor.close()

    def fetch_iter(
        self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Generator[Any, None, None]:
        """
        流式查询，使用原生 execute_iter 按 block 流式推送，不会将全量数据加载到内存。
        逐批获取数据，避免内存溢出
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，可以迭代获取每条记录
        """
        with self.get_connection() as conn:
            # 原生 Client 对象
            native_client = conn._make_client()
            query_iter = native_client.execute_iter(
                sql,
                params=args or {},
                with_column_types=True,
            )
            # 第一个元素固定是列元数据 [(col_name, col_type), ...]
            try:
                columns_with_types = next(query_iter)
                column_names = [col[0] for col in columns_with_types]
            except StopIteration:
                return

            for row in query_iter:
                if self.cursorclass == "dict":
                    yield dict(zip(column_names, row))
                else:
                    yield row

    def execute(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> int:
        """
        执行 SQL 语句（insert/update/delete 等）
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                result = cursor.execute(sql, args)
                # ClickHouse 不支持事务，无需 commit
                return result
            except Exception as e:
                raise e
            finally:
                cursor.close()

    def executemany(self, sql: str, sqlDataList: Sequence[Sequence[Any]]) -> int:
        """
        批量执行 SQL 语句
        :param sql: SQL 语句
        :param sqlDataList: 数据列表，如 [['a','b','c'], ['d','f','e']]
        :return: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                result = cursor.executemany(sql, sqlDataList)
                # ClickHouse 不支持事务，无需 commit
                return result
            except Exception as e:
                raise e
            finally:
                cursor.close()


if __name__ == "__main__":
    DATABASES_CK1_DB_HOST = os.environ.get("DATABASES_CK1_DB_HOST", "")
    DATABASES_CK1_DB_USER = os.environ.get("DATABASES_CK1_DB_USER", "")
    DATABASES_CK1_DB_PASSWD = os.environ.get("DATABASES_CK1_DB_PASSWD", "")
    DATABASES_CK1_DB_DB = os.environ.get("DATABASES_CK1_DB_DB", "")
    DATABASES_CK1_DB_PORT = os.environ.get("DATABASES_CK1_DB_PORT", 9000)

    # 创建连接池客户端
    ck_client = ClickhouseClient(
        host=DATABASES_CK1_DB_HOST,
        user=DATABASES_CK1_DB_USER,
        passwd=DATABASES_CK1_DB_PASSWD,
        db=DATABASES_CK1_DB_DB,
        port=int(DATABASES_CK1_DB_PORT),
    )

    # 查询单条记录
    sql = "SELECT * FROM system.tables LIMIT 1"
    result = ck_client.fetchone(sql)
    print("fetchone:", result)

    # 分批获取数据
    total_count = 0
    for batch in ck_client.fetchmany("SELECT * FROM system.tables LIMIT 25", batch_size=5):
        print("当前批次数量:", len(batch))
        total_count += len(batch)
    print("fetchmany total:", total_count)

    # 查询所有记录
    sql = "SELECT * FROM system.tables LIMIT 10"
    results = ck_client.fetchall(sql)
    print("fetchall count:", len(results))

    # 流式查询
    count = 0
    for row in ck_client.fetch_iter("SELECT * FROM system.tables LIMIT 10"):
        count += 1
    print("fetch_iter:", count)
