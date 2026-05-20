"""
@File    :   presto_client.py
@Time    :   2016/08/05
@Author  :   lijc210@163.com
@Desc    :
Presto (Trino) 连接客户端，内部使用 with 上下文管理器自动管理连接
支持普通查询和流式查询
"""

from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union

try:
    from pyhive import presto
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install pyhive or uv add "pyhive"')
except Exception as e:
    raise ImportError(f"pyhive 导入失败: {e}")


class PrestoClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        username: str = "default",
        password: Optional[str] = None,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        protocol: str = "http",
        source: Optional[str] = None,
        session_properties: Optional[Dict[str, Any]] = None,
        cursorclass: str = "tuple",
    ) -> None:
        """
        Presto 连接客户端

        :param host: 主机地址，默认 localhost
        :param port: 端口号，默认 8080
        :param username: 用户名，默认 default
        :param password: 密码
        :param catalog: catalog 名称
        :param schema: schema 名称
        :param protocol: 协议，默认 http
        :param source: 数据源名称
        :param session_properties: 会话属性
        :param cursorclass: 游标类型，tuple/dict
        """
        self.host = host
        self.port = port
        self.username = username
        self.catalog = catalog
        self.schema = schema
        self.cursorclass = cursorclass

        # 其他可选连接参数
        self.password = password
        self.protocol = protocol
        self.source = source
        self.session_properties = session_properties

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
    # 创建 Presto 客户端（默认使用 tuple 游标）
    presto_client = PrestoClient(
        host="10.10.23.11",
        port=8444,
        username="lijicong",
        catalog="hive",
        schema="dw",
    )

    # 查询单条记录（tuple 格式）
    sql = "SELECT * FROM dw.ol_cms_display_amount LIMIT 1"
    result = presto_client.fetchone(sql)
    print("fetchone:", result)

    # 使用 dict 游标类型
    presto_client_dict = PrestoClient(
        host="10.10.23.11",
        port=8444,
        username="lijicong",
        catalog="hive",
        schema="dw",
        cursorclass="dict",
    )

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
