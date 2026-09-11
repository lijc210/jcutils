#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis 异步客户端工具类

支持单机模式和集群模式，提供统一的异步 API 接口
使用 redis 官方库的异步功能（redis-py 4.2+ 支持 asyncio）

安装依赖：
    pip install redis>=4.2.0

使用示例：
    # 单机模式
    import asyncio
    async def main():
        rc = RedisAsyncClient(host="127.0.0.1", port=6379, password="your_password")
        await rc.set("key", "value", ex=3600)
        value = await rc.get("key")
        await rc.close()

    # 集群模式
    async def main():
        nodes = [
            {"host": "10.10.20.97", "port": 7000},
            {"host": "10.10.20.97", "port": 7001},
            {"host": "10.10.20.97", "port": 7002}
        ]
        rc = RedisAsyncClient(startup_nodes=nodes, password="your_password")
        await rc.set("key", "value")
        await rc.close()

    # 使用异步上下文管理器
    async def main():
        async with RedisAsyncClient(host="127.0.0.1") as rc:
            await rc.set("key", "value")
"""

from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import redis.asyncio as redis
    from redis.asyncio import RedisCluster
except ModuleNotFoundError:
    raise ImportError("请先安装：pip install redis or uv add redis")
except Exception as e:
    raise ImportError(f"redis 导入失败: {e}")


class AsyncRedisClient:
    """
    Redis 异步客户端封装类

    提供简单易用的异步 Redis 操作接口，支持单机和集群模式
    自动检测连接模式，统一API调用方式

    Attributes:
        client: Redis 异步客户端实例（Redis 或 RedisCluster）
        host: 单机模式的主机地址
        port: 单机模式的端口
        db: 单机模式的数据库编号
        password: 密码
        startup_nodes: 集群节点列表
        decode_responses: 是否自动解码响应为字符串
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        startup_nodes: Optional[List[Dict[str, Any]]] = None,
        decode_responses: bool = True,
        **kwargs,
    ) -> None:
        """
        初始化 Redis 异步客户端

        单机模式和集群模式二选一：
        - 单机模式：传入 host 参数
        - 集群模式：传入 startup_nodes 参数

        Args:
            host: Redis 服务器地址（单机模式）
            port: Redis 服务器端口，默认 6379
            db: 数据库编号（单机模式），默认 0，范围 0-15
            password: 密码，如果 Redis 设置了密码则必须提供
            startup_nodes: 集群启动节点列表（集群模式）
                格式：[{"host": "ip", "port": 7000}, ...]
            decode_responses: 是否将响应解码为字符串，默认 True
            **kwargs: 其他 Redis 连接参数
                如：socket_timeout, socket_connect_timeout, max_connections 等

        Raises:
            RedisConnectionError: 连接失败时抛出

        Examples:
            # 单机模式
            >>> rc = RedisAsyncClient(host="127.0.0.1", port=6379, db=0)
            >>> rc = RedisAsyncClient(host="127.0.0.1", password="123456")

            # 集群模式
            >>> nodes = [{"host": "10.10.20.97", "port": 7000}]
            >>> rc = RedisAsyncClient(startup_nodes=nodes, password="123456")
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.startup_nodes = startup_nodes
        self.decode_responses = decode_responses
        self._kwargs = kwargs

        # 客户端实例（懒加载，首次使用时连接）
        self.client: Optional[Union[redis.Redis, RedisCluster]] = None

    async def _connect(self) -> Union[redis.Redis, RedisCluster]:
        """
        建立 Redis 异步连接

        根据参数自动选择单机或集群模式

        Returns:
            Redis 或 RedisCluster 实例
        """
        if self.startup_nodes:
            # 集群模式：使用 redis.asyncio.RedisCluster
            return RedisCluster(
                startup_nodes=self.startup_nodes,
                password=self.password,
                decode_responses=self.decode_responses,
                **self._kwargs,
            )
        else:
            # 单机模式：使用 redis.asyncio.Redis
            return redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                **self._kwargs,
            )

    async def ensure_connected(self) -> None:
        """确保客户端已连接（懒连接）"""
        if self.client is None:
            self.client = await self._connect()

    async def ping(self) -> bool:
        """
        测试 Redis 服务器连接是否正常

        Returns:
            True 表示连接正常，False 表示连接失败

        Examples:
            >>> rc = RedisAsyncClient(host="127.0.0.1")
            >>> if await rc.ping():
            ...     print("Redis 连接成功")
            ... else:
            ...     print("Redis 连接失败")
        """
        try:
            await self.ensure_connected()
            assert self.client is not None
            return await self.client.ping()
        except Exception:
            return False

    async def close(self) -> None:
        """
        关闭 Redis 异步连接

        释放连接池资源，通常在程序结束时调用
        如果使用异步上下文管理器，会自动调用此方法

        Examples:
            >>> rc = RedisAsyncClient(host="127.0.0.1")
            >>> await rc.set("key", "value")
            >>> await rc.close()
        """
        if self.client is not None:
            await self.client.close()
            self.client = None

    # ==================== String 字符串操作 ====================

    async def set(self, key: str, value: Any, ex: Optional[int] = None, px: Optional[int] = None) -> bool:
        """
        设置字符串键值对

        如果键已存在，会覆盖旧值

        Args:
            key: 键名
            value: 值，可以是字符串、数字等
            ex: 过期时间（秒）
            px: 过期时间（毫秒），ex 和 px 同时存在时，px 优先

        Returns:
            True 表示设置成功

        Examples:
            >>> await rc.set("name", "张三")  # 永不过期
            >>> await rc.set("session", "abc123", ex=3600)  # 1小时后过期
            >>> await rc.set("token", "xyz789", px=5000)  # 5秒后过期
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.set(key, value, ex=ex, px=px)

    async def get(self, key: str) -> Optional[str]:
        """
        获取字符串值

        Args:
            key: 键名

        Returns:
            键对应的值（字符串），如果键不存在返回 None

        Examples:
            >>> await rc.set("name", "张三")
            >>> name = await rc.get("name")  # "张三"
            >>> age = await rc.get("age")  # None，键不存在
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.get(key)

    async def mset(self, mapping: Dict[str, Any]) -> bool:
        """
        批量设置多个键值对

        原子性操作，要么全部成功，要么全部失败

        Args:
            mapping: 键值字典 {key: value, ...}

        Returns:
            True 表示设置成功

        Examples:
            >>> await rc.mset({
            ...     "user:1:name": "张三",
            ...     "user:1:age": "30",
            ...     "user:1:city": "北京"
            ... })
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.mset(mapping)

    async def mget(self, keys: List[str]) -> List[Optional[str]]:
        """
        批量获取多个键的值

        Args:
            keys: 键名列表

        Returns:
            值列表，键不存在的位置返回 None

        Examples:
            >>> await rc.mset({"a": "1", "b": "2", "c": "3"})
            >>> values = await rc.mget(["a", "b", "d"])  # ["1", "2", None]
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.mget(keys)

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        递增计数器

        将键存储的数字增加指定值，如果键不存在，会先初始化为 0 再增加

        Args:
            key: 键名
            amount: 增加的数值，默认 1

        Returns:
            增加后的值

        Examples:
            >>> await rc.set("counter", 10)
            >>> await rc.incr("counter")  # 返回 11
            >>> await rc.incr("counter", 5)  # 返回 16
            >>> await rc.incr("new_counter")  # 返回 1，键不存在时从0开始
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.incr(key, amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """
        递减计数器

        将键存储的数字减少指定值，如果键不存在，会先初始化为 0 再减少

        Args:
            key: 键名
            amount: 减少的数值，默认 1

        Returns:
            减少后的值

        Examples:
            >>> await rc.set("counter", 10)
            >>> await rc.decr("counter")  # 返回 9
            >>> await rc.decr("counter", 3)  # 返回 6
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.decr(key, amount)

    # ==================== Hash 哈希表操作 ====================

    async def hset(self, name: str, key: str, value: Any) -> int:
        """
        设置哈希表字段值

        Args:
            name: 哈希表名
            key: 字段名
            value: 字段值

        Returns:
            1 表示新字段，0 表示更新已有字段

        Examples:
            >>> await rc.hset("user:1", "name", "张三")  # 返回 1
            >>> await rc.hset("user:1", "age", 30)
            >>> await rc.hset("user:1", "name", "李四")  # 返回 0，更新已有字段
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.hset(name, key, value)

    async def hget(self, name: str, key: str) -> Optional[str]:
        """
        获取哈希表字段值

        Args:
            name: 哈希表名
            key: 字段名

        Returns:
            字段值，字段不存在返回 None

        Examples:
            >>> await rc.hset("user:1", "name", "张三")
            >>> name = await rc.hget("user:1", "name")  # "张三"
            >>> email = await rc.hget("user:1", "email")  # None
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.hget(name, key)

    async def hmset(self, name: str, mapping: Dict[str, Any]) -> bool:
        """
        批量设置哈希表多个字段

        Args:
            name: 哈希表名
            mapping: 字段字典 {field: value, ...}

        Returns:
            True 表示设置成功

        Examples:
            >>> await rc.hmset("user:1", {
            ...     "name": "张三",
            ...     "age": 30,
            ...     "city": "北京"
            ... })
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.hmset(name, mapping)

    async def hgetall(self, name: str) -> Dict[str, str]:
        """
        获取哈希表所有字段和值

        Args:
            name: 哈希表名

        Returns:
            字典 {field: value, ...}，哈希表不存在返回空字典

        Examples:
            >>> await rc.hmset("user:1", {"name": "张三", "age": "30"})
            >>> user = await rc.hgetall("user:1")  # {"name": "张三", "age": "30"}
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.hgetall(name)

    async def hdel(self, name: str, *keys: str) -> int:
        """
        删除哈希表字段

        Args:
            name: 哈希表名
            *keys: 要删除的字段名

        Returns:
            成功删除的字段数量

        Examples:
            >>> await rc.hmset("user:1", {"name": "张三", "age": "30", "city": "北京"})
            >>> await rc.hdel("user:1", "city")  # 返回 1
            >>> await rc.hdel("user:1", "name", "age")  # 返回 2
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.hdel(name, *keys)

    # ==================== List 列表操作 ====================

    async def lpush(self, name: str, *values: Any) -> int:
        """
        从列表左侧插入元素

        Args:
            name: 列表名
            *values: 要插入的值

        Returns:
            插入后列表的长度

        Examples:
            >>> await rc.lpush("queue", "task1")  # ["task1"]
            >>> await rc.lpush("queue", "task2", "task3")  # ["task3", "task2", "task1"]
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.lpush(name, *values)

    async def rpush(self, name: str, *values: Any) -> int:
        """
        从列表右侧插入元素

        Args:
            name: 列表名
            *values: 要插入的值

        Returns:
            插入后列表的长度

        Examples:
            >>> await rc.rpush("queue", "task1")  # ["task1"]
            >>> await rc.rpush("queue", "task2", "task3")  # ["task1", "task2", "task3"]
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.rpush(name, *values)

    async def lpop(self, name: str) -> Optional[str]:
        """
        从列表左侧弹出元素

        Args:
            name: 列表名

        Returns:
            弹出的元素，列表为空返回 None

        Examples:
            >>> await rc.rpush("queue", "task1", "task2", "task3")
            >>> task = await rc.lpop("queue")  # "task1"
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.lpop(name)

    async def rpop(self, name: str) -> Optional[str]:
        """
        从列表右侧弹出元素

        Args:
            name: 列表名

        Returns:
            弹出的元素，列表为空返回 None

        Examples:
            >>> await rc.rpush("queue", "task1", "task2", "task3")
            >>> task = await rc.rpop("queue")  # "task3"
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.rpop(name)

    async def lrange(self, name: str, start: int = 0, end: int = -1) -> List[str]:
        """
        获取列表指定范围的元素

        Args:
            name: 列表名
            start: 起始索引，0 表示第一个元素
            end: 结束索引，-1 表示最后一个元素

        Returns:
            元素列表

        Examples:
            >>> await rc.rpush("queue", "a", "b", "c", "d", "e")
            >>> await rc.lrange("queue")  # ["a", "b", "c", "d", "e"]
            >>> await rc.lrange("queue", 0, 2)  # ["a", "b", "c"]
            >>> await rc.lrange("queue", -3, -1)  # ["c", "d", "e"]
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.lrange(name, start, end)

    async def llen(self, name: str) -> int:
        """
        获取列表长度

        Args:
            name: 列表名

        Returns:
            列表长度，列表不存在返回 0

        Examples:
            >>> await rc.rpush("queue", "a", "b", "c")
            >>> length = await rc.llen("queue")  # 3
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.llen(name)

    # ==================== Set 集合操作 ====================

    async def sadd(self, name: str, *values: Any) -> int:
        """
        向集合添加元素

        Args:
            name: 集合名
            *values: 要添加的值

        Returns:
            成功添加的新元素数量（已存在的元素不计入）

        Examples:
            >>> await rc.sadd("tags", "python", "redis", "mysql")  # 返回 3
            >>> await rc.sadd("tags", "python", "django")  # 返回 1，"python"已存在
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.sadd(name, *values)

    async def smembers(self, name: str) -> set:
        """
        获取集合所有元素

        Args:
            name: 集合名

        Returns:
            元素集合，集合不存在返回空集合

        Examples:
            >>> await rc.sadd("tags", "python", "redis")
            >>> tags = await rc.smembers("tags")  # {"python", "redis"}
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.smembers(name)

    async def srem(self, name: str, *values: Any) -> int:
        """
        从集合中删除元素

        Args:
            name: 集合名
            *values: 要删除的值

        Returns:
            成功删除的元素数量

        Examples:
            >>> await rc.sadd("tags", "python", "redis", "mysql")
            >>> await rc.srem("tags", "mysql")  # 返回 1
            >>> await rc.srem("tags", "java", "python")  # 返回 1，"java"不存在
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.srem(name, *values)

    async def scard(self, name: str) -> int:
        """
        获取集合元素数量

        Args:
            name: 集合名

        Returns:
            元素数量，集合不存在返回 0

        Examples:
            >>> await rc.sadd("tags", "python", "redis")
            >>> count = await rc.scard("tags")  # 2
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.scard(name)

    # ==================== Sorted Set 有序集合操作 ====================

    async def zadd(self, name: str, mapping: Dict[str, float]) -> int:
        """
        向有序集合添加元素

        Args:
            name: 有序集合名
            mapping: 成员和分数的字典 {member: score, ...}

        Returns:
            成功添加的新成员数量

        Examples:
            >>> await rc.zadd("leaderboard", {"张三": 100, "李四": 95, "王五": 88})
            >>> await rc.zadd("leaderboard", {"张三": 105})  # 更新张三的分数
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.zadd(name, mapping)

    async def zrange(
        self, name: str, start: int = 0, end: int = -1, withscores: bool = False, desc: bool = False
    ) -> Union[List[str], List[Tuple[str, float]]]:
        """
        获取有序集合指定范围的成员（按分数升序或降序）

        Args:
            name: 有序集合名
            start: 起始索引，0 表示第一个元素
            end: 结束索引，-1 表示最后一个元素
            withscores: 是否返回分数
            desc: 是否按分数降序排列

        Returns:
            成员列表，或 (成员, 分数) 元组列表

        Examples:
            >>> await rc.zadd("leaderboard", {"张三": 100, "李四": 95, "王五": 88})
            >>> await rc.zrange("leaderboard", 0, -1)  # ["王五", "李四", "张三"]
            >>> await rc.zrange("leaderboard", 0, -1, withscores=True)
            # [("王五", 88.0), ("李四", 95.0), ("张三", 100.0)]
            >>> await rc.zrange("leaderboard", 0, 2, desc=True)  # ["张三", "李四", "王五"]
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.zrange(name, start, end, withscores=withscores, desc=desc)

    async def zrevrange(
        self, name: str, start: int = 0, end: int = -1, withscores: bool = False
    ) -> Union[List[str], List[Tuple[str, float]]]:
        """
        获取有序集合指定范围的成员（按分数降序）

        与 zrange(desc=True) 功能相同，提供此方法是为了兼容习惯用法

        Args:
            name: 有序集合名
            start: 起始索引，0 表示分数最高的元素
            end: 结束索引，-1 表示分数最低的元素
            withscores: 是否返回分数

        Returns:
            成员列表，或 (成员, 分数) 元组列表

        Examples:
            >>> await rc.zadd("leaderboard", {"张三": 100, "李四": 95, "王五": 88})
            >>> await rc.zrevrange("leaderboard", 0, 2)  # ["张三", "李四", "王五"]
            >>> await rc.zrevrange("leaderboard", 0, 0, withscores=True)
            # [("张三", 100.0)]，获取第一名
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.zrevrange(name, start, end, withscores=withscores)

    async def zcard(self, name: str) -> int:
        """
        获取有序集合成员数量

        Args:
            name: 有序集合名

        Returns:
            成员数量，有序集合不存在返回 0

        Examples:
            >>> await rc.zadd("leaderboard", {"张三": 100, "李四": 95})
            >>> count = await rc.zcard("leaderboard")  # 2
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.zcard(name)

    # ==================== Key 键操作 ====================

    async def delete(self, *keys: str) -> int:
        """
        删除键

        Args:
            *keys: 要删除的键名

        Returns:
            成功删除的键数量

        Examples:
            >>> await rc.set("a", "1")
            >>> await rc.set("b", "2")
            >>> await rc.delete("a", "b")  # 返回 2
            >>> await rc.delete("c")  # 返回 0，键不存在
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        """
        检查键是否存在

        Args:
            *keys: 要检查的键名

        Returns:
            存在的键数量

        Examples:
            >>> await rc.set("a", "1")
            >>> await rc.exists("a")  # 返回 1
            >>> await rc.exists("a", "b")  # 返回 1，只有a存在
            >>> await rc.exists("c")  # 返回 0
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.exists(*keys)

    async def expire(self, key: str, time: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 键名
            time: 过期时间（秒）

        Returns:
            True 表示设置成功，False 表示键不存在

        Examples:
            >>> await rc.set("session", "abc123")
            >>> await rc.expire("session", 3600)  # 1小时后过期
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.expire(key, time)

    async def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间

        Args:
            key: 键名

        Returns:
            剩余秒数
            -1 表示键存在但没有设置过期时间（永不过期）
            -2 表示键不存在

        Examples:
            >>> await rc.set("key", "value", ex=100)
            >>> ttl = await rc.ttl("key")  # 返回剩余秒数
            >>> await rc.set("perm", "value")
            >>> await rc.ttl("perm")  # -1，永不过期
            >>> await rc.ttl("notexist")  # -2，键不存在
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.ttl(key)

    async def keys(self, pattern: str = "*") -> List[str]:
        """
        获取所有匹配的键名

        注意：在大型数据库中使用可能会阻塞 Redis，生产环境慎用

        Args:
            pattern: 匹配模式，支持通配符
                * 匹配任意字符
                ? 匹配单个字符
                [abc] 匹配方括号内的任意字符

        Returns:
            键名列表

        Examples:
            >>> await rc.keys()  # 获取所有键
            >>> await rc.keys("user:*")  # 获取所有以 "user:" 开头的键
            >>> await rc.keys("*:2024")  # 获取所有以 ":2024" 结尾的键
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.keys(pattern)

    # ==================== Pipeline 管道操作 ====================

    async def pipeline(self, transaction: bool = True) -> redis.client.Pipeline:
        """
        创建异步管道对象，用于批量执行命令

        管道可以减少网络往返时间，提高性能
        事务模式下，所有命令会原子性执行

        Args:
            transaction: 是否使用事务，默认 True

        Returns:
            Pipeline 对象

        Examples:
            >>> pipe = rc.pipeline()
            >>> pipe.set("a", "1")
            >>> pipe.set("b", "2")
            >>> pipe.set("c", "3")
            >>> await pipe.execute()  # 批量执行，返回 [True, True, True]

            # 非事务模式
            >>> pipe = rc.pipeline(transaction=False)
            >>> pipe.get("a")
            >>> pipe.get("b")
            >>> await pipe.execute()  # 返回 ["1", "2"]
        """
        await self.ensure_connected()
        assert self.client is not None
        return self.client.pipeline(transaction=transaction)

    # ==================== Lua 脚本执行 ====================

    async def eval(self, script: str, numkeys: int, *keys_and_args: Any) -> Any:
        """
        执行 Lua 脚本

        Lua 脚本在 Redis 服务器端执行，保证原子性

        Args:
            script: Lua 脚本代码
            numkeys: 涉及的键数量
            *keys_and_args: 键名和其他参数
                前 numkeys 个参数是键名（KEYS[1], KEYS[2], ...）
                后面的参数是其他参数（ARGV[1], ARGV[2], ...）

        Returns:
            脚本执行结果

        Examples:
            # 原子性地设置值并设置过期时间
            >>> script = '''
            ... redis.call('set', KEYS[1], ARGV[1])
            ... redis.call('expire', KEYS[1], ARGV[2])
            ... return 1
            ... '''
            >>> await rc.eval(script, 1, "key", "value", 3600)

            # 实现限流器
            >>> script = '''
            ... local current = redis.call('incr', KEYS[1])
            ... if current == 1 then
            ...     redis.call('expire', KEYS[1], ARGV[1])
            ... end
            ... return current
            ... '''
            >>> count = await rc.eval(script, 1, "rate_limit:user:1", 60)
        """
        await self.ensure_connected()
        assert self.client is not None
        return await self.client.eval(script, numkeys, *keys_and_args)

    # ==================== 异步上下文管理器支持 ====================

    async def __aenter__(self) -> "RedisAsyncClient":
        """
        进入异步上下文管理器

        Examples:
            >>> async with RedisAsyncClient(host="127.0.0.1") as rc:
            ...     await rc.set("key", "value")
        """
        await self.ensure_connected()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出异步上下文管理器时自动关闭连接"""
        await self.close()

    # ==================== 对象表示 ====================

    def __str__(self) -> str:
        """返回客户端的字符串表示"""
        if self.startup_nodes:
            return f"RedisAsyncClient(cluster_mode, nodes={len(self.startup_nodes)})"
        return f"RedisAsyncClient(standalone, {self.host}:{self.port}/{self.db})"

    def __repr__(self) -> str:
        """返回客户端的详细表示"""
        return self.__str__()
