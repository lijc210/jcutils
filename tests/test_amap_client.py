"""AmapClient 测试：使用假 Session，不发起真实网络请求"""

import pytest

from jcutils.client.amap import AmapClient, AmapError

OK = {"status": "1", "info": "OK", "infocode": "10000"}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []
        self.closed = False

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return self.response

    def close(self):
        self.closed = True


def build_client(monkeypatch, payload, status_code=200, key="test-key", **kwargs):
    monkeypatch.setenv("AMAP_KEY", key)
    session = FakeSession(FakeResponse(payload, status_code=status_code))
    return AmapClient(session=session, **kwargs), session


def test_key_required(monkeypatch):
    monkeypatch.delenv("AMAP_KEY", raising=False)
    with pytest.raises(ValueError, match="AMAP_KEY"):
        AmapClient()


def test_key_from_env_and_explicit(monkeypatch):
    monkeypatch.setenv("AMAP_KEY", "env-key")
    session = FakeSession(FakeResponse(OK))
    assert AmapClient(session=session).key == "env-key"
    assert AmapClient(key="explicit", session=session).key == "explicit"


def test_regeo_sends_expected_params(monkeypatch):
    payload = {**OK, "regeocode": {"formatted_address": "北京市东城区"}}
    client, session = build_client(monkeypatch, payload)

    result = client.regeo("116.310003,39.991957", city="北京市", radius=1000, extensions="all")

    assert result["regeocode"]["formatted_address"] == "北京市东城区"
    call = session.calls[0]
    assert call["url"] == "https://restapi.amap.com/v3/geocode/regeo"
    assert call["params"] == {
        "key": "test-key",
        "output": "JSON",
        "location": "116.310003,39.991957",
        "batch": "true",
        "extensions": "all",
        "city": "北京市",
        "radius": 1000,
    }
    assert call["timeout"] == 10.0


def test_regeo_address_handles_empty_array(monkeypatch):
    client, _ = build_client(monkeypatch, {**OK, "regeocode": {"formatted_address": []}})
    assert client.regeo_address("1,2") is None

    client, _ = build_client(monkeypatch, {**OK, "regeocode": {"formatted_address": "浙江省杭州市西湖区"}})
    assert client.regeo_address("1,2") == "浙江省杭州市西湖区"


def test_status_error_raises_amap_error(monkeypatch):
    payload = {"status": "0", "info": "INVALID_USER_KEY", "infocode": "10001"}
    client, _ = build_client(monkeypatch, payload)

    with pytest.raises(AmapError) as exc_info:
        client.regeo("1,2")

    assert exc_info.value.infocode == "10001"
    assert "INVALID_USER_KEY" in str(exc_info.value)
    assert exc_info.value.payload == payload


def test_http_error_raises_amap_error(monkeypatch):
    client, _ = build_client(monkeypatch, {"oops": True}, status_code=500)
    with pytest.raises(AmapError, match="HTTP 500"):
        client.geocode("天安门")


def test_geocode_location(monkeypatch):
    client, _ = build_client(monkeypatch, {**OK, "geocodes": [{"location": "116.397477,39.909187"}]})
    assert client.geocode_location("天安门") == "116.397477,39.909187"

    client, _ = build_client(monkeypatch, {**OK, "geocodes": []})
    assert client.geocode_location("不存在的地方") is None


def test_batch_limit(monkeypatch):
    client, _ = build_client(monkeypatch, OK)
    with pytest.raises(ValueError, match="20"):
        client.regeo("|".join(["1,2"] * 21))


def test_parse_coordinates():
    assert AmapClient.parse_coordinates("116.31,39.99") == (("116.31", "39.99"),)
    assert AmapClient.parse_coordinates("1,2|3,4") == (("1", "2"), ("3", "4"))
    assert AmapClient.parse_coordinates("bad") == ()
    assert AmapClient.parse_coordinates("") == ()


def test_context_manager_closes_session(monkeypatch):
    monkeypatch.setenv("AMAP_KEY", "test-key")
    session = FakeSession(FakeResponse(OK))
    with AmapClient(session=session):
        pass
    assert session.closed is True
