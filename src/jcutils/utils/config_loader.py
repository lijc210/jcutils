# coding: utf-8
"""
nacos-sdk-python
pyapollo-zenkilan
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import dotenv_values, load_dotenv

from .platform_ import is_mac, is_windows

if TYPE_CHECKING:
    from schema import AppConfig  # 只有 IDE/类型检查时才执行，运行时跳过


# 先加载 .env（不覆盖已有环境变量）
load_dotenv(override=False)


class ConfigLoader:
    """配置加载器"""

    _config_dict = {}
    SCHEMA_PATH = os.path.join(os.getcwd(), "schema.py")
    CACHE_TTL = 300  # 秒，5分钟

    @staticmethod
    def _get_cache_file(source: str) -> Path:
        """按配置源返回对应的缓存文件路径"""
        return Path(tempfile.gettempdir()) / f"jcutils_config_cache_{source}.json"

    @classmethod
    def _save_cache(cls, config: dict, cache_file: Path) -> None:
        """将配置写入系统临时目录缓存"""
        try:
            cache_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
            print(f"[config] 缓存已写入: {cache_file}")
        except Exception as e:
            print(f"[config] 缓存写入失败（忽略）: {e}")

    @classmethod
    def _load_cache(cls, cache_file: Path) -> dict | None:
        """读取本地缓存，过期或不存在返回 None"""
        try:
            if cache_file.exists():
                age = time.time() - cache_file.stat().st_mtime
                if age < cls.CACHE_TTL:
                    print(f"[config] 使用本地缓存（{int(age)}s 前，TTL={cls.CACHE_TTL}s）: {cache_file}")
                    return json.loads(cache_file.read_text(encoding="utf-8"))
                print(f"[config] 缓存已过期（{int(age)}s > {cls.CACHE_TTL}s），重新拉取")
        except Exception as e:
            print(f"[config] 读取缓存失败（忽略）: {e}")
        return None

    @classmethod
    def _load_remote_with_fallback(cls, loader_func, source: str) -> dict:
        """
        优先读本地缓存（TTL 内），
        缓存过期则拉取远程并更新缓存，
        远程失败则降级使用过期缓存，
        无缓存才真正抛异常。
        """
        cache_file = cls._get_cache_file(source)  # 统一在这里获取一次

        # 1. 缓存有效，直接返回
        cached = cls._load_cache(cache_file)
        if cached is not None:
            return cached

        # 2. 尝试拉取远程
        try:
            config = loader_func()
            cls._save_cache(config, cache_file)
            return config
        except Exception as e:
            print(f"[config] 远程拉取失败: {e}")

        # 3. 降级：使用过期缓存
        try:
            if cache_file.exists():
                print(f"[config] 降级使用过期缓存: {cache_file}")
                return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception as e2:
            print(f"[config] 读取过期缓存也失败: {e2}")

        # 4. 无任何缓存，真正报错
        raise RuntimeError("远程配置拉取失败，且无本地缓存可用，请检查配置中心连接")

    @staticmethod
    def _merge_with_env(source_config: dict) -> dict:
        """只用环境变量覆盖配置源中已有的 key，避免系统环境变量污染业务配置"""
        return {k: os.environ.get(k, v) for k, v in source_config.items()}

    @classmethod
    def _load_from_nacos(cls) -> dict:
        """从 Nacos 拉取配置，合并环境变量（环境变量优先级更高）"""
        from ..utils.nacos_client import NacosClient

        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", "dev").lower()
        if not APP_ID:
            raise ValueError("APP_ID 未设置")
        if not ENV:
            raise ValueError("ENV 未设置")

        NACOS_SERVER = os.getenv("NACOS_SERVER", default="")
        NACOS_NAMESPACE = os.getenv("NACOS_NAMESPACE", "").lower() or ENV
        NACOS_GROUP = os.getenv("NACOS_GROUP", default="")
        NACOS_USERNAME = os.getenv("NACOS_USERNAME", default="")
        NACOS_PASSWORD = os.getenv("NACOS_PASSWORD", default="")

        if (
            not NACOS_SERVER
            or not NACOS_NAMESPACE
            or not NACOS_GROUP
            or not APP_ID
            or not NACOS_USERNAME
            or not NACOS_PASSWORD
        ):
            raise ValueError(
                "使用 Nacos 时必须配置 NACOS_SERVER、NACOS_NAMESPACE、NACOS_GROUP、APP_ID、NACOS_USERNAME 和 NACOS_PASSWORD"
            )

        print(f"[config] 从 Nacos 加载配置: {NACOS_SERVER}")
        print(f"[config] ENV: {ENV}，APP_ID: {APP_ID}")

        nacos_client = NacosClient(
            server=NACOS_SERVER, namespace=NACOS_NAMESPACE, username=NACOS_USERNAME, password=NACOS_PASSWORD
        )

        async def _fetch():
            async with nacos_client:
                return await nacos_client.get_dict(APP_ID, NACOS_GROUP)

        nacos_config = asyncio.run(_fetch())
        if not nacos_config:
            raise Exception(f"Nacos 配置拉取失败: DATA_ID={APP_ID}, GROUP={NACOS_GROUP}")

        nacos_config["APP_ID"] = APP_ID
        nacos_config["ENV"] = NACOS_NAMESPACE

        return cls._merge_with_env(nacos_config)

    @classmethod
    def _load_from_apollo(cls) -> dict:
        """从 Apollo 拉取所有命名空间配置，合并环境变量（环境变量优先级更高）"""
        from pyapollo.client import ApolloClient  # type: ignore

        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", "DEV").lower()
        if not APP_ID:
            raise ValueError("APP_ID 未设置")
        if not ENV:
            raise ValueError("ENV 未设置")

        APOLLO_META_SERVER_ADDRESS = os.getenv("APOLLO_META_SERVER_ADDRESS", default="")
        APOLLO_APP_SECRET = os.getenv("APOLLO_APP_SECRET", default="")
        APOLLO_CLUSTER = os.getenv("APOLLO_CLUSTER", default="default")

        APOLLO_NAMESPACES = os.getenv("APOLLO_NAMESPACES", "application").split(",")

        if not APOLLO_META_SERVER_ADDRESS:
            raise ValueError("APOLLO_META_SERVER_ADDRESS 未配置")

        print(f"[config] 从 Apollo 加载配置: {APOLLO_META_SERVER_ADDRESS}")
        print(f"[config] ENV: {ENV}，APP_ID: {APP_ID}")

        client = ApolloClient(
            meta_server_address=APOLLO_META_SERVER_ADDRESS,
            app_id=APP_ID,
            app_secret=APOLLO_APP_SECRET,
            cluster=APOLLO_CLUSTER,
            env=ENV,
            namespaces=APOLLO_NAMESPACES,
        )

        apollo_config = {}
        for ns in APOLLO_NAMESPACES:
            ns_config = client._cache.get(ns.strip(), {})
            for k, v in ns_config.items():
                apollo_config[k] = str(v) if isinstance(v, dict) else v

        if not apollo_config:
            raise Exception(f"Apollo 配置为空: APP_ID={APP_ID}, NAMESPACES={APOLLO_NAMESPACES}")

        apollo_config["APP_ID"] = APP_ID
        apollo_config["ENV"] = ENV

        return cls._merge_with_env(apollo_config)

    @classmethod
    def _load_from_consul(cls) -> dict:
        """从 Consul KV 拉取配置，合并环境变量（环境变量优先级更高）

        依赖：pip install httpx

        KV 路径约定（两种方式二选一）：
          1. 显式指定前缀：CONSUL_PREFIX=myapp/prod/
          2. 自动拼接：{APP_ID}/{ENV}/  →  例如 myapp/dev/

        KV 结构示例：
          myapp/dev/DB_HOST        → "127.0.0.1"
          myapp/dev/DB_PORT        → "5432"
          myapp/dev/feature/ENABLE → "true"   # 子目录 "/" 会被替换为 "_"，key 变为 FEATURE_ENABLE
        """
        import base64

        import httpx

        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", default="dev").lower()
        if not APP_ID:
            raise ValueError("APP_ID 未配置")
        if not ENV:
            raise ValueError("ENV 未配置")

        CONSUL_SCHEME = os.getenv("CONSUL_SCHEME", default="http")
        CONSUL_HOST = os.getenv("CONSUL_HOST", default="127.0.0.1")
        CONSUL_PORT = int(os.getenv("CONSUL_PORT", default="8500"))
        CONSUL_TOKEN = os.getenv("CONSUL_TOKEN", default="")
        CONSUL_PREFIX = os.getenv("CONSUL_PREFIX", default="")

        # 优先用 CONSUL_PREFIX，否则自动拼接 {APP_ID}/{ENV}/
        kv_prefix = CONSUL_PREFIX or f"{APP_ID}/{ENV}"

        print(f"[config] 从 Consul 加载配置: {CONSUL_HOST}:{CONSUL_PORT}")
        print(f"[config] KV prefix: {kv_prefix}")

        async def _fetch() -> dict:
            base_url = f"{CONSUL_SCHEME}://{CONSUL_HOST}:{CONSUL_PORT}"
            headers = {}
            if CONSUL_TOKEN:
                headers["X-Consul-Token"] = CONSUL_TOKEN

            async with httpx.AsyncClient(base_url=base_url) as client:
                resp = await client.get(f"/v1/kv/{kv_prefix}", params={"recurse": "true"}, headers=headers)
                if resp.status_code == 404:
                    raise Exception(f"Consul KV 路径不存在: prefix={kv_prefix}")
                resp.raise_for_status()
                data = resp.json()

            if not data:
                raise Exception(f"Consul KV 配置为空或路径不存在: prefix={kv_prefix}")

            result = {}
            for item in data:
                key = item.get("Key")
                value = base64.b64decode(item.get("Value", "")).decode("utf-8")
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

        consul_config = asyncio.run(_fetch())
        if not consul_config:
            raise Exception(f"Consul 配置拉取后为空: prefix={kv_prefix}")

        consul_config["APP_ID"] = APP_ID or kv_prefix.strip("/").split("/")[0]
        consul_config["ENV"] = ENV

        return cls._merge_with_env(consul_config)

    @classmethod
    def _load_from_etcd(cls) -> dict:
        """从 etcd 拉取配置，合并环境变量（环境变量优先级更高）

        KV 路径约定（两种方式二选一）：
        1. 显式指定前缀：ETCD_PREFIX=myapp/prod/
        2. 自动拼接：{APP_ID}/{ENV}/  →  例如 myapp/dev/

        KV 结构示例：
        myapp/dev/DB_HOST  → "127.0.0.1"
        myapp/dev/DB_PORT  → "5432"

        Value 支持两种格式：
        1. 直接值：  "127.0.0.1"
        2. 多行 env 格式：
                DB_HOST=127.0.0.1
                DB_PORT=5432
        """
        import base64

        import httpx  # type: ignore  pip install httpx

        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", default="dev").lower()

        if not APP_ID:
            raise ValueError("APP_ID 未配置")

        if not ENV:
            raise ValueError("ENV 未配置")

        ETCD_SCHEME = os.getenv("ETCD_SCHEME", default="http")
        ETCD_HOST = os.getenv("ETCD_HOST", default="127.0.0.1")
        ETCD_PORT = int(os.getenv("ETCD_PORT", default="2379"))
        ETCD_PREFIX = os.getenv("ETCD_PREFIX", default="")
        ETCD_USER = os.getenv("ETCD_USER", default="")
        ETCD_PASSWORD = os.getenv("ETCD_PASSWORD", default="")

        kv_prefix = ETCD_PREFIX or f"{APP_ID}/{ENV}"
        # if not kv_prefix.endswith("/"):
        #     kv_prefix += "/"

        print(f"[config] 从 etcd 加载配置: {ETCD_HOST}:{ETCD_PORT}")
        print(f"[config] KV prefix: {kv_prefix}")

        # etcd v3 gRPC-gateway 接口
        base_url = f"{ETCD_SCHEME}://{ETCD_HOST}:{ETCD_PORT}"

        key_b64 = base64.b64encode(kv_prefix.encode()).decode()
        # range_end: 前缀查询技巧，将最后一个字节 +1
        prefix_bytes = kv_prefix.encode()
        range_end_bytes = prefix_bytes[:-1] + bytes([prefix_bytes[-1] + 1])
        range_end_b64 = base64.b64encode(range_end_bytes).decode()

        # 先获取 token
        token = None
        if ETCD_USER and ETCD_PASSWORD:
            auth_resp = httpx.post(
                f"{base_url}/v3/auth/authenticate",
                json={"name": ETCD_USER, "password": ETCD_PASSWORD},
            )
            auth_resp.raise_for_status()
            token = auth_resp.json().get("token")

        headers = {"Authorization": token} if token else {}

        resp = httpx.post(
            f"{base_url}/v3/kv/range",
            json={"key": key_b64, "range_end": range_end_b64},
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

        kvs = data.get("kvs") or []
        if not kvs:
            raise Exception(f"etcd KV 配置为空或路径不存在: prefix={kv_prefix}")

        result = {}
        for item in kvs:
            full_key = base64.b64decode(item["key"]).decode("utf-8")
            relative_key = full_key[len(kv_prefix) :]
            value = base64.b64decode(item["value"]).decode("utf-8") if item.get("value") else ""

            lines = value.splitlines()
            if len(lines) > 1 or (len(lines) == 1 and "=" in value):
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        k, v = parts
                        result[k.strip()] = v.strip()
            else:
                config_key = relative_key.replace("/", "_").upper()
                if config_key:
                    result[config_key] = value

        if not result:
            raise Exception(f"etcd 配置解析后为空: prefix={kv_prefix}")

        result["APP_ID"] = APP_ID or kv_prefix.strip("/").split("/")[0]
        result["ENV"] = ENV

        return cls._merge_with_env(result)

    @classmethod
    def _load_from_local(cls) -> dict:
        """从 .env 读取配置，合并环境变量"""

        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", default="dev").lower()
        if not APP_ID:
            raise ValueError("APP_ID 未设置")
        if not ENV:
            raise ValueError("ENV 未设置")

        print("[config] 从 .env 加载配置")
        print(f"[config] ENV: {ENV}，APP_ID: {APP_ID}")

        local_config = dict(dotenv_values(".env"))
        local_config["APP_ID"] = APP_ID
        local_config["ENV"] = ENV
        return cls._merge_with_env(local_config)

    @staticmethod
    def _infer_type(value: str) -> str:
        if not value:  # 加上空值保护
            return "str"
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
    def _cast_value(value: str, type_hint: str):
        """将字符串值按类型提示转换为对应的 Python 类型"""
        if not isinstance(value, str):
            return value  # 非字符串（已经是正确类型）直接返回
        if type_hint == "bool":
            return value.lower() == "true"
        if type_hint == "int":
            return int(value)
        if type_hint == "float":
            return float(value)
        return value  # str，保持原样

    @staticmethod
    def _format_key(key: str) -> str:
        return key.replace("-", "_").replace(".", "_").upper()

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
            k = cls._format_key(key)
            t = cls._infer_type(str(value))
            lines.append(f"    {k}: {t}")
        return "\n".join(lines)

    @classmethod
    def _load_schema_module(cls) -> type[AppConfig]:
        """动态加载或重载 schema 模块，返回最新的 AppConfig 类"""
        if "schema" in sys.modules:
            module = importlib.reload(sys.modules["schema"])
        else:
            spec = importlib.util.spec_from_file_location("schema", cls.SCHEMA_PATH)
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules["schema"] = module
        return getattr(module, "AppConfig")

    @classmethod
    def sync_schema(cls) -> type[AppConfig]:
        """判断 schema.py 是否存在或发生变化，按需生成，返回最新的 AppConfig 类"""
        new_content = cls._build_schema_content(cls._config_dict)

        if os.path.exists(cls.SCHEMA_PATH):
            with open(cls.SCHEMA_PATH, "r", encoding="utf-8") as f:
                existing_content = f.read()
            if existing_content == new_content:
                print("[config] schema.py 无变化，跳过生成")
            else:
                print("[config] schema.py 已变化，更新生成")
                with open(cls.SCHEMA_PATH, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"[config] schema.py 更新完成，共 {len(cls._config_dict)} 个配置项")
        else:
            print("[config] schema.py 不存在，生成中")
            with open(cls.SCHEMA_PATH, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[config] schema.py 生成完成，共 {len(cls._config_dict)} 个配置项")

        return cls._load_schema_module()

    @classmethod
    def _get_dirs(cls, APP_ID: str) -> tuple[str, str]:
        if is_windows():
            drive = "D:\\" if os.path.exists("D:\\") else "C:\\"
            return os.path.join(drive, "data", APP_ID), os.path.join(drive, "logs", APP_ID)
        elif is_mac():
            home = os.path.expanduser("~")
            return os.path.join(home, "data", APP_ID), os.path.join(home, "logs", APP_ID)
        else:
            return os.path.join("/data", APP_ID), os.path.join("/logs", APP_ID)

    @classmethod
    def load_config(cls, init_dirs: bool = False) -> AppConfig:
        """
        根据 CONFIG_SOURCE 判断配置来源：
        - nacos  → 从 Nacos 拉取，再合并环境变量
        - apollo → 从 Apollo 拉取，再合并环境变量
        - local（默认）→ 从 .env 读取，再合并环境变量
        """
        CONFIG_SOURCE = os.getenv("CONFIG_SOURCE", "local").lower()

        # local 模式不需要缓存（本地 .env 读取极快）
        if CONFIG_SOURCE == "nacos":
            config_dict = cls._load_remote_with_fallback(cls._load_from_nacos, CONFIG_SOURCE)
        elif CONFIG_SOURCE == "apollo":
            config_dict = cls._load_remote_with_fallback(cls._load_from_apollo, CONFIG_SOURCE)
        elif CONFIG_SOURCE == "consul":
            config_dict = cls._load_remote_with_fallback(cls._load_from_consul, CONFIG_SOURCE)
        elif CONFIG_SOURCE == "etcd":
            config_dict = cls._load_remote_with_fallback(cls._load_from_etcd, CONFIG_SOURCE)
        else:
            config_dict = cls._load_from_local()

        cls._config_dict = config_dict

        if init_dirs:
            # 按需创建目录
            APP_ID = config_dict.get("APP_ID", "")
            data_dir, logs_dir = cls._get_dirs(APP_ID)
            for d in [data_dir, logs_dir]:
                os.makedirs(d, exist_ok=True)
            # 注入到 config_dict，schema 会自动生成这两个字段
            config_dict["DATA_DIR"] = data_dir
            config_dict["LOGS_DIR"] = logs_dir

        # 生成/更新 schema.py，并拿到当次运行最新的 AppConfig 类
        LatestAppConfig = cls.sync_schema()

        # 按 schema 字段定义的类型，将字符串值转换为正确的 Python 类型
        typed_config = {}
        for k, v in config_dict.items():
            if k not in LatestAppConfig.model_fields:  # 忽略 schema 中未定义的字段
                continue
            type_hint = cls._infer_type(str(v))
            typed_config[k] = cls._cast_value(str(v), type_hint)

        app_config = LatestAppConfig.model_construct(**typed_config)

        return app_config
