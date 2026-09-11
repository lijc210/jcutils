# -*- coding:utf-8 -*-
"""
Created on 2016/5/10
@author: lijc210@163.com
Desc: PostgreSQL 异步连接池客户端，内部使用 async with 上下文管理器自动管理连接
支持普通查询和流式查询两种独立的连接池
使用 asyncpg 内置连接池
"""

import logging
from typing import Any, AsyncGenerator, Dict, List, Optional, Sequence, Tuple, Union

logger = logging.getLogger(__name__)

try:
    import asyncpg
except ModuleNotFoundError:
    raise ImportError("请先安装：pip install asyncpg or uv add asyncpg")
except Exception as e:
    raise ImportError(f"asyncpg 导入失败: {e}")


class AsyncPostgresClient:
    def __init__(
        self,
        host: str = "",
        user: str = "",
        passwd: str = "",
        db: str = "",
        port: int = 5432,
        min_size: int = 2,
        max_size: int = 10,
        command_timeout: float = 30.0,
        max_queries: int = 50000,
        max_inactive_connection_lifetime: float = 300.0,
    ):
        """
        PostgreSQL 异步连接池客户端（使用 asyncpg 内置连接池）

        :param host: 主机地址
        :param user: 用户名
        :param passwd: 密码
        :param db: 数据库名
        :param port: 端口号，默认 5432
        :param min_size: 普通连接池最小连接数
        :param max_size: 普通连接池最大连接数
        :param command_timeout: 命令超时时间（秒）
        :param max_queries: 单个连接最大查询数
        :param max_inactive_connection_lifetime: 连接最大空闲时间（秒）
        """
        self.host = host
        self.user = user
        self.password = passwd
        self.dbname = db
        self.port = port

        # 普通连接池配置参数
        self.min_size = min_size
        self.max_size = max_size
        self.command_timeout = command_timeout
        self.max_queries = max_queries
        self.max_inactive_connection_lifetime = max_inactive_connection_lifetime

        # 流式连接池配置参数
        self.stream_min_size = 1
        self.stream_max_size = 1

        # 普通连接池对象（懒加载，首次使用时创建）
        self._normal_pool: Optional[asyncpg.Pool] = None

        # 流式连接池对象（懒加载，首次使用时创建）
        self._stream_pool: Optional[asyncpg.Pool] = None

    def _get_dsn(self) -> str:
        """获取数据库连接 DSN"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    async def _get_or_create_normal_pool(self) -> asyncpg.Pool:
        """获取或创建普通连接池（懒加载）"""
        if self._normal_pool is None:
            logger.info(f"创建普通连接池，连接地址: {self.host}:{self.port}")
            self._normal_pool = await asyncpg.create_pool(
                self._get_dsn(),
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=self.command_timeout,
                max_queries=self.max_queries,
                max_inactive_connection_lifetime=self.max_inactive_connection_lifetime,
                # 启用 prepared statement 缓存
                statement_cache_size=100,
                max_cached_statement_lifetime=300,
            )
            logger.info("普通连接池创建成功")
        return self._normal_pool

    async def _get_or_create_stream_pool(self) -> asyncpg.Pool:
        """获取或创建流式连接池（懒加载）"""
        if self._stream_pool is None:
            logger.info(f"创建流式连接池，连接地址: {self.host}:{self.port}")
            self._stream_pool = await asyncpg.create_pool(
                self._get_dsn(),
                min_size=self.stream_min_size,
                max_size=self.stream_max_size,
                command_timeout=self.command_timeout,
                max_queries=self.max_queries,
                max_inactive_connection_lifetime=self.max_inactive_connection_lifetime,
            )
            logger.info("流式连接池创建成功")
        return self._stream_pool

    async def get_connection(self, pool_type: str = "normal") -> Any:
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
            try:
                if args is None:
                    result = await conn.fetchrow(sql)
                elif isinstance(args, dict):
                    result = await conn.fetchrow(sql, **args)
                else:
                    result = await conn.fetchrow(sql, *args)
                return dict(result) if result is not None else None
            except Exception as e:
                logger.error(f"fetchone 查询失败: {e}")
                raise

    async def fetchmany(
        self,
        sql: str,
        batch_size: int = 100,
        args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
    ) -> AsyncGenerator[List[Any], None]:
        """
        分批获取所有数据，每批返回一次

        :param sql: SQL 语句
        :param batch_size: 每批的数量，默认 100
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，每次返回一批数据
        """
        async with await self.get_connection("normal") as conn:
            try:
                if args is None:
                    results = await conn.fetch(sql)
                elif isinstance(args, dict):
                    results = await conn.fetch(sql, **args)
                else:
                    results = await conn.fetch(sql, *args)
                for i in range(0, len(results), batch_size):
                    batch = results[i : i + batch_size]
                    yield [dict(row) for row in batch]
            except Exception as e:
                logger.error(f"fetchmany 查询失败: {e}")
                raise

    async def fetchall(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> List[Any]:
        """
        查询所有记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        async with await self.get_connection("normal") as conn:
            try:
                if args is None:
                    results = await conn.fetch(sql)
                elif isinstance(args, dict):
                    results = await conn.fetch(sql, **args)
                else:
                    results = await conn.fetch(sql, *args)
                return [dict(row) for row in results]
            except Exception as e:
                logger.error(f"fetchall 查询失败: {e}")
                raise

    async def fetch_iter(
        self,
        sql: str,
        batch_size: int = 1000,
        args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
    ) -> AsyncGenerator[Any, None]:
        """
        流式查询，需要返回大数量时使用
        使用服务端游标逐批获取数据，避免内存溢出
        :param sql: SQL 语句
        :param batch_size: 每批获取的记录数，默认 1000
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，可以迭代获取每条记录
        """
        async with await self.get_connection("stream") as conn:
            try:
                # 使用 cursor 进行流式查询
                async with conn.transaction():
                    if args is None:
                        cursor = await conn.cursor(sql)
                    elif isinstance(args, dict):
                        cursor = await conn.cursor(sql, **args)
                    else:
                        cursor = await conn.cursor(sql, *args)
                    while True:
                        batch = await cursor.fetch(batch_size)
                        if not batch:
                            break
                        for row in batch:
                            yield dict(row)
            except Exception as e:
                logger.error(f"fetch_iter 查询失败: {e}")
                raise

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
            try:
                if args is None:
                    result = await conn.fetchval(sql, column=column)
                elif isinstance(args, dict):
                    result = await conn.fetchval(sql, **args, column=column)
                else:
                    result = await conn.fetchval(sql, *args, column=column)
                return result
            except Exception as e:
                logger.error(f"fetch_val 查询失败: {e}")
                raise

    async def execute(
        self,
        sql: str,
        args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
        extend: bool = False,
    ) -> int:
        """
        执行 SQL 语句（insert/update/delete 等）
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :param extend: 是否扩展语句超时时间（PostgreSQL 特有）
        :return: 受影响的行数
        """
        async with await self.get_connection("normal") as conn:
            try:
                if extend:
                    await conn.execute("SET statement_timeout TO 0")
                if args is None:
                    result = await conn.execute(sql)
                elif isinstance(args, dict):
                    result = await conn.execute(sql, **args)
                else:
                    result = await conn.execute(sql, *args)
                # asyncpg 返回执行状态字符串，需要解析行数
                # 格式为 "INSERT 0 1" 或 "UPDATE 5" 等
                parts = result.split()
                if len(parts) >= 2:
                    try:
                        return int(parts[-1])
                    except (ValueError, IndexError):
                        return 0
                return 0
            except Exception as e:
                logger.error(f"execute 执行失败: {e}")
                raise

    async def executemany(self, sql: str, sqlDataList: Sequence[Sequence[Any]]) -> None:
        """
        批量执行 SQL 语句
        :param sql: SQL 语句
        :param sqlDataList: 数据列表，如 [['a','b','c'], ['d','f','e']]
        :return: 受影响的行数
        """
        async with await self.get_connection("normal") as conn:
            try:
                await conn.executemany(sql, sqlDataList)
            except Exception as e:
                logger.error(f"executemany 执行失败: {e}")
                raise

    async def execute_isolation(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> int:
        """
        在自动提交模式下执行 SQL 语句（PostgreSQL 特有）
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 受影响的行数
        """
        async with await self.get_connection("normal") as conn:
            try:
                # 临时设置自动提交
                await conn.execute("SET AUTOCOMMIT ON")
                if args is None:
                    result = await conn.execute(sql)
                elif isinstance(args, dict):
                    result = await conn.execute(sql, **args)
                else:
                    result = await conn.execute(sql, *args)
                await conn.execute("SET AUTOCOMMIT OFF")
                # 解析返回的行数
                parts = result.split()
                if len(parts) >= 2:
                    try:
                        return int(parts[-1])
                    except (ValueError, IndexError):
                        return 0
                return 0
            except Exception as e:
                logger.error(f"execute_isolation 执行失败: {e}")
                raise

    # 兼容旧版 API
    async def fetch(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> List[Any]:
        """
        查询所有记录（兼容旧版 API）
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        return await self.fetchall(sql, args)

    async def fetch_one(
        self, query: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Optional[Union[Dict[str, Any], Tuple[Any, ...]]]:
        """
        查询单行数据（兼容旧版 API）
        :param query: SQL 查询语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 单行数据或 None
        """
        return await self.fetchone(query, args)

    # 上下文管理器支持
    async def __aenter__(self):
        """支持异步上下文管理器"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出时关闭连接池"""
        await self.close()

    async def close(self):
        """关闭所有连接池"""
        if self._normal_pool:
            logger.info("关闭普通连接池...")
            await self._normal_pool.close()
            self._normal_pool = None
            logger.info("普通连接池已关闭")

        if self._stream_pool:
            logger.info("关闭流式连接池...")
            await self._stream_pool.close()
            self._stream_pool = None
            logger.info("流式连接池已关闭")

    async def reset_pool(self) -> None:
        """重置数据库连接池

        关闭旧连接池并创建新的连接池。
        """
        await self.close()
        await self._get_or_create_normal_pool()


if __name__ == "__main__":

    async def main():
        # 创建连接池客户端
        pg_client = AsyncPostgresClient(
            host="10.230.141.173",
            user="form_reader",
            passwd="xxxxxxxxxxxx",
            db="data",
            port=5432,
        )

        try:
            # 查询单条记录
            sql = "select ip_num,city from config.xxxxx limit 1"
            result = await pg_client.fetchone(sql)
            print("fetchone:", result)

            # 分批获取数据
            total_count = 0
            async for batch in pg_client.fetchmany("select ip_num,city from config.xxxxx limit 25", batch_size=5):
                print("当前批次数量:", len(batch))
                total_count += len(batch)
            print("fetchmany total:", total_count)

            # 查询所有记录
            sql = "select ip_num,city from config.xxxxx limit 10"
            results = await pg_client.fetchall(sql)
            print("fetchall count:", len(results))

            # 流式查询
            count = 0
            async for row in pg_client.fetch_iter("select ip_num,city from config.xxxxx limit 10"):
                count += 1
            print("fetch_iter:", count)

            # 查询单个值
            value = await pg_client.fetch_val("select count(*) from config.xxxxx limit 1")
            print("fetch_val:", value)

            # 执行 SQL
            await pg_client.execute("create table if not exists test_pg_async_client(id serial, name varchar(50))")
            await pg_client.execute("delete from test_pg_async_client")
            await pg_client.execute("insert into test_pg_async_client(name) values('test1')")

            # 批量执行
            await pg_client.executemany(
                "insert into test_pg_async_client(name) values($1)", [("test2",), ("test3",), ("test4",)]
            )

        finally:
            # 关闭连接池
            await pg_client.close()

    # asyncio.run(main())
