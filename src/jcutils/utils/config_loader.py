# coding: utf-8
"""
nacos-sdk-python
pyapollo-zenkilan
"""

import asyncio
import os
from typing import TYPE_CHECKING

from dotenv import dotenv_values, load_dotenv

# 先加载 .env（不覆盖已有环境变量）
load_dotenv(override=False)

SCHEMA_PATH = os.path.join(os.getcwd(), "schema.py")


class ConfigLoader:
    """配置加载器"""

    SCHEMA_PATH = SCHEMA_PATH
    _config_dict = None
    _app_config = None

    @staticmethod
    def _merge_with_env(source_config: dict) -> dict:
        """只用环境变量覆盖配置源中已有的 key，避免系统环境变量污染业务配置"""
        return {k: os.environ.get(k, v) for k, v in source_config.items()}

    @classmethod
    def _load_from_nacos(cls) -> dict:
        """从 Nacos 拉取配置，合并环境变量（环境变量优先级更高）"""
        from ..utils.nacos_client import NacosClient

        NACOS_SERVER = os.getenv("NACOS_SERVER", default="")
        NACOS_NAMESPACE = os.getenv("NACOS_NAMESPACE", default="")
        NACOS_GROUP = os.getenv("NACOS_GROUP", default="")
        NACOS_DATA_ID = os.getenv("NACOS_DATA_ID", default="")
        NACOS_USERNAME = os.getenv("NACOS_USERNAME", default="")
        NACOS_PASSWORD = os.getenv("NACOS_PASSWORD", default="")

        if (
            not NACOS_SERVER
            or not NACOS_NAMESPACE
            or not NACOS_GROUP
            or not NACOS_DATA_ID
            or not NACOS_USERNAME
            or not NACOS_PASSWORD
        ):
            raise ValueError(
                "使用 Nacos 时必须配置 NACOS_SERVER、NACOS_NAMESPACE、NACOS_GROUP、NACOS_DATA_ID、NACOS_USERNAME 和 NACOS_PASSWORD"
            )

        print(f"[config] 从 Nacos 加载配置: {NACOS_SERVER}")
        print(f"[config] NACOS_NAMESPACE: {NACOS_NAMESPACE}，NACOS_DATA_ID: {NACOS_DATA_ID}")

        nacos_client = NacosClient(
            server=NACOS_SERVER, namespace=NACOS_NAMESPACE, username=NACOS_USERNAME, password=NACOS_PASSWORD
        )

        async def _fetch():
            async with nacos_client:
                return await nacos_client.get_dict(NACOS_DATA_ID, NACOS_GROUP)

        nacos_config = asyncio.run(_fetch())
        if not nacos_config:
            raise Exception(f"Nacos 配置拉取失败: DATA_ID={NACOS_DATA_ID}, GROUP={NACOS_GROUP}")

        return cls._merge_with_env(nacos_config)

    @classmethod
    def _load_from_apollo(cls) -> dict:
        """从 Apollo 拉取所有命名空间配置，合并环境变量（环境变量优先级更高）"""
        from pyapollo.client import ApolloClient  # type: ignore
        from pyapollo.settings import ApolloSettingsConfig  # type: ignore

        APOLLO_META_SERVER_ADDRESS = os.getenv("APOLLO_META_SERVER_ADDRESS")
        APOLLO_APP_ID = os.getenv("APOLLO_APP_ID")

        if not APOLLO_META_SERVER_ADDRESS:
            raise ValueError("APOLLO_META_SERVER_ADDRESS 未配置")
        if not APOLLO_APP_ID:
            raise ValueError("使用 Apollo 时必须配置 APOLLO_APP_ID")

        print(f"[config] 从 Apollo 加载配置: {APOLLO_META_SERVER_ADDRESS}")

        settings = ApolloSettingsConfig(
            meta_server_address=APOLLO_META_SERVER_ADDRESS,
            app_id=APOLLO_APP_ID,
            using_app_secret=os.getenv("APOLLO_USING_APP_SECRET", "false").lower() == "true",
            app_secret=os.getenv("APOLLO_APP_SECRET", ""),
            cluster=os.getenv("APOLLO_CLUSTER", "default"),
            env=os.getenv("APOLLO_ENV", "DEV"),
            namespaces=os.getenv("APOLLO_NAMESPACES", "application").split(","),
        )

        client = ApolloClient(settings=settings)

        namespaces = settings.namespaces or ["application"]
        apollo_config = {}
        for ns in namespaces:
            ns_config = client._cache.get(ns.strip(), {})
            apollo_config.update(ns_config)

        if not apollo_config:
            raise Exception(f"Apollo 配置为空: APP_ID={APOLLO_APP_ID}, NAMESPACES={namespaces}")

        print(f"[config] Apollo 配置加载成功，共 {len(apollo_config)} 个配置项")
        return cls._merge_with_env(apollo_config)

    @classmethod
    def _load_from_local(cls) -> dict:
        """从 .env 读取配置，合并环境变量"""
        print("[config] 从 .env 加载配置")
        local = dict(dotenv_values(".env"))
        return cls._merge_with_env(local)

    @staticmethod
    def _infer_type(value: str) -> str:
        if value.lower() in ("true", "false"):
            return "bool"
        try:
            int(value)
            return "int"
        except ValueError:
            pass
        return "str"

    @classmethod
    def _build_schema_content(cls, raw: dict) -> str:
        lines = [
            "from pydantic import BaseModel",
            "",
            "",
            "class AppConfig(BaseModel):",
        ]
        if not raw:
            lines.append("    pass")
        for key, value in sorted(raw.items()):
            t = cls._infer_type(str(value))
            lines.append(f"    {key}: {t}")
        return "\n".join(lines)

    @classmethod
    def _sync_schema(cls, raw: dict) -> None:
        """判断 schema.py 是否存在或发生变化，按需生成"""
        new_content = cls._build_schema_content(raw)

        if os.path.exists(cls.SCHEMA_PATH):
            with open(cls.SCHEMA_PATH, "r", encoding="utf-8") as f:
                existing_content = f.read()
            if existing_content == new_content:
                print("[config] schema.py 无变化，跳过生成")
                return
            print("[config] schema.py 已变化，更新生成")
        else:
            print("[config] schema.py 不存在，生成中")

        with open(cls.SCHEMA_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[config] schema.py 生成完成，共 {len(raw)} 个配置项")

    @classmethod
    def load_config(cls) -> dict:
        """
        根据 CONFIG_SOURCE 判断配置来源：
        - nacos  → 从 Nacos 拉取，再合并环境变量
        - apollo → 从 Apollo 拉取，再合并环境变量
        - local（默认）→ 从 .env 读取，再合并环境变量
        """
        CONFIG_SOURCE = os.getenv("CONFIG_SOURCE", "local").lower()

        if CONFIG_SOURCE == "nacos":
            raw = cls._load_from_nacos()
        elif CONFIG_SOURCE == "apollo":
            raw = cls._load_from_apollo()
        else:
            raw = cls._load_from_local()

        cls._sync_schema(raw)
        return raw

    @classmethod
    def get_config_dict(cls) -> dict:
        """获取配置字典"""
        if cls._config_dict is None:
            cls._config_dict = cls.load_config()
        return cls._config_dict


# 向后兼容：模块级变量
if TYPE_CHECKING:
    from schema import AppConfig  # IDE 和类型检查器能识别 # noqa: E402  # type: ignore
else:
    try:
        from schema import AppConfig
    except ImportError:
        from pydantic import BaseModel as AppConfig


app_config: AppConfig = AppConfig.model_validate(ConfigLoader.get_config_dict())
