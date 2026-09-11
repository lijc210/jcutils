"""
Consul 配置中心客户端，异步版本。

基于 httpx 直接调用 Consul HTTP API。

KV 路径约定：
  1. 显式指定前缀：prefix="myapp/prod/"
  2. 自动拼接：{APP_ID}/{ENV}/  →  例如 myapp/dev/

Value 支持两种格式：
  1. 直接值：  "127.0.0.1"
  2. 多行 env 格式：
        DB_HOST=127.0.0.1
        DB_PORT=5432
"""

import base64
import io
from typing import List, Optional, Tuple

try:
    import httpx
except ModuleNotFoundError:
    raise ImportError("请先安装：pip install httpx or uv add httpx")
except Exception as e:
    raise ImportError(f"httpx 导入失败: {e}")


class AsyncConsulClient:
    """Consul 配置中心客户端，异步版本（基于 httpx）。"""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8500,
        scheme: str = "http",
        token: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        self._host = host
        self._port = port
        self._scheme = scheme
        self._token = token
        self._timeout = timeout
        self._kwargs = kwargs
        self._base_url = f"{scheme}://{host}:{port}"
        self._client: Optional[httpx.AsyncClient] = None

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {}
            if self._token:
                headers["X-Consul-Token"] = self._token
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=headers,
                timeout=self._timeout,
                **self._kwargs,
            )
        return self._client

    async def get_kv(self, key: str, recurse: bool = False):
        """获取指定 key 的 KV 数据。

        :return: (index, value) 元组，value 为 None 或 item 列表，
                 item 中的 Value 已解码为 str
        """
        if not key:
            raise ValueError("key 必须提供")

        client = self._ensure_client()
        params = {"recurse": "true"} if recurse else None
        resp = await client.get(f"/v1/kv/{key}", params=params)
        if resp.status_code == 404:
            return 0, None
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return 0, None

        for item in data:
            value = item.get("Value")
            if value:
                item["Value"] = base64.b64decode(value).decode("utf-8")

        index = resp.headers.get("X-Consul-Index", 0)
        return int(index), data

    async def get_raw(self, key: str) -> str:
        """获取指定 key 的原始配置值。"""
        if not key:
            raise ValueError("key 必须提供")

        _, data = await self.get_kv(key)
        if not data:
            raise ValueError(f"Consul 配置为空: key={key}")
        return data[0].get("Value") or ""

    async def get_dict(self, key: str) -> dict:
        """获取指定 key 的配置，解析为 dotenv 格式的字典。"""
        if not key:
            raise ValueError("key 必须提供")

        from dotenv import dotenv_values

        raw = await self.get_raw(key=key)
        return dict(dotenv_values(stream=io.StringIO(raw)))

    async def get_prefix(self, key_prefix: str) -> List[Tuple[str, str]]:
        """获取指定前缀的所有 KV 对，解析为 [(key, value), ...]。"""
        if not key_prefix:
            raise ValueError("key_prefix 必须提供")

        _, data = await self.get_kv(key_prefix, recurse=True)
        if not data:
            return []

        items: List[Tuple[str, str]] = []
        for item in data:
            key = item.get("Key", "")
            value = item.get("Value") or ""
            items.append((key, value))
        return items

    async def get_prefix_dict(self, key_prefix: str) -> dict:
        """获取指定前缀的所有 KV 对，解析为配置字典。

        解析规则（与同步版 get_prefix_dict 保持一致）：
        - Value 为 "K=V" 格式：拆分为 K -> V
        - 多行时逐行解析
        - 单行非 "K=V" 格式：以 key 为配置名（子目录跳过）
        """
        items = await self.get_prefix(key_prefix)
        if not items:
            raise Exception(f"Consul KV 配置为空或路径不存在: prefix={key_prefix}")

        result = {}
        for key, value in items:
            for aline in value.splitlines():
                alist = aline.split("=", 1)
                if len(alist) == 2:
                    k, v = alist
                    result[k.strip()] = v.strip()
                else:
                    if "/" in key:
                        continue
                    result[key.strip()] = aline.strip()
        return result

    async def put(self, key: str, value: str):
        """写入 KV。"""
        if not key:
            raise ValueError("key 必须提供")

        client = self._ensure_client()
        resp = await client.put(f"/v1/kv/{key}", content=value)
        resp.raise_for_status()
        return True

    async def delete(self, key: str, recurse: bool = False):
        """删除指定 key 的 KV。"""
        if not key:
            raise ValueError("key 必须提供")

        client = self._ensure_client()
        params = {"recurse": "true"} if recurse else None
        resp = await client.delete(f"/v1/kv/{key}", params=params)
        resp.raise_for_status()
        return True

    async def shutdown(self):
        """关闭底层 httpx 连接。"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        self._ensure_client()
        return self

    async def __aexit__(self, *_):
        await self.shutdown()
