"""
@author: lijc210@163.com
@file: built_in_tools.py
@time: 2019/09/25
@desc: Python内置工具函数封装 - pickle序列化工具
"""

import pickle
from typing import Any


def pickleFile(file: str, item: Any) -> None:
    """
    将对象序列化并保存到文件中

    :param file: 文件路径
    :param item: 要序列化的对象
    :return: None
    """
    with open(file, "wb") as dbFile:
        pickle.dump(item, dbFile)


def unpickeFile(file: str) -> Any:
    """
    从文件中反序列化对象

    :param file: 文件路径
    :return: 反序列化后的对象
    """
    with open(file, "rb") as dbFile:
        return pickle.load(dbFile)
