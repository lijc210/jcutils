"""
@Time   : 2018/8/22
@author : lijc210@163.com
@Desc:  : 功能描述 - 函数执行时间日志记录工具
"""

import json
import logging
import time
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from func_timeout import FunctionTimedOut, func_timeout

T = TypeVar("T")


def run_time_log(
    thr_time: float = 0.5,
    logger: Optional[logging.Logger] = None,
    message: str = "",
    stop_time: float = 0,
    stop_return: Any = None,
    force_stop: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    记录函数执行时间到日志
    多线程安全，多进程不安全

    :param thr_time: 超过多长时间记录日志（秒）
    :param logger: 日志记录器对象
    :param message: 传递一些信息
    :param stop_time: 超过多长时间停止执行（秒）
    :param stop_return: 超时返回值
    :param force_stop: 超时是否停止执行
    :return: 装饰器函数
    """

    def decorator_function(function: Callable[..., T]) -> Callable[..., T]:
        @wraps(function)
        def wrapped_function(*args: Any, **kwargs: Any) -> T:
            t0: float = time.time()
            if stop_time and force_stop:
                try:
                    result: T = func_timeout(stop_time, function, args=args, kwargs=kwargs)
                except FunctionTimedOut:
                    if logger:
                        logger.warning("{}函数未在{}秒内完成，将强制停止".format(function.__name__, stop_time))
                    return stop_return  # type: ignore
            else:
                result = function(*args, **kwargs)
            t1: float = time.time()
            cost_time: float = t1 - t0
            if cost_time > thr_time:  # 大于多少秒的，则记录下来
                # print args,kwargs
                if logger:
                    logger.warning("{}\t{}\n{}\t{}".format(function.__name__, cost_time, args, kwargs))
            return result

        return wrapped_function

    return decorator_function


class Timer:
    """
    代码段执行时间计时器类

    用于标记和计算不同代码段的执行时间，支持多个标签的时间统计
    """

    def __init__(self, tag: str, logger: Optional[logging.Logger], **kwargs: Any):
        """
        初始化计时器

        :param tag: 主标签名称
        :param logger: 日志记录器对象
        :param kwargs: 其他附加数据
        """
        self.tag: str = tag
        self.logger: Optional[logging.Logger] = logger
        # func : [开始时间, 结束时间]
        self.data: Dict[str, List[float]] = defaultdict(list)
        self.other: Dict[str, Any] = dict(kwargs)
        self.tag_data_dcit: Dict[str, Any] = {}
        self.tag_start(self.tag)

    def tag_start(self, title: str) -> None:
        """
        开始计时某个标签

        :param title: 标签名称
        :return: None
        """
        self.data[title].append(time.time())

    def tag_end(self, title: str) -> None:
        """
        结束计时某个标签

        :param title: 标签名称
        :return: None
        """
        self.data[title].append(time.time())

    def tag_data(self, title: str, value: Any) -> None:
        """
        记录标签对应的自定义数据

        :param title: 标签名称
        :param value: 数据值
        :return: None
        """
        self.tag_data_dcit[title] = value

    def if_time(self, title: str, t: float) -> None:
        """
        如果执行时间超过阈值，则输出日志

        :param title: 标签名称
        :param t: 时间阈值（秒）
        :return: None
        """
        self.tag_end(self.tag)
        times: List[float] = self.data[title]
        if len(times) >= 2:
            s: float = times[-2]
            e: float = times[-1]
            cost: float = e - s
            if cost > t:
                _data: Dict[str, float] = {k: v[1] - v[0] for k, v in self.data.items() if len(v) >= 2}
                if self.logger:
                    self.logger.info(
                        "total:{}##{}##{}##{}".format(
                            cost,
                            self.tag,
                            _data,
                            json.dumps(self.tag_data_dcit, ensure_ascii=False),
                        )
                    )


if __name__ == "__main__":
    #####run_time_log#####
    # 注意：这里需要根据实际项目调整导入路径
    try:
        from utils.logging_ import FileHandler_
    except ImportError:
        # 如果导入失败，创建一个简单的logger用于测试
        import logging

        def FileHandler_(
            getLogger: str,
            setLevel: str,
            filename: str,
            mode: str = "w",
            StreamHandler: bool = False,
            formatter: Optional[Any] = None,
        ) -> logging.Logger:
            logger = logging.getLogger(getLogger)
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(filename, mode=mode, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s [%(filename)s,%(lineno)d] %(message)s"))
            logger.addHandler(handler)
            return logger

    FUNC_LOG_PATH: str = "func.log"  # 函数日志
    logger: logging.Logger = FileHandler_(
        getLogger="api",
        setLevel="logging.INFO",
        filename=FUNC_LOG_PATH,
        mode="w",
        StreamHandler=False,
        formatter=None,
    )

    @run_time_log(
        thr_time=0.5,
        logger=logger,
        stop_time=0.7,
        stop_return=[],
        force_stop=False,
    )
    def aaa(a: int, b: int, c: int = 0) -> Tuple[int, int, int]:
        print("aaaa")
        time.sleep(1)
        return a, b, c

    print(aaa(1, 2, c=3))

    # #####Timer#####
    #
    # def bbb() -> None:
    #     TITLE_FUN: str = "test"
    #     timer = Timer(tag=TITLE_FUN, logger=logger)
    #     # timer.tag_start(TITLE_FUN)
    #     timer.tag_start("aaa")
    #     time.sleep(1)
    #     timer.tag_end("aaa")
    #     timer.tag_start("bbb")
    #     time.sleep(2)
    #     timer.tag_end("bbb")
    #     timer.tag_data("ccccccccc", "value")
    #     # timer.tag_end(TITLE_FUN)
    #     timer.if_time(TITLE_FUN, 1)
    #
    #
    # bbb()
