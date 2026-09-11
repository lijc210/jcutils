# -*- coding:utf-8 -*-
"""
Created on 2016/5/10
@author: lijc210@163.com
Desc: PostgreSQL 连接池客户端，内部使用 with 上下文管理器自动管理连接
支持普通查询和流式查询两种独立的连接池
使用 psycopg3 (psycopg) 内置连接池
"""

from typing import Any, Dict, Generator, Optional, Sequence, Tuple, Union

try:
    from psycopg.rows import dict_row, tuple_row
    from psycopg_pool import ConnectionPool
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install "psycopg[pool]" or uv add "psycopg[pool]"')
except Exception as e:
    raise ImportError(f"psycopg 导入失败: {e}")


class PostgresClient:
    def __init__(
        self,
        host: str = "",
        user: str = "",
        passwd: str = "",
        db: str = "",
        port: int = 5432,
        cursor_factory: str = "dict",
        min_size: int = 2,
        max_size: int = 10,
        max_idle: int = 300,
        max_lifetime: int = 1800,
        num_workers: int = 3,
    ) -> None:
        """
        PostgreSQL 连接池客户端（使用 psycopg3 内置连接池）

        :param host: 主机地址
        :param user: 用户名
        :param passwd: 密码
        :param db: 数据库名
        :param port: 端口号，默认 5432
        :param cursor_factory: 游标类型，dict/普通
        :param min_size: 普通连接池最小连接数
        :param max_size: 普通连接池最大连接数
        :param max_idle: 连接最大空闲时间（秒）
        :param max_lifetime: 连接最大生命周期（秒）
        :param num_workers: 连接池工作线程数
        """
        self.host = host
        self.user = user
        self.password = passwd
        self.dbname = db
        self.port = port
        self.cursor_factory = cursor_factory

        # 普通连接池配置参数
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle = max_idle
        self.max_lifetime = max_lifetime
        self.num_workers = num_workers

        # 流式连接池配置参数
        self.stream_min_size = 1
        self.stream_max_size = 1

        # 普通连接池对象（懒加载，首次使用时创建）
        self._normal_pool = None

        # 流式连接池对象（懒加载，首次使用时创建）
        self._stream_pool = None

    def _get_row_factory(self) -> Any:
        """根据配置获取行工厂类型"""
        if self.cursor_factory == "dict":
            return dict_row
        else:
            return tuple_row

    def _get_connection_params(self) -> Dict[str, Any]:
        """获取连接参数"""
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "dbname": self.dbname,
            "port": self.port,
            "autocommit": True,
            "row_factory": self._get_row_factory(),
        }

    def _get_or_create_normal_pool(self) -> Any:
        """获取或创建普通连接池（懒加载）"""
        if self._normal_pool is None:
            # 创建普通连接池
            self._normal_pool = ConnectionPool(
                conninfo=(
                    f"host={self.host} user={self.user} password={self.password} dbname={self.dbname} port={self.port}"
                ),
                min_size=self.min_size,
                max_size=self.max_size,
                max_idle=self.max_idle,
                max_lifetime=self.max_lifetime,
                num_workers=self.num_workers,
                open=False,
                kwargs={"autocommit": True, "row_factory": self._get_row_factory()},
            )
            # 打开连接池
            self._normal_pool.open()
        return self._normal_pool

    def _get_or_create_stream_pool(self) -> Any:
        """获取或创建流式连接池（懒加载）"""
        if self._stream_pool is None:
            # 创建流式连接池
            self._stream_pool = ConnectionPool(
                conninfo=(
                    f"host={self.host} user={self.user} password={self.password} dbname={self.dbname} port={self.port}"
                ),
                min_size=self.stream_min_size,
                max_size=self.stream_max_size,
                max_idle=self.max_idle,
                max_lifetime=self.max_lifetime,
                num_workers=1,
                open=False,
                kwargs={"autocommit": False, "row_factory": self._get_row_factory()},
            )
            # 打开连接池
            self._stream_pool.open()
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
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
                result = cursor.fetchone()
                return result

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
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
                while True:
                    batch = cursor.fetchmany(batch_size)
                    if not batch:
                        break
                    yield batch

    def fetchall(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> Sequence[Any]:
        """
        查询所有记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        with self.get_connection("normal") as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
                results = cursor.fetchall()
                return results

    def fetch_iter(
        self, sql: str, batch_size: int = 1000, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Generator[Any, None, None]:
        """
        流式查询，需要返回大数量时使用
        使用服务端游标逐批获取数据，避免内存溢出
        :param sql: SQL 语句
        :param batch_size: 每批获取的记录数，默认 1000
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，可以迭代获取每条记录
        """
        with self.get_connection("stream") as conn:
            with conn.cursor(name="stream_cursor") as cursor:
                cursor.itersize = batch_size
                cursor.execute(sql, args)
                for row in cursor:
                    yield row

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
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql, args)
                    result = cursor.fetchone()
                    if result is None:
                        return None
                    if isinstance(result, dict):
                        # 如果是字典，通过列名或位置获取
                        columns = [desc.name for desc in cursor.description]
                        column_name = columns[column]
                        return result.get(column_name)
                    else:
                        # 如果是元组，通过位置获取
                        return result[column]
                except Exception as e:
                    conn.rollback()
                    raise e

    def execute(
        self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None, extend: bool = False
    ) -> int:
        """
        执行 SQL 语句（insert/update/delete 等）
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :param extend: 是否扩展语句超时时间（PostgreSQL 特有）
        :return: 受影响的行数
        """
        with self.get_connection("normal") as conn:
            with conn.cursor() as cursor:
                try:
                    if extend:
                        cursor.execute("SET statement_timeout TO 0")
                    cursor.execute(sql, args)
                    # psycopg execute 返回游标，需要获取 rowcount
                    return cursor.rowcount if cursor else 0
                except Exception as e:
                    conn.rollback()
                    raise e

    def executemany(self, sql: str, sqlDataList: Sequence[Sequence[Any]]) -> int:
        """
        批量执行 SQL 语句
        :param sql: SQL 语句
        :param sqlDataList: 数据列表，如 [['a','b','c'], ['d','f','e']]
        :return: 受影响的行数
        """
        with self.get_connection("normal") as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.executemany(sql, sqlDataList)
                    # psycopg executemany 返回游标，需要获取 rowcount
                    return cursor.rowcount if cursor else 0
                except Exception as e:
                    conn.rollback()
                    raise e

    def execute_isolation(self, sql: str) -> None:
        """
        在自动提交模式下执行 SQL 语句（PostgreSQL 特有）
        :param sql: SQL 语句
        :return: None
        """
        with self.get_connection("normal") as conn:
            with conn.cursor() as cursor:
                try:
                    # 临时设置隔离级别为 0（自动提交）
                    conn.execute("SET AUTOCOMMIT ON")
                    cursor.execute(sql)
                    conn.execute("SET AUTOCOMMIT OFF")
                except Exception as e:
                    conn.rollback()
                    raise e

    def close(self) -> None:
        """关闭所有连接池"""
        if self._normal_pool:
            self._normal_pool.close()
        if self._stream_pool:
            self._stream_pool.close()

    def __enter__(self) -> "PostgresClient":
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出时关闭连接池"""
        self.close()


if __name__ == "__main__":
    pg_client = PostgresClient(
        host="10.230.141.173",
        user="form_reader",
        passwd="xxxxxxxxxxxx",
        db="data",
        port=5432,
        cursor_factory="dict",
    )

    # 查询单条记录
    sql = "select ip_num,city from config.xxxxx limit 1"
    result = pg_client.fetchone(sql)
    print("fetchone:", result)

    # 分批获取数据
    total_count = 0
    for batch in pg_client.fetchmany("select ip_num,city from config.xxxxx limit 25", batch_size=5):
        print("当前批次数量:", len(batch))
        total_count += len(batch)
    print("fetchmany total:", total_count)

    # 查询所有记录
    sql = "select ip_num,city from config.xxxxx limit 10"
    results = pg_client.fetchall(sql)
    print("fetchall count:", len(results))

    # 流式查询
    count = 0
    for row in pg_client.fetch_iter("select ip_num,city from config.xxxxx limit 10"):
        count += 1
    print("fetch_iter:", count)

    # 执行 SQL
    pg_client.execute("create table if not exists test_pg_client(id serial, name varchar(50))")
    pg_client.execute("delete from test_pg_client")
    pg_client.execute("insert into test_pg_client(name) values('test1')")

    # 批量执行
    pg_client.executemany("insert into test_pg_client(name) values(%s)", [["test2"], ["test3"], ["test4"]])

    # 关闭连接池
    pg_client.close()
