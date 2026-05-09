# coding: utf-8
"""
@File    :   format_utils.py
@Time    :   2024/08/03 17:54:47
@Author  :   lijc210@163.com
@Desc    :   tabulate因字体长度，在html和微信中显示不正常，可以使用table_format函数
"""

from typing import List, Union

import wcwidth


def print_format(string: str, way: str = "^", width: int = 10, fill: str = " ") -> str:
    """
    格式化输出字符串，支持中文、英文、数字等，支持居中、左对齐、右对齐，支持填充字符，支持换行符

    :param string: 要输出的字符串
    :param way: 输出方式，"^"为居中，">"为右对齐，"<"为左对齐
    :param width: 输出宽度
    :param fill: 填充字符
    :return: 格式化后的字符串
    """
    count: int = wcwidth.wcswidth(string) - len(string)  # 宽字符数量
    width = width - count if width >= count else 0  # 调整宽度，保证填充后的长度正确
    text: str = "{0:{1}{2}{3}}".format(string, fill, way, width)  # 格式化字符串
    return text


def table_format(title: str, data_list: List[List[Union[str, int, float]]], way: str = "^") -> str:
    """
    格式化输出表格

    :param title: 表格标题
    :param data_list: 表格数据，二维列表
    :param way: 输出方式，"^"为居中，">"为右对齐，"<"为左对齐
    :return: 格式化后的表格字符串
    """
    text: str = "## " + title + "\n\n"  # 添加标题

    # 计算每一列的最大宽度
    col_widths: List[int] = [max(wcwidth.wcswidth(str(cell)) for cell in col) for col in zip(*data_list)]

    # 格式化每一行数据
    for row in data_list:
        for i, cell in enumerate(row):
            if isinstance(cell, float):
                cell = "{:.2f}".format(cell)  # 保留两位小数
            count: int = wcwidth.wcswidth(str(cell)) - len(str(cell))  # 计算宽字符数量
            width: int = col_widths[i] + 4  # 保证表格有一定的空隙
            width = width - count if width >= count else 0  # 调整宽度
            text += "|" + "{0:{1}{2}{3}}".format(cell, " ", way, width)  # 格式化每个单元格
        text += "" + "|\n"  # 换行
    return text


if __name__ == "__main__":
    # 测试print_format函数
    text: str = print_format("《深度学习 deep learning》", width=30)
    print(text)
    text = print_format("《C++ primer plus》", width=30)
    print(text)
    text = print_format("日文 君の名は", "^", width=30)
    print(text)
    text = print_format("韩语 하늘의 3 분의 1은 파멸", width=30)
    print(text)

    print("#" * 50)

    # 示例使用table_format函数
    start_time: str = "2024-07-01"
    end_time: str = "2024-07-31"
    title: str = f"处理状态统计 {start_time}-{end_time}"
    data: List[List[Union[str, float]]] = [
        ["门店编码", "差异", "订单中心", "dws"],
        ["615032", 31.00, 392.36, 361.36],
        ["158237", 29.43, 53.10, 23.67],
        ["610126", 23.40, 358.60, 335.20],
        ["318412", 22.69, 47.38, 24.69],
        ["610033", 12.50, 56.30, 43.80],
        ["371298", 11.90, 274.80, 262.90],
        ["410642", 11.90, 59.50, 47.60],
        ["140067", 9.90, 191.10, 181.20],
        ["323179", 9.10, 161.06, 151.96],
        ["140707", 7.60, 89.67, 82.07],
    ]

    markdown_table: str = table_format(title, data)
    print(markdown_table)
