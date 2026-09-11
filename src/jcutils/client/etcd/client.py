import io
import threading
from typing import Callable, Optional

from dotenv import dotenv_values

try:
    from etcd3gw import Etcd3Client  # type: ignore
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install jcutils[etcd] or uv add "jcutils[etcd]"')
except Exception as e:
    raise ImportError(f"etcd3gw 导入失败: {e}")


class EtcdClient:
    """etcd 配置中心客户端，同步版本。"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 2379,
        protocol: str = "http",
        ca_cert: Optional[str] = None,
        cert_key: Optional[str] = None,
        cert_cert: Optional[str] = None,
        timeout: Optional[int] = None,
        api_path: Optional[str] = "/v3/",
    ):
        self._host = host
        self._port = port
        self._protocol = protocol
        self._ca_cert = ca_cert
        self._cert_key = cert_key
        self._cert_cert = cert_cert
        self._timeout = timeout
        self._api_path = api_path
        self._client = None
        self._watchers: list = []

    def _ensure_client(self):
        if self._client is not None:
            return

        self._client = Etcd3Client(
            host=self._host,
            port=self._port,
            protocol=self._protocol,
            ca_cert=self._ca_cert,
            cert_key=self._cert_key,
            cert_cert=self._cert_cert,
            timeout=self._timeout,
            api_path=self._api_path,
        )

    def get_raw(self, key: str) -> str:
        """获取指定 key 的原始配置值。"""
        if not key:
            raise ValueError("key 必须提供")

        self._ensure_client()
        values = self._client.get(key)
        if not values:
            raise ValueError(f"Etcd 配置为空: key={key}")
        raw = values[0]
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return raw

    def get_dict(self, key: str) -> dict:
        """获取指定 key 的配置，解析为 dotenv 格式的字典。"""
        if not key:
            raise ValueError("key 必须提供")

        raw = self.get_raw(key=key)
        return dict(dotenv_values(stream=io.StringIO(raw)))

    def add_listener(
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

        self._ensure_client()

        iterator, cancel = self._client.watch(key)
        self._watchers.append(cancel)

        def _watch_loop():
            try:
                while True:
                    event = next(iterator)
                    if event is None:
                        break
                    kv = event.get("kv", {})
                    event_key = kv.get("key", key)
                    event_value = kv.get("value", "")
                    if isinstance(event_key, bytes):
                        event_key = event_key.decode("utf-8")
                    if isinstance(event_value, bytes):
                        event_value = event_value.decode("utf-8")
                    callback(event_key, event_value)
            except StopIteration:
                pass

        t = threading.Thread(target=_watch_loop, daemon=True)
        t.start()

    def put(self, key: str, value: str, lease: Optional[int] = None):
        """写入配置。

        :param key: 键
        :param value: 值
        :param lease: 可选，租约 ID
        """
        self._ensure_client()
        self._client.put(key, value, lease=lease)

    def delete(self, key: str):
        """删除指定 key 的配置。"""
        if not key:
            raise ValueError("key 必须提供")

        self._ensure_client()
        self._client.delete(key)

    def shutdown(self):
        """关闭客户端，清理所有 watcher 和连接。"""
        for cancel in self._watchers:
            cancel()
        self._watchers.clear()

        if self._client is not None:
            self._client.session.close()
            self._client = None

    def __enter__(self):
        self._ensure_client()
        return self

    def __exit__(self, *_):
        self.shutdown()
