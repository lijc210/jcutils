# nacos_client.py
import io
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
    raise ImportError('请先安装：pip install jcutils[nacos] or uv add "jcutils[nacos]"')
except Exception as e:
    raise ImportError(f"nacos-sdk-python 导入失败: {e}")


class NacosClient:
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

    async def _ensure_client(self):
        if self._client is not None:
            return

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
        self._client = await NacosConfigService.create_config_service(client_config)

    async def get_raw(self, data_id: Optional[str] = None, group: Optional[str] = None) -> str:
        if not data_id or not group:
            raise ValueError("data_id 和 group 必须提供")

        await self._ensure_client()
        raw = await self._client.get_config(
            ConfigParam(
                data_id=data_id,
                group=group,
            )
        )
        if not raw:
            raise ValueError(f"Nacos 配置为空: data_id={data_id}, group={group}")
        return raw

    async def get_dict(self, data_id: Optional[str] = None, group: Optional[str] = None) -> dict:
        if not data_id or not group:
            raise ValueError("data_id 和 group 必须提供")

        raw = await self.get_raw(data_id=data_id, group=group)
        return dict(dotenv_values(stream=io.StringIO(raw)))

    async def add_listener(
        self,
        callback: Callable[[str, str, str, str], None],
        data_id: Optional[str] = None,
        group: Optional[str] = None,
    ):
        if not data_id or not group:
            raise ValueError("data_id 和 group 必须提供")

        await self._ensure_client()
        await self._client.add_listener(
            data_id,
            group,
            callback,
        )

    async def shutdown(self):
        if self._client is not None:
            await self._client.shutdown()
            self._client = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, *_):
        await self.shutdown()


if __name__ == "__main__":
    pass
