"""
@Desc: 高德地图 Web 服务客户端（逆地理编码 / 地理编码）

Key 不写在代码里，通过环境变量 AMAP_KEY 提供：

    export AMAP_KEY=你的高德 Web 服务 Key

文档：
- 逆地理编码: https://lbs.amap.com/api/webservice/guide/api/georegeo
- 地理编码:   https://lbs.amap.com/api/webservice/guide/api/geocodes
"""

from __future__ import annotations

import os
from typing import Any

import requests

AMAP_BASE_URL = "https://restapi.amap.com/v3"
# 批量逆地理编码单次最多 20 个坐标点（高德接口限制）
MAX_BATCH_SIZE = 20


class AmapError(RuntimeError):
    """高德 Web 服务调用失败"""

    def __init__(self, message: str, *, infocode: str | None = None, payload: dict | None = None) -> None:
        super().__init__(message)
        self.infocode = infocode
        self.payload = payload


class AmapClient:
    """高德地图 Web 服务客户端

    只依赖 requests。Key 优先取构造参数，其次取环境变量 AMAP_KEY。

    使用示例::

        from jcutils.client.amap import AmapClient

        with AmapClient() as client:
            result = client.regeo("116.310003,39.991957")
            print(result["regeocode"]["formatted_address"])
    """

    def __init__(self, key: str | None = None, timeout: float = 10.0, session: requests.Session | None = None) -> None:
        """
        :param key: 高德 Web 服务 Key，缺省读环境变量 AMAP_KEY
        :param timeout: 单次请求超时时间（秒）
        :param session: 可复用的 requests.Session，便于自定义代理/连接池
        """
        self.key = key or os.getenv("AMAP_KEY", "")
        if not self.key:
            raise ValueError("高德 Key 未配置：请设置环境变量 AMAP_KEY，或通过 AmapClient(key=...) 传入")
        self.timeout = timeout
        self._session = session or requests.Session()

    def close(self) -> None:
        """释放连接资源"""
        self._session.close()

    def __enter__(self) -> AmapClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """调用高德接口，返回解析后的 JSON；失败统一抛 AmapError"""
        query = {"key": self.key, "output": "JSON", **params}
        try:
            resp = self._session.get(f"{AMAP_BASE_URL}{path}", params=query, timeout=self.timeout)
        except requests.RequestException as e:
            raise AmapError(f"高德接口请求异常: {e}") from e

        if resp.status_code != 200:
            raise AmapError(f"高德接口 HTTP {resp.status_code}: {resp.text[:200]}")

        try:
            data = resp.json()
        except ValueError as e:
            raise AmapError(f"高德接口返回内容不是合法 JSON: {resp.text[:200]}") from e

        if str(data.get("status")) != "1":
            infocode = data.get("infocode")
            raise AmapError(
                f"高德接口返回错误: {data.get('info') or 'unknown'} (infocode={infocode})",
                infocode=infocode,
                payload=data,
            )
        return data

    def regeo(
        self,
        location: str,
        city: str | None = None,
        batch: bool = True,
        radius: int | None = None,
        extensions: str = "base",
    ) -> dict[str, Any]:
        """
        逆地理编码：坐标 → 地址，返回高德原始响应

        :param location: 坐标，"经度,纬度"；批量时用 "|" 分隔
        :param city: 可选，指定查询城市，如 "北京市"
        :param batch: 是否批量查询；单点查询建议传 False，响应结构更简单
        :param radius: 可选，搜索半径（米），范围 0~3000
        :param extensions: "base" 或 "all"，all 会返回周边 POI/AOI 等扩展信息
        """
        if batch and len(self.parse_coordinates(location)) > MAX_BATCH_SIZE:
            raise ValueError(f"批量逆地理编码单次最多 {MAX_BATCH_SIZE} 个坐标")

        params: dict[str, Any] = {
            "location": location,
            "batch": "true" if batch else "false",
            "extensions": extensions,
        }
        if city:
            params["city"] = city
        if radius is not None:
            params["radius"] = radius
        return self._request("/geocode/regeo", params)

    def regeo_address(self, location: str, city: str | None = None) -> str | None:
        """逆地理编码，只返回格式化地址；查询无结果时返回 None

        高德在无结果时 formatted_address 可能返回空数组 []，这里统一转成 None。
        """
        data = self.regeo(location, city=city, batch=False)
        regeocode = data.get("regeocode") or {}
        address = regeocode.get("formatted_address")
        return address if isinstance(address, str) and address else None

    def geocode(self, address: str, city: str | None = None, batch: bool = False) -> dict[str, Any]:
        """
        地理编码：地址 → 坐标，返回高德原始响应

        :param address: 结构化地址，如 "北京市朝阳区阜通东大街6号"
        :param city: 可选，指定查询城市
        :param batch: 是否批量查询
        """
        params: dict[str, Any] = {"address": address, "batch": "true" if batch else "false"}
        if city:
            params["city"] = city
        return self._request("/geocode/geo", params)

    def geocode_location(self, address: str, city: str | None = None) -> str | None:
        """地理编码，只返回第一个匹配的 "经度,纬度"；查询无结果时返回 None"""
        data = self.geocode(address, city=city, batch=False)
        geocodes = data.get("geocodes") or []
        if not geocodes:
            return None
        location = geocodes[0].get("location")
        return location if isinstance(location, str) and location else None

    @staticmethod
    def parse_coordinates(location_str: str) -> tuple[tuple[str, ...], ...]:
        """解析坐标字符串

        单个："116.310003,39.991957"
        批量："116.310003,39.991957|117.310003,39.991957"
        """
        if not location_str:
            return ()
        if "|" in location_str:
            return tuple(tuple(coord.split(",")) for coord in location_str.split("|") if "," in coord)
        if "," in location_str:
            return (tuple(location_str.split(",")),)
        return ()
