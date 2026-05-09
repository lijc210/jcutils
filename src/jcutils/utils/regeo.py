"""
@File    :   regeo.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :   高德地图逆地理编码工具
             根据坐标（经纬度）获取详细的地址信息
"""

from typing import Any, Dict, Optional, Tuple

import requests

georegeo_url = "https://restapi.amap.com/v3/geocode/regeo"

key = "ec67ff42f93e2088681011e54edf688d"


def api_geocode(location: str, city: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    根据坐标获取地址信息（逆地理编码）

    :param location: 坐标点，支持单个坐标或批量坐标
                    单个坐标格式："经度,纬度"，如 "116.310003,39.991957"
                    批量坐标格式："经度1,纬度1|经度2,纬度2|..."
                    如 "116.310003,39.991957|117.310003,39.991957"
    :param city: 可选，指定查询的城市，如 "北京市"
    :return: 高德地图 API 返回的 JSON 数据（字典格式），如果请求失败则返回 None
             返回数据结构示例：
             {
                 "status": "1",
                 "info": "OK",
                 "infocode": "10000",
                 "regeocode": {
                     "formatted_address": "北京市东城区...",
                     "addressComponent": {...},
                     ...
                 }
             }
    """
    try:
        resp = requests.get(
            georegeo_url,
            params={"key": key, "location": location, "city": city, "batch": "true"},
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def api_geocode_and_print(location: str, city: Optional[str] = None) -> None:
    """
    根据坐标获取地址信息并打印到控制台

    :param location: 坐标点，格式："经度,纬度" 或批量坐标
    :param city: 可选，指定查询的城市
    :return: None
    """
    result = api_geocode(location, city)
    if result:
        print(result)
    else:
        print("请求失败")


def parse_coordinates(location_str: str) -> Tuple[str, ...]:
    """
    解析坐标字符串，返回经纬度元组列表

    :param location_str: 坐标字符串，支持单个或批量格式
                         单个格式："116.310003,39.991957"
                         批量格式："116.310003,39.991957|117.310003,39.991957"
    :return: 经纬度元组的元组，如 (("116.310003", "39.991957"), ("117.310003", "39.991957"))
    """
    if "|" in location_str:
        # 批量坐标
        coords = location_str.split("|")
        return tuple(tuple(coord.split(",")) for coord in coords if "," in coord)
    else:
        # 单个坐标
        if "," in location_str:
            return (tuple(location_str.split(",")),)
        return ()


if __name__ == "__main__":
    # 测试单个坐标
    print("=== 测试单个坐标 ===")
    api_geocode_and_print("116.310003,39.991957")

    # 测试批量坐标
    print("\n=== 测试批量坐标 ===")
    api_geocode_and_print("116.310003,39.991957|117.310003,39.991957")

    # 测试指定城市
    print("\n=== 测试指定城市 ===")
    api_geocode_and_print("116.310003,39.991957", city="北京市")

    # 测试坐标解析
    print("\n=== 测试坐标解析 ===")
    coords = parse_coordinates("116.310003,39.991957|117.310003,39.991957")
    print(f"解析结果: {coords}")

    # 常见测试坐标
    test_locations = {
        "天安门": "116.397477,39.909187",
        "东方明珠": "121.499719,31.239704",
        "广州塔": "113.319129,23.109632",
        "深圳市民中心": "114.05685,22.54309",
    }

    print("\n=== 常见地标测试 ===")
    for name, coord in test_locations.items():
        result = api_geocode(coord)
        if result and result.get("status") == "1":
            address = result.get("regeocode", {}).get("formatted_address", "未知")
            print(f"{name} ({coord}): {address}")
        else:
            print(f"{name} ({coord}): 查询失败")
