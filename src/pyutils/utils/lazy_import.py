"""
@File    :   lazy_import.py
@Time    :   2021/03/12 14:43:29
@Author  :   lijc210@163.com
@Desc    :  官网的例子
"""

import importlib.util
import sys


def lazy_import(name):
    spec = importlib.util.find_spec(name)
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


if __name__ == "__main__":
    os = lazy_import("os")
    print(os)
