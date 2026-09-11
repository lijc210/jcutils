"""
Nacos 配置中心客户端（同步版本）。

nacos-sdk-python 的 NacosConfigService 为纯异步实现，
同步版本通过维护一个专用后台事件循环线程来驱动它，
所有操作通过 run_coroutine_threadsafe 提交到该线程执行。

注意：
1. add_listener 的回调会在后台事件循环线程中被调用；
2. 使用完毕后请调用 shutdown() 或使用 with 语句释放资源。
"""

import asyncio
import io
import threading
from typing import Callable, Optional

from dotenv import dotenv_values

try:
    from v2.nacos import (  # type: ignore
        ClientConfigBuilder,
        ConfigParam,
        GRPCConfig,
        NacosConfigService,
    )
except ModuleNotFoundError:
    raise ImportError("请先安装：pip install nacos-sdk-python or uv add nacos-sdk-python")
except Exception as e:
    raise ImportError(f"nacos-sdk-python 导入失败: {e}")


class NacosClient:
    """Nacos 配置中心客户端，同步版本。"""

    def __init__(
        self,
        server: str,
        namespace: str,
        username: str,
        password: str,
        grpc_timeout: int = 5000,
    ):
        self._server = server
        self._namespace = namespace
        self._username = username
        self._password = password
        self._grpc_timeout = grpc_timeout
        self._client = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None

    @staticmethod
    def _loop_runner(loop: asyncio.AbstractEventLoop) -> None:
        """后台事件循环线程的主函数。"""
        asyncio.set_event_loop(loop)
        loop.run_forever()
        loop.close()

    def _ensure_running(self) -> None:
        """确保后台事件循环线程处于运行状态，必要时重建。"""
        if (
            self._loop is not None
            and not self._loop.is_closed()
            and self._loop_thread is not None
            and self._loop_thread.is_alive()
        ):
            return

        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._loop_runner,
            args=(self._loop,),
            daemon=True,
            name="jcutils-nacos-loop",
        )
        self._loop_thread.start()

    def _submit(self, coro_factory):
        """将协程提交到后台事件循环执行并同步等待结果。

        :param coro_factory: 接收 NacosConfigService 实例、
                             返回协程的可调用对象

        在 shutdown 之后再次调用会自动重建事件循环并重新创建客户端。
        """
        self._ensure_running()
        assert self._loop is not None
        loop = self._loop

        if self._client is None:
            client_config = (
                ClientConfigBuilder()
                .server_address(self._server)
                .namespace_id(self._namespace)
                .username(self._username)
                .password(self._password)
                .log_level("WARNING")
                .grpc_config(GRPCConfig(grpc_timeout=self._grpc_timeout))
                .build()
            )
            self._client = asyncio.run_coroutine_threadsafe(
                NacosConfigService.create_config_service(client_config), loop
            ).result()

        return asyncio.run_coroutine_threadsafe(coro_factory(self._client), loop).result()

    def get_raw(self, data_id: Optional[str] = None, group: Optional[str] = None) -> str:
        if not data_id or not group:
            raise ValueError("data_id 和 group 必须提供")

        raw = self._submit(
            lambda client: client.get_config(
                ConfigParam(
                    data_id=data_id,
                    group=group,
                )
            )
        )
        if not raw:
            raise ValueError(f"Nacos 配置为空: data_id={data_id}, group={group}")
        return raw

    def get_dict(self, data_id: Optional[str] = None, group: Optional[str] = None) -> dict:
        if not data_id or not group:
            raise ValueError("data_id 和 group 必须提供")

        raw = self.get_raw(data_id=data_id, group=group)
        return dict(dotenv_values(stream=io.StringIO(raw)))

    def add_listener(
        self,
        callback: Callable[[str, str, str, str], None],
        data_id: Optional[str] = None,
        group: Optional[str] = None,
    ):
        """监听指定配置的变更。

        回调会在后台事件循环线程中被调用，签名需为
        callback(tenant, data_id, group, content)。
        """
        if not data_id or not group:
            raise ValueError("data_id 和 group 必须提供")

        self._submit(
            lambda client: client.add_listener(
                data_id,
                group,
                callback,
            )
        )

    def shutdown(self):
        """关闭客户端，停止后台事件循环线程。"""
        if self._loop is None or self._loop.is_closed():
            self._client = None
            return

        try:
            if self._client is not None:
                asyncio.run_coroutine_threadsafe(self._client.shutdown(), self._loop).result()
                self._client = None
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._loop_thread is not None and self._loop_thread.is_alive():
                self._loop_thread.join(timeout=10)
            self._loop = None
            self._loop_thread = None

    def __enter__(self):
        self._submit(lambda client: asyncio.sleep(0))  # 触发客户端初始化
        return self

    def __exit__(self, *_):
        self.shutdown()
