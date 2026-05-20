"""
@File    :   clickhouse_connect_client.py
@Desc    :
ClickHouse 连接客户端，使用 clickhouse-connect（HTTP 协议）
对编码问题容错更好，是官方推荐的 Python 客户端
pip install clickhouse-connect
"""

from typing import Any, Dict, Generator, Optional, Sequence, Tuple, Union

try:
    import clickhouse_connect
    from clickhouse_connect.driver.client import Client
except ImportError:
    raise ImportError("请先安装：pip install clickhouse-connect")


class ClickhouseConnectClient:
    def __init__(
        self,
        host: str = "127.0.0.1",
        user: str = "default",
        passwd: str = "",
        db: str = "default",
        port: int = 8123,
        secure: bool = False,
        max_execution_time: int = 420,
    ) -> None:
        """
        ClickHouse 连接客户端（clickhouse-connect HTTP 协议）

        :param host: 主机地址
        :param user: 用户名
        :param passwd: 密码
        :param db: 数据库名
        :param port: 端口号，HTTP 默认 8123，HTTPS 默认 8443
        :param secure: 是否使用 HTTPS
        :param max_execution_time: 最大执行时间（秒）
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.port = port
        self.secure = secure
        self.max_execution_time = max_execution_time

    def get_client(self) -> Client:
        """
        获取一个客户端连接

        :return: clickhouse_connect Client 对象
        """
        return clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.passwd,
            database=self.db,
            secure=self.secure,
            settings={"max_execution_time": self.max_execution_time},
        )

    def fetchone(
        self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        查询单条记录，返回字典
        :param sql: SQL 语句
        :param args: 参数化查询的参数
        :return: 单条记录字典，无结果返回 None
        """
        client = self.get_client()
        try:
            result = client.query(sql, parameters=args)
            if not result.result_rows:
                return None
            # 将第一行组合成字典
            return dict(zip(result.column_names, result.result_rows[0]))
        finally:
            client.close()

    def fetchmany(
        self,
        sql: str,
        batch_size: int = 100,
        args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
    ) -> Generator[Sequence[Dict[str, Any]], None, None]:
        """
        分批获取所有数据，每批返回一次（字典列表）

        :param sql: SQL 语句
        :param batch_size: 每批的数量，默认 100
        :param args: 参数化查询的参数
        :return: 生成器，每次返回一批字典列表
        """
        client = self.get_client()
        try:
            result = client.query(sql, parameters=args)
            columns = result.column_names
            rows = result.result_rows
            for i in range(0, len(rows), batch_size):
                batch = rows[i : i + batch_size]
                yield [dict(zip(columns, row)) for row in batch]
        finally:
            client.close()

    def fetchall(
        self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Sequence[Dict[str, Any]]:
        """
        查询所有记录，返回字典列表
        :param sql: SQL 语句
        :param args: 参数化查询的参数
        :return: 所有记录的字典列表
        """
        client = self.get_client()
        try:
            result = client.query(sql, parameters=args)
            columns = result.column_names
            return [dict(zip(columns, row)) for row in result.result_rows]
        finally:
            client.close()

    def fetch_iter(
        self,
        sql: str,
        batch_size: int = 1000,
        args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式查询，返回大数量时使用，逐条 yield 避免内存溢出
        :param sql: SQL 语句
        :param batch_size: 内部分批大小，默认 1000
        :param args: 参数化查询的参数
        :return: 生成器，每次 yield 一条字典记录
        """
        client = self.get_client()
        try:
            # query_column_block_stream 按 block 流式读取，内存友好
            with client.query_column_block_stream(sql, parameters=args) as stream:
                columns = stream.source.column_names
                for block in stream:
                    # block 是按列存储的，转置成行
                    rows = zip(*block)
                    for row in rows:
                        yield dict(zip(columns, row))
        finally:
            client.close()

    def execute(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> Any:
        """
        执行 SQL 语句（INSERT/ALTER/CREATE/DROP 等）
        :param sql: SQL 语句
        :param args: 参数化查询的参数
        :return: clickhouse_connect QuerySummary 对象
        """
        client = self.get_client()
        try:
            return client.command(sql, parameters=args)
        except Exception as e:
            raise e
        finally:
            client.close()

    def executemany(self, sql: str, data: Sequence[Sequence[Any]], column_names: Sequence[str]) -> Any:
        """
        批量插入数据
        :param sql: 目标表名（如 'my_table'）或完整 INSERT SQL
        :param data: 数据列表，如 [['a','b'], ['c','d']]
        :param column_names: 列名列表，如 ['col1', 'col2']
        :return: QuerySummary 对象
        """
        client = self.get_client()
        try:
            return client.insert(sql, data=data, column_names=column_names)
        except Exception as e:
            raise e
        finally:
            client.close()


if __name__ == "__main__":
    import os

    DATABASES_JDBC_CK1_DB_HOST = os.environ.get("DATABASES_JDBC_CK1_DB_HOST", "")
    DATABASES_JDBC_CK1_DB_USER = os.environ.get("DATABASES_JDBC_CK1_DB_USER", "")
    DATABASES_JDBC_CK1_DB_PASSWD = os.environ.get("DATABASES_JDBC_CK1_DB_PASSWD", "")
    DATABASES_JDBC_CK1_DB_DB = os.environ.get("DATABASES_JDBC_CK1_DB_DB", "")
    DATABASES_JDBC_CK1_DB_PORT = os.environ.get("DATABASES_JDBC_CK1_DB_PORT", 9000)

    client = ClickhouseConnectClient(
        host=DATABASES_JDBC_CK1_DB_HOST,
        user=DATABASES_JDBC_CK1_DB_USER,
        passwd=DATABASES_JDBC_CK1_DB_PASSWD,
        db=DATABASES_JDBC_CK1_DB_DB,
        port=int(DATABASES_JDBC_CK1_DB_PORT),
    )

    # 查询单条
    result = client.fetchone("SELECT * FROM system.tables LIMIT 1")
    print("fetchone:", result)

    # 分批获取
    total = 0
    for batch in client.fetchmany("SELECT * FROM system.tables LIMIT 25", batch_size=5):
        print("当前批次数量:", len(batch))
        total += len(batch)
    print("fetchmany total:", total)

    # 查询所有
    results = client.fetchall("SELECT * FROM system.tables LIMIT 10")
    print("fetchall count:", len(results))

    # 流式查询
    count = 0
    for row in client.fetch_iter("SELECT * FROM system.tables LIMIT 10"):
        # print(row)
        count += 1
    print("fetch_iter:", count)
