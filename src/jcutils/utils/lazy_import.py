"""
@File    :   lazy_import.py
@Time    :   2021/03/12 14:43:29
@Author  :   lijc210@163.com
@Desc    :   懒加载模块导入工具
             参考 Python 官方示例，实现模块的延迟导入
"""

import importlib.util
import sys
import types
from typing import Any


def lazy_import(name: str) -> types.ModuleType:
    """
    懒加载模块导入函数，延迟加载模块直到真正使用时才导入

    这种方式可以减少应用程序启动时间，特别是在有大量可选依赖时非常有用。
    只有在第一次访问模块属性时才会真正加载模块。

    :param name: 要导入的模块名称，如 "os", "numpy", "pandas" 等
    :return: 模块对象
    :raises ImportError: 如果找不到指定的模块
    :raises ModuleNotFoundError: 如果模块不存在
    """
    spec: Any = importlib.util.find_spec(name)
    if spec is None:
        raise ImportError(f"Module '{name}' not found")

    loader: Any = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module: types.ModuleType = importlib.util.module_from_spec(spec)

    # 将模块注册到 sys.modules 中，避免重复导入
    sys.modules[name] = module
    loader.exec_module(module)

    return module


if __name__ == "__main__":
    # 测试懒加载
    os_module: types.ModuleType = lazy_import("os")
    print(f"Module: {os_module}")
    print(f"Module name: {os_module.__name__}")

    # 测试获取模块属性（此时才会真正加载模块）
    print(f"Current directory: {os_module.getcwd()}")

    # 测试导入不存在的模块
    try:
        lazy_import("nonexistent_module_xyz")
    except ImportError as e:
        print(f"Expected error: {e}")
