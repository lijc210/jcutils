"""
@File    :   date_encoder.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :   自定义JSON编码器，处理datetime对象的序列化
"""

import datetime
import json
from typing import Any


class DateEncoder(json.JSONEncoder):
    """
    自定义JSON编码器，用于处理datetime对象的序列化

    将datetime对象转换为字符串格式，便于JSON序列化
    支持datetime.datetime、datetime.date、datetime.time等类型
    """

    def default(self, obj: Any) -> Any:
        """
        重写JSONEncoder的default方法，处理特殊类型的序列化

        :param obj: 要序列化的对象
        :return: JSON可序列化的对象
        :raises TypeError: 如果对象类型无法被序列化
        """
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.time):
            return obj.strftime("%H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    # 测试DateEncoder
    data = {
        "name": "张三",
        "birthday": datetime.datetime(1990, 5, 15, 14, 30, 0),
        "today": datetime.date.today(),
        "now": datetime.datetime.now(),
    }

    # 使用DateEncoder序列化
    json_str = json.dumps(data, cls=DateEncoder, ensure_ascii=False)
    print(json_str)
