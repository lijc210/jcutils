# coding: utf-8
"""
nacos-sdk-python
pyapollo-zenkilan
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import os
import sys
from typing import TYPE_CHECKING

from dotenv import dotenv_values, load_dotenv

from .platform_ import is_mac, is_windows

if TYPE_CHECKING:
    from schema import AppConfig  # 只有 IDE/类型检查时才执行，运行时跳过

SCHEMA_PATH = os.path.join(os.getcwd(), "schema.py")

# 先加载 .env（不覆盖已有环境变量）
load_dotenv(override=False)


class ConfigLoader:
    """配置加载器"""

    _config_dict = {}

    @staticmethod
    def _merge_with_env(source_config: dict) -> dict:
        """只用环境变量覆盖配置源中已有的 key，避免系统环境变量污染业务配置"""
        return {k: os.environ.get(k, v) for k, v in source_config.items()}

    @classmethod
    def _load_from_nacos(cls) -> dict:
        """从 Nacos 拉取配置，合并环境变量（环境变量优先级更高）"""
        from ..utils.nacos_client import NacosClient

        NACOS_SERVER = os.getenv("NACOS_SERVER", default="")
        NACOS_NAMESPACE = os.getenv("NACOS_NAMESPACE") or os.getenv("ENV", default="dev").lower()
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

        nacos_config["APP_NAME"] = NACOS_DATA_ID
        nacos_config["ENV"] = NACOS_NAMESPACE

        return cls._merge_with_env(nacos_config)

    @classmethod
    def _load_from_apollo(cls) -> dict:
        """从 Apollo 拉取所有命名空间配置，合并环境变量（环境变量优先级更高）"""
        from pyapollo.client import ApolloClient  # type: ignore

        APOLLO_META_SERVER_ADDRESS = os.getenv("APOLLO_META_SERVER_ADDRESS", default="")
        APOLLO_APP_ID = os.getenv("APOLLO_APP_ID", default="")
        APOLLO_APP_SECRET = os.getenv("APOLLO_APP_SECRET", default="")
        APOLLO_CLUSTER = os.getenv("APOLLO_CLUSTER", default="default")
        APOLLO_ENV = os.getenv("APOLLO_ENV") or os.getenv("ENV", "DEV")
        APOLLO_NAMESPACES = os.getenv("APOLLO_NAMESPACES", "application").split(",")

        if not APOLLO_META_SERVER_ADDRESS:
            raise ValueError("APOLLO_META_SERVER_ADDRESS 未配置")
        if not APOLLO_APP_ID:
            raise ValueError("使用 Apollo 时必须配置 APOLLO_APP_ID")

        print(f"[config] 从 Apollo 加载配置: {APOLLO_META_SERVER_ADDRESS}")
        print(f"[config] APOLLO_APP_ID: {APOLLO_APP_ID}，APOLLO_ENV: {APOLLO_ENV}")

        client = ApolloClient(
            meta_server_address=APOLLO_META_SERVER_ADDRESS,
            app_id=APOLLO_APP_ID,
            app_secret=APOLLO_APP_SECRET,
            cluster=APOLLO_CLUSTER,
            env=APOLLO_ENV,
            namespaces=APOLLO_NAMESPACES,
        )

        apollo_config = {}
        for ns in APOLLO_NAMESPACES:
            ns_config = client._cache.get(ns.strip(), {})
            for k, v in ns_config.items():
                apollo_config[k] = str(v) if isinstance(v, dict) else v

        if not apollo_config:
            raise Exception(f"Apollo 配置为空: APP_ID={APOLLO_APP_ID}, NAMESPACES={APOLLO_NAMESPACES}")

        apollo_config["APP_NAME"] = APOLLO_APP_ID
        apollo_config["ENV"] = APOLLO_ENV

        return cls._merge_with_env(apollo_config)

    @classmethod
    def _load_from_local(cls) -> dict:
        """从 .env 读取配置，合并环境变量"""
        print("[config] 从 .env 加载配置")
        ENV = os.getenv("ENV", default="dev").lower()
        APP_NAME = os.getenv("APP_NAME", default="")
        local_config = dict(dotenv_values(".env"))
        local_config["APP_NAME"] = APP_NAME
        local_config["ENV"] = ENV
        return cls._merge_with_env(local_config)

    @staticmethod
    def _infer_type(value: str) -> str:
        if value.lower() in ("true", "false"):
            return "bool"
        try:
            int(value)
            return "int"
        except ValueError:
            pass
        try:
            float(value)
            return "float"
        except ValueError:
            pass
        return "str"

    @staticmethod
    def _format_key(key: str) -> str:
        return key.replace("-", "_").replace(".", "_").upper()

    @classmethod
    def _build_schema_content(cls, raw: dict) -> str:
        lines = [
            "from pydantic import BaseModel",
            "from typing import Optional",
            "",
            "",
            "class AppConfig(BaseModel):",
        ]
        if not raw:
            lines.append("    pass")
        for key, value in sorted(raw.items()):
            k = cls._format_key(key)
            t = cls._infer_type(str(value))
            lines.append(f"    {k}: Optional[{t}] = None")
        return "\n".join(lines)

    @classmethod
    def _load_schema_module(cls) -> type[AppConfig]:
        """动态加载或重载 schema 模块，返回最新的 AppConfig 类"""
        if "schema" in sys.modules:
            module = importlib.reload(sys.modules["schema"])
        else:
            spec = importlib.util.spec_from_file_location("schema", SCHEMA_PATH)
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules["schema"] = module
        return module.AppConfig

    @classmethod
    def sync_schema(cls) -> type[AppConfig]:
        """判断 schema.py 是否存在或发生变化，按需生成，返回最新的 AppConfig 类"""
        new_content = cls._build_schema_content(cls._config_dict)

        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                existing_content = f.read()
            if existing_content == new_content:
                print("[config] schema.py 无变化，跳过生成")
            else:
                print("[config] schema.py 已变化，更新生成")
                with open(SCHEMA_PATH, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"[config] schema.py 更新完成，共 {len(cls._config_dict)} 个配置项")
        else:
            print("[config] schema.py 不存在，生成中")
            with open(SCHEMA_PATH, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[config] schema.py 生成完成，共 {len(cls._config_dict)} 个配置项")

        return cls._load_schema_module()

    @classmethod
    def _get_dirs(cls, app_name: str) -> tuple[str, str]:
        if is_windows():
            drive = "D:\\" if os.path.exists("D:\\") else "C:\\"
            return os.path.join(drive, "data", app_name), os.path.join(drive, "logs", app_name)
        elif is_mac():
            home = os.path.expanduser("~")
            return os.path.join(home, "data", app_name), os.path.join(home, "logs", app_name)
        else:
            return os.path.join("/data", app_name), os.path.join("/logs", app_name)

    @classmethod
    def load_config(cls, init_dirs: bool = False) -> AppConfig:
        """
        根据 CONFIG_SOURCE 判断配置来源：
        - nacos  → 从 Nacos 拉取，再合并环境变量
        - apollo → 从 Apollo 拉取，再合并环境变量
        - local（默认）→ 从 .env 读取，再合并环境变量
        """
        CONFIG_SOURCE = os.getenv("CONFIG_SOURCE", "local").lower()

        if CONFIG_SOURCE == "nacos":
            config_dict = cls._load_from_nacos()
        elif CONFIG_SOURCE == "apollo":
            config_dict = cls._load_from_apollo()
        else:
            config_dict = cls._load_from_local()

        cls._config_dict = config_dict

        if init_dirs:
            # 按需创建目录
            app_name = config_dict.get("APP_NAME", "")
            data_dir, logs_dir = cls._get_dirs(app_name)
            for d in [data_dir, logs_dir]:
                os.makedirs(d, exist_ok=True)
            # 注入到 config_dict，schema 会自动生成这两个字段
            config_dict["DATA_DIR"] = data_dir
            config_dict["LOGS_DIR"] = logs_dir

        # 生成/更新 schema.py，并拿到当次运行最新的 AppConfig 类
        LatestAppConfig = cls.sync_schema()

        # 只传入 schema 中已定义的字段，忽略多余的 key
        app_config = LatestAppConfig.model_construct(
            **{k: v for k, v in config_dict.items() if k in LatestAppConfig.model_fields}
        )

        return app_config
