"""
@author: lijc210@163.com
@file: tool_threading.py
@time: 2020/03/11
@desc: 多线程类
提供简单的多线程执行和结果获取功能
"""

import time
from threading import Thread
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class MyThread(Thread):
    """
    自定义线程类，用于执行函数并获取返回结果

    继承自 threading.Thread，提供了方便的结果获取机制
    """

    def __init__(
        self, func: Callable[..., T], args: Tuple[Any, ...] = (), kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        初始化线程对象

        :param func: 要在线程中执行的函数
        :param args: 传递给函数的位置参数元组
        :param kwargs: 传递给函数的关键字参数字典
        """
        super().__init__()
        self.func: Callable[..., T] = func
        self.args: Tuple[Any, ...] = args
        self.kwargs: dict = kwargs if kwargs is not None else {}
        self.result: Any = None

    def run(self) -> None:
        """
        线程执行的方法

        当调用 start() 时，这个方法会在新的线程中执行
        执行传入的函数并保存返回结果
        """
        self.result = self.func(*self.args, **self.kwargs)

    def get_result(self) -> Any:
        """
        获取函数执行的结果

        :return: 函数的返回值，如果执行出错则返回 None
        """
        try:
            return self.result
        except Exception:
            return None


def run_threads(funcs_args: List[Tuple[Callable[..., T], Tuple[Any, ...], Optional[Dict[str, Any]]]]) -> List[Any]:
    """
    并行执行多个函数

    :param funcs_args: 函数和参数的列表，每个元素是 (函数, 位置参数元组, 关键字参数字典)
                     例如: [(func1, (arg1, arg2), {}), (func2, (), {'kwarg': value})]
    :return: 所有函数的返回值列表，顺序与输入一致
    """
    threads: List[MyThread] = []
    for func, args, kwargs in funcs_args:
        thread = MyThread(func, args, kwargs)
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 收集结果
    results: List[Any] = []
    for thread in threads:
        results.append(thread.get_result())

    return results


if __name__ == "__main__":
    # 测试基本功能
    def task(n: int) -> int:
        """模拟耗时任务"""
        time.sleep(n)
        return n * 10

    # 创建并启动两个线程
    t1 = MyThread(task, args=(1,))
    t2 = MyThread(task, args=(3,))

    t1.start()
    t2.start()

    start_time = time.time()

    t1.join()
    t2.join()

    res1 = t1.get_result()
    res2 = t2.get_result()

    print(f"任务1结果: {res1}")  # 应该输出 10
    print(f"任务2结果: {res2}")  # 应该输出 30

    elapsed_time = time.time() - start_time
    print(f"总耗时: {elapsed_time:.2f}秒")  # 应该接近3秒（并行执行）

    # 测试使用 kwargs
    def task_with_kwargs(name: str, multiplier: int = 2) -> str:
        """使用关键字参数的任务"""
        time.sleep(0.5)
        return f"{name} * {multiplier} = {len(name) * multiplier}"

    t3 = MyThread(task_with_kwargs, args=("Python",), kwargs={"multiplier": 3})
    t3.start()
    t3.join()

    print(f"任务3结果: {t3.get_result()}")  # 应该输出 "Python * 3 = 18"

    # 测试 run_threads 函数
    print("\n测试 run_threads 函数:")

    def compute_square(x: int) -> int:
        time.sleep(0.1)
        return x * x

    def compute_cube(x: int) -> int:
        time.sleep(0.1)
        return x * x * x

    def compute_double(x: int) -> int:
        time.sleep(0.1)
        return x * 2

    tasks = [
        (compute_square, (5,), {}),
        (compute_cube, (3,), {}),
        (compute_double, (4,), {}),
    ]

    results = run_threads(tasks)
    print(f"并行执行结果: {results}")  # 应该输出 [25, 27, 8]
