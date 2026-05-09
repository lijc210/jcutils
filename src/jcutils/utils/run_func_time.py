"""
@Time   : 2018/8/22
@author : lijc210@163.com
@Desc:  : 功能描述 - 函数执行时间装饰器
"""

import time
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def run_time(function: Callable[..., T]) -> Callable[..., T]:
    """
    打印函数执行时间装饰器
    :param function: 要装饰的函数
    :return: 包装后的函数
    """

    @wraps(function)
    def wrapped_function(*args: Any, **kwargs: Any) -> T:
        t0: float = time.time()
        result: T = function(*args, **kwargs)
        t1: float = time.time()
        print("{}: {} seconds".format(function.__name__, str(t1 - t0)))
        return result

    return wrapped_function


if __name__ == "__main__":

    @run_time
    def aaa() -> None:
        print("aaaa")

    aaa()
