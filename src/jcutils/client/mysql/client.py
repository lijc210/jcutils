"""
@File    :   mssql_client.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :
MySQL 连接池客户端，内部使用 with 上下文管理器自动管理连接
支持普通查询和流式查询两种独立的连接池
"""

from typing import Any, Dict, Generator, Optional, Sequence, Tuple, Union

try:
    import pymysql  # type: ignore
    from dbutils.pooled_db import PooledDB  # type: ignore
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install jcutils[mysql] or uv add "jcutils[mysql]"')
except Exception as e:
    raise ImportError(f"pymysql 导入失败: {e}")


class MySqlClient:
    def __init__(
        self,
        host: str = "",
        user: str = "",
        passwd: str = "",
        db: str = "",
        port: int = 3306,
        charset: str = "utf8mb4",
        cursorclass: str = "dict",
        mincached: int = 2,
        maxcached: int = 5,
        maxconnections: int = 10,
        blocking: bool = True,
        ping: int = 1,
    ) -> None:
        """
        MySQL 连接池客户端

        :param host: 主机地址
        :param user: 用户名
        :param passwd: 密码
        :param db: 数据库名
        :param port: 端口号，默认 3306
        :param charset: 字符集，默认 utf8mb4
        :param cursorclass: 游标类型，dict/ss_dict/ss_list/普通
        :param mincached: 普通连接池初始空闲连接数
        :param maxcached: 普通连接池最大空闲连接数
        :param maxconnections: 普通连接池最大连接数
        :param blocking: 连接池满时是否阻塞等待
        :param ping: 检查连接的频率，0=不检查，1=每次使用前检查
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.charset = charset
        self.port = port
        self.cursorclass = cursorclass

        # 普通连接池配置参数
        self.mincached = mincached
        self.maxcached = maxcached
        self.maxconnections = maxconnections
        self.blocking = blocking
        self.ping = ping

        # 流式连接池配置参数
        self.stream_minconnections = 1

        # 普通连接池对象（懒加载，首次使用时创建）
        self._normal_pool = None

        # 流式连接池对象（懒加载，首次使用时创建）
        self._stream_pool = None

    def _get_or_create_normal_pool(self) -> PooledDB:
        """获取或创建普通连接池（懒加载）"""
        # 根据配置获取普通查询的游标类型
        if self.cursorclass == "dict":
            cursorclass = pymysql.cursors.DictCursor
        else:
            cursorclass = pymysql.cursors.Cursor
        if self._normal_pool is None:
            # 创建普通连接池
            self._normal_pool = PooledDB(
                creator=pymysql,
                mincached=self.mincached,
                maxcached=self.maxcached,
                maxconnections=self.maxconnections,
                blocking=self.blocking,
                ping=self.ping,
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.db,
                charset=self.charset,
                port=self.port,
                cursorclass=cursorclass,
                autocommit=True,
            )
        return self._normal_pool

    def _get_or_create_stream_pool(self) -> PooledDB:
        """获取或创建流式连接池（懒加载）"""

        # 根据配置获取普通查询的游标类型
        if self.cursorclass == "dict":
            cursorclass = pymysql.cursors.SSDictCursor
        else:
            cursorclass = pymysql.cursors.SSCursor
        if self._stream_pool is None:
            # 创建流式连接池（使用服务端游标）
            self._stream_pool = PooledDB(
                creator=pymysql,
                mincached=0,
                maxcached=0,
                maxconnections=self.stream_minconnections,
                blocking=True,
                ping=1,
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.db,
                charset=self.charset,
                port=self.port,
                cursorclass=cursorclass,
                autocommit=True,
            )
        return self._stream_pool

    def get_connection(self, pool_type: str = "normal") -> Any:
        """
        从指定类型的连接池获取一个连接

        :param pool_type: 连接池类型，normal/stream
        :return: 连接对象
        """
        if pool_type == "stream":
            pool = self._get_or_create_stream_pool()
        else:
            pool = self._get_or_create_normal_pool()
        return pool.connection()

    def fetchone(
        self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Optional[Union[Dict[str, Any], Tuple[Any, ...]]]:
        """
        查询单条记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 单条记录
        """
        with self.get_connection("normal") as conn:
            cursor = conn.cursor()
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
        with self.get_connection("normal") as conn:
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

    def fetchall(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> Sequence[Any]:
        """
        查询所有记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        with self.get_connection("normal") as conn:
            cursor = conn.cursor()
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
        使用服务端游标(SSCursor)逐批获取数据，避免内存溢出
        :param sql: SQL 语句
        :param batch_size: 每批获取的记录数，默认 1000
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，可以迭代获取每条记录
        """
        with self.get_connection("stream") as conn:
            cursor = conn.cursor()
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
        with self.get_connection("normal") as conn:
            cursor = conn.cursor()
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
        with self.get_connection("normal") as conn:
            cursor = conn.cursor()
            try:
                result = cursor.execute(sql, args)
                conn.commit()
                return result
            except Exception as e:
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
        with self.get_connection("normal") as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(sql, sqlDataList)
                conn.commit()
                lastrowid = getattr(cursor, "lastrowid", 0)
                return lastrowid
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()


if __name__ == "__main__":
    from pydantic import BaseModel

    class TestConnectionConfig(BaseModel):
        host: str
        user: str
        passwd: str
        db: str
        port: int

    mysql_config = TestConnectionConfig(
        host="10.10.11.244",
        user="biuser",
        passwd="@biuser123",
        db="userdata",
        port=3309,
    )

    # 创建连接池客户端（此时不会创建任何连接池）
    mysql_client = MySqlClient(
        host="10.10.11.244",
        user="biuser",
        passwd="@biuser123",
        db="userdata",
        port=3309,
    )

    # 首次普通查询时创建普通连接池
    sql = "select * from userdata.dict_professionalterm limit 1"
    result = mysql_client.fetchone(sql)
    print("fetchone:", result)

    # 分批获取数据
    total_count = 0
    for batch in mysql_client.fetchmany("select * from userdata.dict_professionalterm limit 25", batch_size=5):
        print("当前批次数量:", len(batch))
        total_count += len(batch)
    print("fetchmany total:", total_count)

    # 流式连接池已创建，复用连接
    sql = "select * from userdata.dict_professionalterm limit 5"
    results = mysql_client.fetchall(sql)
    print("fetchall count:", len(results))

    # 首次流式查询时创建独立的流式连接池
    count = 0
    for row in mysql_client.fetch_iter("select * from userdata.dict_professionalterm limit 10"):
        count += 1
    print("fetch_iter:", count)
