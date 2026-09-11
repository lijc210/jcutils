"""
@Time   : 2018/8/22
@author : lijc210@163.com
@Desc:  : 功能描述 - 行级性能分析装饰器
"""

import time
from functools import wraps
from typing import Any, Callable, TypeVar

from line_profiler import LineProfiler

T = TypeVar("T")


# 查询接口中每行代码执行的时间
def run_line_time(f: Callable[..., T]) -> Callable[..., T]:
    """
    行级性能分析装饰器，使用 line_profiler 分析函数每行代码的执行时间

    :param f: 要分析的函数
    :return: 包装后的函数
    """

    @wraps(f)
    def decorator(*args: Any, **kwargs: Any) -> T:
        func_return: T = f(*args, **kwargs)
        lp: LineProfiler = LineProfiler()
        lp_wrap: Callable[..., T] = lp(f)
        lp_wrap(*args, **kwargs)
        lp.print_stats()
        return func_return

    return decorator


if __name__ == "__main__":

    @run_line_time
    def aaa() -> None:
        print("aaaa")
        time.sleep(1)
        time.sleep(2)
        for _i in range(3):
            time.sleep(1)

    aaa()
