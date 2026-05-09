"""
@File    :   __init__.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :   None
"""

from jcutils._core import calculate_differences, hello_from_bin, say_hello


def main() -> None:
    print(hello_from_bin())
    print(say_hello())
    result = calculate_differences([20230101, 20230102, 20230105])
    print(result)
