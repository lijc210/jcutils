"""
@File    :   presto_client.py
@Time    :   2016/08/05
@Author  :   lijc210@163.com
@Desc    :
Presto (Trino) 连接客户端，内部使用 with 上下文管理器自动管理连接
支持普通查询和流式查询
"""

from typing import Any, Dict, Generator, List, Optional, Protocol, Sequence, Tuple, Union

from pyhive import presto


class ConnectionConfig(Protocol):
    """连接配置协议接口（所有属性均为可选）"""

    host: Optional[str]
    port: Optional[int]
    username: Optional[str]
    password: Optional[str]
    catalog: Optional[str]
    schema: Optional[str]
    protocol: Optional[str]
    source: Optional[str]
    session_properties: Optional[Dict[str, Any]]


class PrestoClient:
    def __init__(
        self,
        conn_config: ConnectionConfig,
        cursorclass: str = "tuple",
    ) -> None:
        """
        Presto 连接客户端

        :param conn_config: 连接配置对象（符合 ConnectionConfig 协议），包含 host, port, username, catalog, schema 等
        :param cursorclass: 游标类型，tuple/dict
        """
        self.host = conn_config.host or "localhost"
        self.port = conn_config.port or 8080
        self.username = conn_config.username or "default"
        self.catalog = conn_config.catalog
        self.schema = conn_config.schema
        self.cursorclass = cursorclass

        # 其他可选连接参数
        self.password = conn_config.password
        self.protocol = conn_config.protocol or "http"
        self.source = conn_config.source
        self.session_properties = conn_config.session_properties

    def get_connection(self) -> Any:
        """
        获取一个数据库连接

        :return: 连接对象
        """
        conn_kwargs = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
        }

        # 可选参数
        if self.password:
            conn_kwargs["password"] = self.password
        if self.catalog:
            conn_kwargs["catalog"] = self.catalog
        if self.schema:
            conn_kwargs["schema"] = self.schema
        if self.protocol:
            conn_kwargs["protocol"] = self.protocol
        if self.source:
            conn_kwargs["source"] = self.source
        if self.session_properties:
            conn_kwargs["session_properties"] = self.session_properties

        conn = presto.connect(**conn_kwargs)
        return conn

    def get_cursor(self, conn: Any) -> Any:
        """
        根据配置获取游标

        :param conn: 数据库连接
        :return: 游标对象
        """
        cursor = conn.cursor()
        return cursor

    def _convert_to_dict(self, cursor: Any, results: List[Tuple[Any, ...]]) -> List[Dict[str, Any]]:
        """
        将查询结果转换为字典列表

        :param cursor: 游标对象
        :param results: 查询结果（元组列表）
        :return: 字典列表
        """
        if not cursor.description:
            return []
        desc = [field[0] for field in cursor.description]
        return [dict(zip(desc, row, strict=True)) for row in results]

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

                # 如果需要返回字典格式
                if self.cursorclass == "dict" and result is not None:
                    if cursor.description:
                        desc = [field[0] for field in cursor.description]
                        return dict(zip(desc, result, strict=True))
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

                    # 如果需要返回字典格式
                    if self.cursorclass == "dict":
                        yield self._convert_to_dict(cursor, batch)
                    else:
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

                # 如果需要返回字典格式
                if self.cursorclass == "dict":
                    return self._convert_to_dict(cursor, results)
                return results
            finally:
                cursor.close()

    def fetch_iter(
        self, sql: str, batch_size: int = 1000, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Generator[Any, None, None]:
        """
        流式查询，需要返回大数量时使用
        逐批获取数据，避免内存溢出
        :param sql: SQL 语句
        :param batch_size: 每批获取的记录数，默认 1000
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，可以迭代获取每条记录
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                while True:
                    results = cursor.fetchmany(batch_size)
                    if not results:
                        break

                    # 如果需要返回字典格式
                    if self.cursorclass == "dict":
                        results = self._convert_to_dict(cursor, results)

                    for row in results:
                        yield row
            finally:
                cursor.close()

    def execute(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> int:
        """
        执行 SQL 语句（insert/update/delete 等）
        Presto 主要用于查询，支持的数据操作有限
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                result = cursor.execute(sql, args)
                # Presto 不支持事务，无需 commit
                return result
            except Exception as e:
                raise e
            finally:
                cursor.close()

    def executemany(self, sql: str, sqlDataList: Sequence[Sequence[Any]]) -> int:
        """
        批量执行 SQL 语句
        Presto 主要用于查询，批量插入操作有限
        :param sql: SQL 语句
        :param sqlDataList: 数据列表，如 [['a','b','c'], ['d','f','e']]
        :return: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                result = cursor.executemany(sql, sqlDataList)
                # Presto 不支持事务，无需 commit
                return result
            except Exception as e:
                raise e
            finally:
                cursor.close()


if __name__ == "__main__":
    from types import SimpleNamespace

    # 使用 SimpleNamespace 创建配置对象
    presto_config = SimpleNamespace(
        host="10.10.23.11",
        port=8444,
        username="lijicong",
        catalog="hive",
        schema="dw",
    )  # type: ignore[assignment]

    # 创建 Presto 客户端（默认使用 tuple 游标）
    presto_client = PrestoClient(conn_config=presto_config)  # type: ignore[arg-type]

    # 查询单条记录（tuple 格式）
    sql = "SELECT * FROM dw.ol_cms_display_amount LIMIT 1"
    result = presto_client.fetchone(sql)
    print("fetchone:", result)

    # 使用 dict 游标类型
    presto_client_dict = PrestoClient(conn_config=presto_config, cursorclass="dict")  # type: ignore[arg-type]

    # 查询单条记录（dict 格式）
    result = presto_client_dict.fetchone(sql)
    print("fetchone (dict):", result)

    # 分批获取数据
    total_count = 0
    for batch in presto_client_dict.fetchmany("SELECT * FROM dw.ol_cms_display_amount LIMIT 25", batch_size=5):
        print("当前批次数量:", len(batch))
        total_count += len(batch)
    print("fetchmany total:", total_count)

    # 查询所有记录
    results = presto_client_dict.fetchall("SELECT * FROM dw.ol_cms_display_amount LIMIT 10")
    print("fetchall count:", len(results))

    # 流式查询
    count = 0
    for row in presto_client_dict.fetch_iter("SELECT * FROM dw.ol_cms_display_amount LIMIT 10"):
        count += 1
    print("fetch_iter:", count)

    # 兼容旧版 API
    results = presto_client.query(sql)
    print("query count:", len(results))

    results_dict = presto_client.queryDict(sql)
    print("queryDict count:", len(results_dict))
