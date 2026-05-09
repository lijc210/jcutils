"""
@Time   : 2018/8/22
@author : lijc210@163.com
@Desc:  : 功能描述 - 函数执行时间装饰器
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

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


def run_time_log(
    thr_time: float = 0.5, logger: Optional[logging.Logger] = None, message: str = ""
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    记录函数执行时间到日志
    多线程安全，多进程不安全
    :param thr_time: 时间阈值（秒），超过此时间才会记录
    :param logger: 日志记录器对象
    :param message: 附加消息
    :return: 装饰器函数
    """

    def decorator_function(function: Callable[..., T]) -> Callable[..., T]:
        @wraps(function)
        def wrapped_function(*args: Any, **kwargs: Any) -> T:
            t0: float = time.time()
            result: T = function(*args, **kwargs)
            t1: float = time.time()
            cost_time: float = t1 - t0
            if cost_time > thr_time:  # 大于多少秒的，则记录下来
                # print args,kwargs
                if logger:
                    logger.warning("{}\t{}\t{}".format(function.__name__, cost_time, message))
            return result

        return wrapped_function

    return decorator_function


if __name__ == "__main__":

    @run_time
    def aaa() -> None:
        print("aaaa")

    aaa()
