import io
import threading
import time
from typing import Callable, Optional, TypeVar

import requests
from dotenv import dotenv_values

try:
    from etcd3gw import Etcd3Client
    from etcd3gw.exceptions import Etcd3Exception
    from etcd3gw.lease import Lease
except ModuleNotFoundError:
    raise ImportError("请先安装：pip install etcd3gw or uv add etcd3gw")
except Exception as e:
    raise ImportError(f"etcd3gw 导入失败: {e}")

T = TypeVar("T")


class EtcdClient:
    """etcd 配置中心客户端，同步版本。

    支持 etcd v3 的用户名密码认证：
    构造时传入 ``username`` / ``password`` 后，客户端会先调用
    ``/v3/auth/authenticate`` 获取 token，并将 token 写入底层
    requests.Session 的 ``Authorization`` 请求头，后续所有请求自动携带。
    """

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
        username: Optional[str] = None,
        password: Optional[str] = None,
        token_ttl: Optional[int] = None,
    ):
        self._host = host
        self._port = port
        self._protocol = protocol
        self._ca_cert = ca_cert
        self._cert_key = cert_key
        self._cert_cert = cert_cert
        self._timeout = timeout
        self._api_path = api_path
        self._username = username
        self._password = password
        self._token_ttl = token_ttl
        self._client: Optional[Etcd3Client] = None
        self._watchers: list = []
        # 认证相关状态：token 及主动过期时间
        self._auth_token: Optional[str] = None
        self._auth_token_expires_at: Optional[float] = None
        self._auth_lock = threading.Lock()

    def _build_client(self) -> Etcd3Client:
        """创建底层 Etcd3Client。

        etcd3gw 原生不支持用户名密码认证，需要认证时为其注入自定义的
        requests.Session，认证 token 通过 session 级请求头下发。
        """
        if self._username is None and self._password is None:
            return Etcd3Client(
                host=self._host,
                port=self._port,
                protocol=self._protocol,
                ca_cert=self._ca_cert,
                cert_key=self._cert_key,
                cert_cert=self._cert_cert,
                timeout=self._timeout,
                api_path=self._api_path,
            )

        if self._username is None or self._password is None:
            raise ValueError("username 和 password 必须同时提供")

        session = requests.Session()
        if self._ca_cert is not None:
            session.verify = self._ca_cert
        if self._cert_cert is not None and self._cert_key is not None:
            session.cert = (self._cert_cert, self._cert_key)

        return Etcd3Client(
            host=self._host,
            port=self._port,
            protocol=self._protocol,
            ca_cert=self._ca_cert,
            cert_key=self._cert_key,
            cert_cert=self._cert_cert,
            timeout=self._timeout,
            api_path=self._api_path,
            session=session,
        )

    def _ensure_client(self) -> Etcd3Client:
        client = self._client
        if client is None:
            client = self._build_client()
            self._client = client
        return client

    def _is_authenticated(self) -> bool:
        """是否启用了用户名密码认证。"""
        return self._username is not None or self._password is not None

    def _do_authenticate(self):
        """调用 /v3/auth/authenticate 获取 token，并写入 session 请求头。"""
        if not self._is_authenticated():
            return

        client = self._ensure_client()
        url = client.get_url("/auth/authenticate")
        payload = {"name": self._username, "password": self._password}
        try:
            response = client.session.post(url, json=payload, timeout=client.timeout)
        except requests.exceptions.RequestException as e:
            raise Etcd3Exception(f"Etcd 认证请求失败: {e}")
        if response.status_code != requests.codes["ok"]:
            raise Etcd3Exception(
                f"Etcd 认证失败: status={response.status_code}, reason={response.reason}, text={response.text}",
            )

        data = response.json()
        token = data.get("token")
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        self._auth_token = token if token else None
        if token:
            # authenticate 响应一般只有 token，ttl 用于主动过期刷新
            ttl = data.get("ttl") or self._token_ttl
            self._auth_token_expires_at = time.monotonic() + ttl if ttl else None
            client.session.headers["Authorization"] = token
        else:
            # etcd 未启用认证时返回空 token，视为无需认证
            self._auth_token_expires_at = None
            client.session.headers.pop("Authorization", None)

    def _ensure_auth(self):
        """懒认证：无 token 或 token 过期时重新认证。"""
        if not self._is_authenticated():
            return

        with self._auth_lock:
            expired = self._auth_token is None or (
                self._auth_token_expires_at is not None and time.monotonic() >= self._auth_token_expires_at
            )
            if expired:
                self._do_authenticate()

    def _invalidate_auth(self):
        """使当前 token 失效，下次请求前重新认证。"""
        with self._auth_lock:
            self._auth_token = None
            self._auth_token_expires_at = None
            client = self._client
            if client is not None:
                client.session.headers.pop("Authorization", None)

    def _execute(self, op: Callable[[], T]) -> T:
        """执行带认证的操作，认证失效时重新认证并重试一次。"""
        for attempt in range(2):
            self._ensure_auth()
            try:
                return op()
            except Etcd3Exception:
                if attempt == 0 and self._is_authenticated():
                    self._invalidate_auth()
                    continue
                raise
        raise RuntimeError("unreachable")

    def get_raw(self, key: str) -> str:
        """获取指定 key 的原始配置值。"""
        if not key:
            raise ValueError("key 必须提供")

        client = self._ensure_client()
        values = self._execute(lambda: client.get(key))
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

    def get_prefix(self, key_prefix: str) -> list[tuple[str, str]]:
        """获取指定前缀的所有 KV 对。

        :param key_prefix: key 前缀
        :return: [(key, value), ...]，key 和 value 均已解码为 str
        """
        if not key_prefix:
            raise ValueError("key_prefix 必须提供")

        client = self._ensure_client()
        values = self._execute(lambda: client.get_prefix(key_prefix))
        items: list[tuple[str, str]] = []
        for value, kv in values:
            k = kv.get("key", key_prefix)
            if isinstance(k, bytes):
                k = k.decode("utf-8")
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            items.append((k, value))
        return items

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

        client = self._ensure_client()
        iterator, cancel = self._execute(lambda: client.watch(key))
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

    def put(self, key: str, value: str, lease: Optional[Lease] = None):
        """写入配置。

        :param key: 键
        :param value: 值
        :param lease: 可选，etcd3gw 的 Lease 对象
        """
        client = self._ensure_client()
        self._execute(lambda: client.put(key, value, lease=lease))

    def delete(self, key: str):
        """删除指定 key 的配置。"""
        if not key:
            raise ValueError("key 必须提供")

        client = self._ensure_client()
        self._execute(lambda: client.delete(key))

    def shutdown(self):
        """关闭客户端，清理所有 watcher 和连接。"""
        for cancel in self._watchers:
            cancel()
        self._watchers.clear()

        client = self._client
        if client is not None:
            client.session.close()
            self._client = None

    def __enter__(self):
        self._ensure_client()
        return self

    def __exit__(self, *_):
        self.shutdown()
