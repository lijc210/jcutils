# coding: utf-8
"""
nacos-sdk-python
pyapollo-zenkilan
"""

from __future__ import annotations

import asyncio
import base64
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

from ..client import AsyncEtcdClient, NacosClient

try:
    import httpx
except ModuleNotFoundError:
    httpx = None  # 可选依赖，使用时检查

try:
    from pyapollo.client import ApolloClient  # type: ignore
except ModuleNotFoundError:
    ApolloClient = None  # 可选依赖，使用时检查

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
    def _get_cache_file(source: str, app_id: str) -> Path:
        """按配置源返回对应的缓存文件路径"""
        return Path(tempfile.gettempdir()) / f"{app_id}_config_cache_{source}.json"

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
    def _load_remote_with_fallback(cls, loader_func, source: str, app_id: str) -> dict:
        """
        优先读本地缓存（TTL 内），
        缓存过期则拉取远程并更新缓存，
        远程失败则降级使用过期缓存，
        无缓存才真正抛异常。
        """

        cache_file = cls._get_cache_file(source, app_id)  # 统一在这里获取一次

        # 1. 缓存有效，直接返回
        cached = cls._load_cache(cache_file)
        if cached is not None:
            ENV = os.getenv("ENV", default="dev").lower()
            print(f"[config] ENV: {ENV}，APP_ID: {app_id}")
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
        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", "dev").lower()

        NACOS_SERVER = os.getenv("NACOS_SERVER", default="")
        NACOS_NAMESPACE = os.getenv("NACOS_NAMESPACE", "").lower() or ENV
        NACOS_GROUP = os.getenv("NACOS_GROUP", default="")
        NACOS_USERNAME = os.getenv("NACOS_USERNAME", default="")
        NACOS_PASSWORD = os.getenv("NACOS_PASSWORD", default="")

        print(f"[config] 从 Nacos 加载配置: {NACOS_SERVER}")
        print(f"[config] ENV: {ENV}，APP_ID: {APP_ID}")

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
        if ApolloClient is None:
            raise ImportError('请先安装：pip install jcutils[all] or uv add "jcutils[all]"')

        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", "DEV").lower()

        APOLLO_META_SERVER_ADDRESS = os.getenv("APOLLO_META_SERVER_ADDRESS", default="")
        APOLLO_APP_SECRET = os.getenv("APOLLO_APP_SECRET", default="")
        APOLLO_CLUSTER = os.getenv("APOLLO_CLUSTER", default="default")

        APOLLO_NAMESPACES = os.getenv("APOLLO_NAMESPACES", "application").split(",")

        print(f"[config] 从 Apollo 加载配置: {APOLLO_META_SERVER_ADDRESS}")
        print(f"[config] ENV: {ENV}，APP_ID: {APP_ID}")

        if not APOLLO_META_SERVER_ADDRESS:
            raise ValueError("APOLLO_META_SERVER_ADDRESS 未配置")

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
        if httpx is None:
            raise ImportError('请先安装：pip install jcutils[all] or uv add "jcutils[all]"')

        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", default="dev").lower()

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
        APP_ID = os.getenv("APP_ID", default="")
        ENV = os.getenv("ENV", default="dev").lower()

        ETCD_HOST = os.getenv("ETCD_HOST", default="127.0.0.1")
        ETCD_PORT = int(os.getenv("ETCD_PORT", default="2379"))
        ETCD_PREFIX = os.getenv("ETCD_PREFIX", default="")
        ETCD_USER = os.getenv("ETCD_USER", default="")
        ETCD_PASSWORD = os.getenv("ETCD_PASSWORD", default="")

        kv_prefix = ETCD_PREFIX or f"{APP_ID}/{ENV}"

        print(f"[config] 从 etcd 加载配置: {ETCD_HOST}:{ETCD_PORT}")
        print(f"[config] KV prefix: {kv_prefix}")

        async def _fetch():
            client = AsyncEtcdClient(
                host=ETCD_HOST,
                port=ETCD_PORT,
                username=ETCD_USER or None,
                password=ETCD_PASSWORD or None,
            )
            async with client:
                items = await client.get_prefix(kv_prefix)
                if not items:
                    raise Exception(f"etcd KV 配置为空或路径不存在: prefix={kv_prefix}")
                return items

        try:
            kvs = asyncio.run(_fetch())
        except Exception as e:
            err_msg = str(e)
            if "user name is empty" in err_msg or "authentication failed" in err_msg:
                raise Exception(
                    f"etcd 认证失败，请配置 ETCD_USER 和 ETCD_PASSWORD 环境变量。原始错误: {err_msg}"
                ) from e
            raise

        result = {}
        for full_key, value in kvs:
            relative_key = full_key[len(kv_prefix) :]

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
        """
        获取应用数据和日志目录
        优先使用环境变量，生产环境用 /data，开发环境自动适配

        Returns:
            tuple[str, str]: (data_dir, log_dir)
        """
        # 1. 环境变量优先（最高优先级）
        data_dir_env = os.environ.get(f"{APP_ID.upper()}_DATA_DIR")
        log_dir_env = os.environ.get(f"{APP_ID.upper()}_LOG_DIR")

        if data_dir_env and log_dir_env:
            os.makedirs(data_dir_env, exist_ok=True)
            os.makedirs(log_dir_env, exist_ok=True)
            return data_dir_env, log_dir_env

        # 2. 检查是否在 Docker 容器中
        in_docker = os.path.exists("/.dockerenv")

        # 3. 根据环境选择基础路径
        if in_docker or sys.platform.startswith("linux"):
            # 生产环境或 Linux 服务器
            # 数据：/data/{APP_ID}/data
            # 日志：/data/logs/{APP_ID}
            data_dir = f"/data/{APP_ID}/data"
            log_dir = f"/data/logs/{APP_ID}"

        elif sys.platform == "darwin":
            # Mac 开发：使用 ~/data
            base = os.path.join(os.path.expanduser("~"), "data", APP_ID)
            data_dir = os.path.join(base, "data")
            log_dir = os.path.join(os.path.expanduser("~"), "data", "logs", APP_ID)

        elif sys.platform == "win32":
            # Windows 开发：使用 D:\data 或 C:\data
            drive = "D:\\" if os.path.exists("D:\\") else "C:\\"
            data_dir = os.path.join(drive, APP_ID, "data")
            log_dir = os.path.join(drive, "logs", APP_ID)
        else:
            # 其他：fallback
            data_dir = os.path.join("/var", "lib", APP_ID, "data")
            log_dir = os.path.join("/var", "log", APP_ID)

        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        return data_dir, log_dir

    @classmethod
    def load_config(cls, init_dirs: bool = False) -> AppConfig:
        """
        根据 CONFIG_SOURCE 判断配置来源：
        - nacos  → 从 Nacos 拉取，再合并环境变量
        - apollo → 从 Apollo 拉取，再合并环境变量
        - local（默认）→ 从 .env 读取，再合并环境变量
        """
        CONFIG_SOURCE = os.getenv("CONFIG_SOURCE", "local").lower()
        ENV = os.getenv("ENV", "dev").lower()
        APP_ID = os.getenv("APP_ID", "")
        if not ENV:
            raise ValueError("ENV 未配置")
        if not APP_ID:
            raise ValueError("APP_ID 未设置")

        # local 模式不需要缓存（本地 .env 读取极快）
        if CONFIG_SOURCE == "nacos":
            config_dict = cls._load_remote_with_fallback(cls._load_from_nacos, CONFIG_SOURCE, APP_ID)
        elif CONFIG_SOURCE == "apollo":
            config_dict = cls._load_remote_with_fallback(cls._load_from_apollo, CONFIG_SOURCE, APP_ID)
        elif CONFIG_SOURCE == "consul":
            config_dict = cls._load_remote_with_fallback(cls._load_from_consul, CONFIG_SOURCE, APP_ID)
        elif CONFIG_SOURCE == "etcd":
            config_dict = cls._load_remote_with_fallback(cls._load_from_etcd, CONFIG_SOURCE, APP_ID)
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
