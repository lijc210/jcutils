"""
@File    :   mssql_client.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :
Microsoft SQL Server 连接客户端，内部使用 with 上下文管理器自动管理连接
支持普通查询和流式查询
"""

from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union

try:
    import pymssql
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install jcutils[pymssql] or uv add "jcutils[pymssql]"')
except Exception as e:
    raise ImportError(f"pymssql 导入失败: {e}")


class MsSqlClient:
    def __init__(
        self,
        host: str = "",
        user: str = "",
        passwd: str = "",
        db: str = "",
        port: int = 1433,
        charset: str = "utf8",
        cursorclass: str = "dict",
        autocommit: bool = True,
        timeout: Optional[int] = None,
    ) -> None:
        """
        SQL Server 连接客户端

        :param host: 主机地址
        :param user: 用户名
        :param passwd: 密码
        :param db: 数据库名
        :param port: 端口号，默认 1433
        :param charset: 字符集，默认 utf8
        :param cursorclass: 游标类型，dict/普通
        :param autocommit: 是否自动提交，默认 True
        :param timeout: 查询超时时间（秒）
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.port = port
        self.charset = charset
        self.cursorclass = cursorclass
        self.autocommit = autocommit
        self.timeout = timeout

    def get_connection(self) -> Any:
        """
        获取一个数据库连接

        :return: 连接对象
        """
        conn_params = {
            "host": self.host,
            "user": self.user,
            "password": self.passwd,
            "database": self.db,
            "charset": self.charset,
            "port": self.port,
            "autocommit": self.autocommit,
        }
        if self.timeout is not None:
            conn_params["timeout"] = self.timeout
        conn = pymssql.connect(**conn_params)
        return conn

    def get_cursor(self, conn: Any) -> Any:
        """
        根据配置获取游标

        :param conn: 数据库连接
        :return: 游标对象
        """
        if self.cursorclass == "dict":
            cursor = conn.cursor(as_dict=True)
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

    def fetchall(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> List[Any]:
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
                    for row in results:
                        yield row
            finally:
                cursor.close()

    def fetch_val(
        self,
        sql: str,
        args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
        column: int = 0,
    ) -> Any:
        """
        查询单个值
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :param column: 要返回的列索引（默认为第 0 列）
        :return: 单个值
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                result = cursor.fetchone()
                if result is None:
                    return None
                if isinstance(result, dict):
                    # 如果是字典，通过列名或位置获取
                    columns = [desc[0] for desc in cursor.description]
                    column_name = columns[column]
                    return result.get(column_name)
                else:
                    # 如果是元组，通过位置获取
                    return result[column]
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
            cursor = self.get_cursor(conn)
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
        :return: lastrowid
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.executemany(sql, sqlDataList)
                if not self.autocommit:
                    conn.commit()
                lastrowid = getattr(cursor, "lastrowid", 0)
                return lastrowid
            except Exception as e:
                if not self.autocommit:
                    conn.rollback()
                raise e
            finally:
                cursor.close()


if __name__ == "__main__":
    mssql_client = MsSqlClient(
        host="xx.xx.xx.xx",
        user="xxxxx",
        passwd="your_password",
        db="AIS20201114183546",
        port=1433,
    )

    # 查询单条记录
    sql = "SELECT TOP 1 * FROM dbo.table_name"
    result = mssql_client.fetchone(sql)
    print("fetchone:", result)

    # 分批获取数据
    total_count = 0
    for batch in mssql_client.fetchmany("SELECT TOP 25 * FROM dbo.table_name", batch_size=5):
        print("当前批次数量:", len(batch))
        total_count += len(batch)
    print("fetchmany total:", total_count)

    # 查询所有记录
    sql = "SELECT TOP 10 * FROM dbo.table_name"
    results = mssql_client.fetchall(sql)
    print("fetchall count:", len(results))

    # 流式查询
    count = 0
    for row in mssql_client.fetch_iter("SELECT TOP 10 * FROM dbo.table_name"):
        count += 1
    print("fetch_iter:", count)
