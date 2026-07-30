"""
aetcd 不支持TLS
"""

import io
from typing import Callable, List, Optional, Tuple

from dotenv import dotenv_values


class AsyncEtcdClient:
    """基于 aetcd 的异步 etcd 配置中心客户端。"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 2379,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: Optional[int] = None,
        connect_wait_timeout: int = 3,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._timeout = timeout
        self._connect_wait_timeout = connect_wait_timeout
        self._client = None
        self._watchers: list = []

    async def _ensure_client(self):
        if self._client is not None:
            return

        from aetcd import Client as AetcdClient

        self._client = AetcdClient(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            timeout=self._timeout,
            connect_wait_timeout=self._connect_wait_timeout,
        )

    async def get_raw(self, key: str) -> str:
        """获取指定 key 的原始配置值。"""
        if not key:
            raise ValueError("key 必须提供")

        from aetcd.utils import to_bytes

        await self._ensure_client()
        result = await self._client.get(to_bytes(key))
        if result is None:
            raise ValueError(f"Etcd 配置为空: key={key}")
        raw = result.value
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return raw

    async def get_dict(self, key: str) -> dict:
        """获取指定 key 的配置，解析为 dotenv 格式的字典。"""
        if not key:
            raise ValueError("key 必须提供")

        raw = await self.get_raw(key=key)
        return dict(dotenv_values(stream=io.StringIO(raw)))

    async def get_prefix(self, key_prefix: str) -> List[Tuple[str, str]]:
        """获取指定前缀的所有 KV 对。

        :param key_prefix: key 前缀
        :return: [(key, value), ...]，key 和 value 均已解码为 str
        """
        if not key_prefix:
            raise ValueError("key_prefix 必须提供")

        from aetcd.utils import to_bytes

        await self._ensure_client()
        result = await self._client.get_prefix(to_bytes(key_prefix))
        items: List[Tuple[str, str]] = []
        for kv in result:
            k = kv.key.decode("utf-8") if isinstance(kv.key, bytes) else kv.key
            v = kv.value.decode("utf-8") if isinstance(kv.value, bytes) else kv.value
            items.append((k, v))
        return items

    async def add_listener(
        self,
        callback: Callable[[str, str], None],
        key: str,
    ):
        """监听指定 key 的配置变更。

        :param callback: 回调函数，接收 (key, value)
        :param key: 监听的 key
        """
        if not key:
            raise ValueError("key 必须提供")

        from aetcd.utils import to_bytes

        await self._ensure_client()

        watch = await self._client.watch(to_bytes(key))
        self._watchers.append(watch)

        async def _watch_loop():
            try:
                async for event in watch:
                    event_key = event.kv.key
                    event_value = event.kv.value
                    if isinstance(event_key, bytes):
                        event_key = event_key.decode("utf-8")
                    if isinstance(event_value, bytes):
                        event_value = event_value.decode("utf-8")
                    callback(event_key, event_value)
            except Exception:
                pass

        import asyncio

        asyncio.create_task(_watch_loop())

    async def put(self, key: str, value: str, lease: Optional[int] = None):
        """写入配置。

        :param key: 键
        :param value: 值
        :param lease: 可选，租约 ID
        """
        if not key:
            raise ValueError("key 必须提供")

        from aetcd.utils import to_bytes

        await self._ensure_client()
        await self._client.put(to_bytes(key), to_bytes(value), lease=lease)

    async def delete(self, key: str):
        """删除指定 key 的配置。"""
        if not key:
            raise ValueError("key 必须提供")

        from aetcd.utils import to_bytes

        await self._ensure_client()
        await self._client.delete(to_bytes(key))

    async def shutdown(self):
        """关闭客户端，清理所有 watcher 和连接。"""
        for watch in self._watchers:
            await watch.cancel()
        self._watchers.clear()

        if self._client is not None:
            await self._client.close()
            self._client = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, *_):
        await self.shutdown()
