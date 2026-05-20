"""
@File    :   PyodbcClient.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :
SQL Server ODBC 连接客户端，内部使用 with 上下文管理器自动管理连接
支持普通查询和流式查询
"""

from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union

try:
    import pyodbc  # type: ignore
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install pyodbc or uv add "pyodbc"')
except Exception as e:
    raise ImportError(f"pyodbc 导入失败: {e}")


class PyodbcClient:
    def __init__(
        self,
        server: str = "",
        database: str = "",
        username: str = "",
        password: str = "",
        driver: str = "ODBC Driver 17 for SQL Server",
        autocommit: bool = True,
        timeout: Optional[int] = None,
    ) -> None:
        """
        SQL Server ODBC 连接客户端

        :param server: 服务器地址
        :param database: 数据库名
        :param username: 用户名
        :param password: 密码
        :param driver: ODBC 驱动名称，默认 "ODBC Driver 17 for SQL Server"
        :param autocommit: 是否自动提交，默认 True
        :param timeout: 查询超时时间（秒）
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.autocommit = autocommit
        self.timeout = timeout

    def get_connection(self) -> Any:
        """
        获取一个数据库连接

        :return: 连接对象
        """
        conn_str = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password}"
        )
        conn = pyodbc.connect(conn_str)
        conn.autocommit = self.autocommit
        if self.timeout is not None:
            conn.timeout = self.timeout
        return conn

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
            cursor = conn.cursor()
            try:
                cursor.execute(sql, args)
                result = cursor.fetchone()
                if result is not None and cursor.description:
                    # 转换为字典格式
                    desc = [column[0] for column in cursor.description]
                    return dict(zip(desc, result, strict=True))
                return result
            finally:
                cursor.close()

    def fetchmany(
        self, sql: str, batch_size: int = 100, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Generator[List[Any], None, None]:
        """
        分批获取所有数据，每批返回一次

        :param sql: SQL 语句
        :param batch_size: 每批的数量，默认 100
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，每次返回一批数据
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, args)
                while True:
                    batch = cursor.fetchmany(batch_size)
                    if not batch:
                        break
                    yield batch
            finally:
                cursor.close()

    def fetchall(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> List[Any]:
        """
        查询所有记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, args)
                results = cursor.fetchall()
                # 转换为字典列表
                if results and cursor.description:
                    desc = [column[0] for column in cursor.description]
                    return [dict(zip(desc, row, strict=True)) for row in results]
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
            cursor = conn.cursor()
            try:
                cursor.execute(sql, args)
                # 获取列名
                desc = [column[0] for column in cursor.description] if cursor.description else []
                while True:
                    results = cursor.fetchmany(batch_size)
                    if not results:
                        break
                    for row in results:
                        if desc:
                            yield dict(zip(desc, row, strict=True))
                        else:
                            yield row
            finally:
                cursor.close()

    def execute(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> int:
        """
        执行 SQL 语句（insert/update/delete 等）
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, args)
                if not self.autocommit:
                    conn.commit()
                return cursor.rowcount
            except Exception as e:
                if not self.autocommit:
                    conn.rollback()
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
            cursor = conn.cursor()
            try:
                cursor.executemany(sql, sqlDataList)
                if not self.autocommit:
                    conn.commit()
                return cursor.rowcount
            except Exception as e:
                if not self.autocommit:
                    conn.rollback()
                raise e
            finally:
                cursor.close()

    # 兼容旧版 API
    def execute_query(self, sql_query: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> List[Any]:
        """
        查询所有记录（兼容旧版 API）
        :param sql_query: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        return self.fetchall(sql_query, args)

    def execute_update(self, sql_query: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> int:
        """
        执行 SQL 语句（兼容旧版 API）
        :param sql_query: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 受影响的行数
        """
        return self.execute(sql_query, args)

    def close_connection(self) -> None:
        """
        关闭连接（兼容旧版 API）
        注意：由于使用了上下文管理器，通常不需要手动关闭
        """
        # 此方法仅用于兼容，实际使用中推荐使用 with 语句
        pass


if __name__ == "__main__":
    # 创建 SQL Server 客户端
    client = PyodbcClient(
        server="47.94.219.54",
        database="AIS20201114183546",
        username="BIRead",
        password="your_password",
    )

    # 查询单条记录
    sql = "SELECT TOP 1 * FROM dbo.T_SAL_OUTSTOCK"
    result = client.fetchone(sql)
    print("fetchone:", result)

    # 分批获取数据
    total_count = 0
    for batch in client.fetchmany("SELECT TOP 25 * FROM dbo.T_SAL_OUTSTOCK", batch_size=5):
        print("当前批次数量:", len(batch))
        total_count += len(batch)
    print("fetchmany total:", total_count)

    # 查询所有记录
    sql = "SELECT TOP 10 * FROM dbo.T_SAL_OUTSTOCK"
    results = client.fetchall(sql)
    print("fetchall count:", len(results))

    # 流式查询
    count = 0
    for row in client.fetch_iter("SELECT TOP 10 * FROM dbo.T_SAL_OUTSTOCK"):
        count += 1
    print("fetch_iter:", count)

    # 兼容旧版 API
    result = client.execute_query(sql)
    print("execute_query count:", len(result))
