"""
Consul 配置中心客户端。

同步版本基于 python-consul2 的 std 模块（requests 实现），

KV 路径约定：
  1. 显式指定前缀：prefix="myapp/prod/"
  2. 自动拼接：{APP_ID}/{ENV}/  →  例如 myapp/dev/

Value 支持两种格式：
  1. 直接值：  "127.0.0.1"
  2. 多行 env 格式：
        DB_HOST=127.0.0.1
        DB_PORT=5432
"""

import io
from typing import List, Optional, Tuple

try:
    import consul  # type: ignore
except ModuleNotFoundError:
    raise ImportError("请先安装：pip install python-consul2 or uv add python-consul2")
except Exception as e:
    raise ImportError(f"python-consul2 导入失败: {e}")


class ConsulClient:
    """Consul 配置中心客户端，同步版本。"""

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
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            self._client = consul.Consul(
                host=self._host,
                port=self._port,
                scheme=self._scheme,
                token=self._token,
                timeout=self._timeout,
                **self._kwargs,
            )
        return self._client

    def get_kv(self, key: str, recurse: bool = False):
        """获取指定 key 的 KV 数据。

        :return: (index, value) 元组，value 为 None 或 item 列表
        """
        if not key:
            raise ValueError("key 必须提供")

        return self._ensure_client().kv.get(key, recurse=recurse)

    def get_raw(self, key: str) -> str:
        """获取指定 key 的原始配置值。"""
        if not key:
            raise ValueError("key 必须提供")

        _, data = self.get_kv(key)
        if not data:
            raise ValueError(f"Consul 配置为空: key={key}")
        raw = data.get("Value")
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return raw

    def get_dict(self, key: str) -> dict:
        """获取指定 key 的配置，解析为 dotenv 格式的字典。"""
        if not key:
            raise ValueError("key 必须提供")

        from dotenv import dotenv_values

        raw = self.get_raw(key=key)
        return dict(dotenv_values(stream=io.StringIO(raw)))

    def get_prefix(self, key_prefix: str) -> List[Tuple[str, str]]:
        """获取指定前缀的所有 KV 对，解析为 [(key, value), ...]。"""
        if not key_prefix:
            raise ValueError("key_prefix 必须提供")

        _, data = self.get_kv(key_prefix, recurse=True)
        if not data:
            return []

        items: List[Tuple[str, str]] = []
        for item in data:
            key = item.get("Key", "")
            value = item.get("Value") or b""
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            items.append((key, value))
        return items

    def get_prefix_dict(self, key_prefix: str) -> dict:
        """获取指定前缀的所有 KV 对，解析为配置字典。

        解析规则（与 ConfigLoader 保持一致）：
        - Value 为 "K=V" 格式：拆分为 K -> V
        - 多行时逐行解析
        - 单行非 "K=V" 格式：以 key 为配置名（子目录跳过）
        """
        items = self.get_prefix(key_prefix)
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

    def put(self, key: str, value: str, **kwargs):
        """写入 KV。"""
        if not key:
            raise ValueError("key 必须提供")

        return self._ensure_client().kv.put(key, value, **kwargs)

    def delete(self, key: str, recurse: bool = False, **kwargs):
        """删除指定 key 的 KV。"""
        if not key:
            raise ValueError("key 必须提供")

        return self._ensure_client().kv.delete(key, recurse=recurse, **kwargs)

    def shutdown(self):
        """关闭底层 HTTP session（同步版使用 requests，通常无需手动调用）。"""
        if self._client is not None:
            if hasattr(self._client.http, "session") and self._client.http.session:
                self._client.http.session.close()
            self._client = None

    def __enter__(self):
        self._ensure_client()
        return self

    def __exit__(self, *_):
        self.shutdown()
