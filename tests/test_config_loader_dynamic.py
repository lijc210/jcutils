"""ConfigLoader 动态读取（get_value / get_json_value）测试

用桩替换 ``_fetch_source_config``，不依赖 .env、配置中心，也不会写 schema.py。
"""

import pytest

from jcutils.utils import config_loader
from jcutils.utils.config_loader import ConfigLoader

SOURCE = {
    "APP_ID": "demo",
    "ENV": "dev",
    "MAX_RETRY": "3",
    "RATE": "0.5",
    "FLAG": "true",
    "EXTRA": '{"a": 1}',
}


@pytest.fixture
def config(monkeypatch):
    """把类状态和回源逻辑都替换掉，DYNAMIC_TTL=0 让每次读取都回源"""
    source = dict(SOURCE)
    monkeypatch.setattr(ConfigLoader, "_fetch_source_config", classmethod(lambda cls: dict(source)))
    monkeypatch.setattr(ConfigLoader, "_config_dict", {})
    monkeypatch.setattr(ConfigLoader, "_dynamic_index", {})
    monkeypatch.setattr(ConfigLoader, "_injected_keys", set())
    monkeypatch.setattr(ConfigLoader, "_snapshot_at", 0.0)
    monkeypatch.setattr(ConfigLoader, "DYNAMIC_TTL", 0)
    return source


def test_get_value_casts_like_startup(config):
    assert ConfigLoader.get_value("MAX_RETRY") == 3
    assert ConfigLoader.get_value("RATE") == 0.5
    assert ConfigLoader.get_value("FLAG") is True
    # key 兼容小写 / 点 / 中划线写法
    assert ConfigLoader.get_value("app_id") == "demo"
    assert ConfigLoader.get_value("max-retry") == 3


def test_get_value_missing_key(config):
    with pytest.raises(KeyError):
        ConfigLoader.get_value("NOT_EXIST")
    assert ConfigLoader.get_value("NOT_EXIST", None) is None
    assert ConfigLoader.get_value("NOT_EXIST", "fallback") == "fallback"


def test_get_json_value(config):
    assert ConfigLoader.get_json_value("EXTRA") == {"a": 1}
    assert ConfigLoader.get_json_value("NOT_EXIST", {}) == {}
    with pytest.raises(KeyError):
        ConfigLoader.get_json_value("NOT_EXIST")


def test_get_json_value_invalid(config):
    with pytest.raises(ValueError):
        ConfigLoader.get_json_value("APP_ID")  # "demo" 不是合法 JSON
    assert ConfigLoader.get_json_value("APP_ID", {}) == {}


def test_refresh_picks_up_changes(config):
    assert ConfigLoader.get_value("MAX_RETRY") == 3
    config["MAX_RETRY"] = "5"
    assert ConfigLoader.get_value("MAX_RETRY") == 5


def test_value_cached_within_ttl(config, monkeypatch):
    calls = []

    def fake_fetch(cls):
        calls.append(1)
        return dict(config)

    monkeypatch.setattr(ConfigLoader, "_fetch_source_config", classmethod(fake_fetch))
    monkeypatch.setattr(ConfigLoader, "DYNAMIC_TTL", 300)

    assert ConfigLoader.get_value("MAX_RETRY") == 3
    assert ConfigLoader.get_value("MAX_RETRY") == 3
    assert len(calls) == 1  # TTL 内只回源一次


def test_refresh_failure_keeps_old_snapshot(config, monkeypatch):
    assert ConfigLoader.get_value("MAX_RETRY") == 3

    def boom(cls):
        raise RuntimeError("config center down")

    monkeypatch.setattr(ConfigLoader, "_fetch_source_config", classmethod(boom))
    # 回源失败时沿用旧快照，不把调用方打挂
    assert ConfigLoader.get_value("MAX_RETRY") == 3


def test_refresh_keeps_injected_keys(config, monkeypatch):
    monkeypatch.setattr(ConfigLoader, "_injected_keys", {"DATA_DIR"})
    monkeypatch.setattr(ConfigLoader, "_config_dict", {"DATA_DIR": "/tmp/data"})
    assert ConfigLoader.get_value("DATA_DIR") == "/tmp/data"


def test_merge_with_env_ignores_dotenv_copy(monkeypatch):
    # load_dotenv 在启动时会把 .env 的值写进 os.environ，这些副本不应压过 .env 的新内容
    monkeypatch.setattr(config_loader, "_DOTENV_INJECTED", {"MAX_RETRY": "3"})
    monkeypatch.setenv("MAX_RETRY", "3")
    assert ConfigLoader._merge_with_env({"MAX_RETRY": "5"})["MAX_RETRY"] == "5"

    # 真实的进程环境变量仍然优先
    monkeypatch.setenv("MAX_RETRY", "9")
    assert ConfigLoader._merge_with_env({"MAX_RETRY": "5"})["MAX_RETRY"] == "9"
