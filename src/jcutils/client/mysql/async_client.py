"""
@File    :   mysql_client_async.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :
MySQL 异步连接池客户端，内部使用 async with 上下文管理器自动管理连接
支持普通查询和流式查询两种独立的连接池
"""

from typing import Any, AsyncGenerator, Dict, List, Optional, Protocol, Sequence, Tuple, Union

import aiomysql
from aiomysql import Pool


class ConnectionConfig(Protocol):
    """连接配置协议接口"""

    host: str
    user: str
    passwd: str
    db: str
    port: int


class AsyncMySQLClient:
    def __init__(
        self,
        conn_config: ConnectionConfig,
        charset: str = "utf8mb4",
        cursorclass: str = "dict",
        mincached: int = 2,
        maxcached: int = 5,
        maxconnections: int = 10,
        blocking: bool = True,
        echo: bool = False,
    ):
        """
        MySQL 异步连接池客户端

        :param conn_config: 连接配置对象（符合 ConnectionConfig 协议），包含 host, user, passwd, db, port
        :param charset: 字符集，默认 utf8mb4
        :param cursorclass: 游标类型，dict/ss_dict/ss_list/普通
        :param mincached: 普通连接池初始空闲连接数
        :param maxcached: 普通连接池最大空闲连接数
        :param maxconnections: 普通连接池最大连接数
        :param blocking: 连接池满时是否阻塞等待
        :param echo: 是否输出 SQL 日志
        """
        self.host = conn_config.host
        self.user = conn_config.user
        self.passwd = conn_config.passwd
        self.db = conn_config.db
        self.charset = charset
        self.port = conn_config.port
        self.cursorclass = cursorclass
        self.echo = echo

        # 普通连接池配置参数
        self.mincached = mincached
        self.maxcached = maxcached
        self.maxconnections = maxconnections
        self.blocking = blocking

        # 流式连接池配置参数
        self.stream_minconnections = 1

        # 普通连接池对象（懒加载，首次使用时创建）
        self._normal_pool: Optional[Pool] = None

        # 流式连接池对象（懒加载，首次使用时创建）
        self._stream_pool: Optional[Pool] = None

        # 游标类型映射
        self.cursor_map = {
            "dict": aiomysql.DictCursor,
            "ss_dict": aiomysql.SSDictCursor,
            "ss_list": aiomysql.SSCursor,
            "default": aiomysql.Cursor,
        }

    def _get_cursor_class(self, cursorclass_type: str = "normal"):
        """
        根据配置获取游标类型

        :param cursorclass_type: 游标类型 normal/stream
        :return: 游标类
        """
        if cursorclass_type == "stream":
            # 流式查询使用服务端游标
            if self.cursorclass == "dict":
                return aiomysql.SSDictCursor
            else:
                return aiomysql.SSCursor
        else:
            # 普通查询
            return self.cursor_map.get(self.cursorclass, aiomysql.Cursor)

    async def _get_or_create_normal_pool(self) -> Any:
        """获取或创建普通连接池（懒加载）"""
        if self._normal_pool is None:
            cursorclass = self._get_cursor_class("normal")
            # 创建普通连接池
            self._normal_pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.passwd,
                db=self.db,
                charset=self.charset,
                minsize=self.mincached,
                maxsize=self.maxconnections,
                autocommit=True,
                cursorclass=cursorclass,
                echo=self.echo,
                connect_timeout=30,
            )
        return self._normal_pool

    async def _get_or_create_stream_pool(self) -> Any:
        """获取或创建流式连接池（懒加载）"""
        if self._stream_pool is None:
            cursorclass = self._get_cursor_class("stream")
            # 创建流式连接池（使用服务端游标）
            self._stream_pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.passwd,
                db=self.db,
                charset=self.charset,
                minsize=0,
                maxsize=self.stream_minconnections,
                autocommit=True,
                cursorclass=cursorclass,
                echo=self.echo,
                connect_timeout=30,
            )
        return self._stream_pool

    async def get_connection(self, pool_type: str = "normal"):
        """
        从指定类型的连接池获取一个连接

        :param pool_type: 连接池类型，normal/stream
        :return: 连接对象
        """
        if pool_type == "stream":
            pool = await self._get_or_create_stream_pool()
        else:
            pool = await self._get_or_create_normal_pool()
        return pool.acquire()

    async def fetchone(
        self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Optional[Union[Dict[str, Any], Tuple[Any, ...]]]:
        """
        查询单条记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 单条记录
        """
        async with await self.get_connection("normal") as conn:
            async with conn.cursor(self._get_cursor_class("normal")) as cursor:
                try:
                    await cursor.execute(sql, args)
                    result = await cursor.fetchone()
                    return result
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def fetchmany(
        self, sql: str, batch_size: int = 100, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> AsyncGenerator[List[Any], None]:
        """
        分批获取所有数据，每批返回一次

        :param sql: SQL 语句
        :param batch_size: 每批的数量，默认 100
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，每次返回一批数据
        """
        async with await self.get_connection("normal") as conn:
            async with conn.cursor(self._get_cursor_class("normal")) as cursor:
                try:
                    await cursor.execute(sql, args)
                    while True:
                        batch = await cursor.fetchmany(batch_size)
                        if not batch:
                            break
                        yield batch
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def fetchall(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> List[Any]:
        """
        查询所有记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        async with await self.get_connection("normal") as conn:
            async with conn.cursor(self._get_cursor_class("normal")) as cursor:
                try:
                    await cursor.execute(sql, args)
                    results = await cursor.fetchall()
                    return results
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def fetch_iter(
        self, sql: str, batch_size: int = 1000, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> AsyncGenerator[Any, None]:
        """
        流式查询，需要返回大数量时使用
        使用服务端游标(SSCursor)逐批获取数据，避免内存溢出
        :param sql: SQL 语句
        :param batch_size: 每批获取的记录数，默认 1000
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，可以迭代获取每条记录
        """
        async with await self.get_connection("stream") as conn:
            async with conn.cursor(self._get_cursor_class("stream")) as cursor:
                try:
                    await cursor.execute(sql, args)
                    while True:
                        results = await cursor.fetchmany(batch_size)
                        if not results:
                            break
                        for row in results:
                            yield row
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def fetch_val(
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
        async with await self.get_connection("normal") as conn:
            async with conn.cursor(self._get_cursor_class("normal")) as cursor:
                try:
                    await cursor.execute(sql, args)
                    result = await cursor.fetchone()
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
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def execute(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> int:
        """
        执行 SQL 语句（insert/update/delete 等）
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 受影响的行数
        """
        async with await self.get_connection("normal") as conn:
            async with conn.cursor(self._get_cursor_class("normal")) as cursor:
                try:
                    result = await cursor.execute(sql, args)
                    await conn.commit()
                    return result
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def executemany(self, sql: str, sqlDataList: Sequence[Sequence[Any]]) -> int:
        """
        批量执行 SQL 语句
        :param sql: SQL 语句
        :param sqlDataList: 数据列表，如 [['a','b','c'], ['d','f','e']]
        :return: lastrowid
        """
        async with await self.get_connection("normal") as conn:
            async with conn.cursor(self._get_cursor_class("normal")) as cursor:
                try:
                    rowcount = await cursor.executemany(sql, sqlDataList)
                    await conn.commit()
                    return rowcount
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def close(self):
        """关闭所有连接池"""
        if self._normal_pool:
            self._normal_pool.close()
            await self._normal_pool.wait_closed()
        if self._stream_pool:
            self._stream_pool.close()
            await self._stream_pool.wait_closed()

    async def __aenter__(self):
        """支持异步上下文管理器"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出时关闭连接池"""
        await self.close()


# 运行示例
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

    async def main():
        # 创建连接池客户端
        mysql_client = AsyncMySQLClient(conn_config=mysql_config)

        try:
            # 查询单条记录
            sql = "select * from userdata.dict_professionalterm limit 1"
            result = await mysql_client.fetchone(sql)
            print("fetchone:", result)

            # 分批获取数据
            total_count = 0
            async for batch in mysql_client.fetchmany(
                "select * from userdata.dict_professionalterm limit 25", batch_size=5
            ):
                print("当前批次数量:", len(batch))
                total_count += len(batch)
            print("fetchmany total:", total_count)

            # 查询所有记录
            sql = "select * from userdata.dict_professionalterm limit 5"
            results = await mysql_client.fetchall(sql)
            print("fetchall count:", len(results))

            # 流式查询
            count = 0
            async for row in mysql_client.fetch_iter("select * from userdata.dict_professionalterm limit 10"):
                count += 1
            print("fetch_iter:", count)

        finally:
            await mysql_client.close()

    # asyncio.run(main())
