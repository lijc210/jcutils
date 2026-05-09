# coding: utf-8
"""
@File    :   tabulate_utils.py
@Time    :   2024/08/03 17:54:47
@Author  :   lijc210@163.com
@Desc    :   Tabulate表格格式化工具，支持多种表格格式输出
"""

from typing import Any, Dict, List, Sequence, Union

import tabulate

tabulate.WIDE_CHARS_MODE = True


def table_to_markdown(
    data: Union[Sequence[Sequence[Any]], Dict[str, Sequence[Any]]],
    headers: Union[Sequence[str], str, Dict[str, str]] = (),
    tablefmt: str = "simple_outline",
    showindex: Union[bool, str, Sequence[int]] = False,
) -> str:
    """
    使用 tabulate 库将数据转换为 Markdown 格式的表格

    支持多种表格格式：
    - "pipe": GitHub Flavored Markdown 格式
    - "grid": 网格格式
    - "simple": 简单格式
    - "orgtbl": Org 模式表格
    - "rst": reStructuredText 表格
    - "mediawiki": MediaWiki 表格
    - "latex": LaTeX 表格
    - "latex_booktabs": LaTeX 表格（使用 booktabs）
    - "html": HTML 表格
    - "textile": Textile 格式
    - "simple_outline": 简单大纲格式

    :param data: 需要转换的数据，可以是二维列表或字典
                 例如: [[1, 'Alice', 24], [2, 'Bob', 30]]
                 或: {'Name': ['Alice', 'Bob'], 'Age': [30, 25]}
    :param headers: 列标题，可以是列表、字符串或 None
                   例如: ['ID', 'Name', 'Age']、"firstrow"、"keys"或 ()
    :param tablefmt: 表格格式字符串，默认为 "simple_outline"
    :param showindex: 是否显示行索引，可以是布尔值、字符串或整数序列
                    例如: True, False, "always", "never", [1, 2, 3]
    :return: 格式化后的表格字符串
    """
    # 使用 tabulate 库将数据转换为指定格式的表格
    markdown_table: str = tabulate.tabulate(data, headers=headers, tablefmt=tablefmt, showindex=showindex)
    return markdown_table


if __name__ == "__main__":
    # 示例使用 - 字典数据
    data_dict: Dict[str, Sequence[Any]] = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [30, 25, 35],
        "City": ["New York", "Los Angeles", "Chicago"],
    }

    # 生成 Markdown 表格
    markdown_table_dict: str = table_to_markdown(data_dict, headers="keys", tablefmt="pipe")

    print("字典数据示例:")
    print(markdown_table_dict)
    print()

    # 数据：一个包含多个子列表的列表，每个子列表代表一行
    data_list: List[List[Union[str, int]]] = [
        ["Name", "Age", "City"],
        ["Alice", 30, "New York"],
        ["Bob", 25, "Los Angeles"],
        ["Charlie", 35, "Chicago"],
    ]

    # 生成 Markdown 表格
    markdown_table_list: str = table_to_markdown(data_list, headers="firstrow", tablefmt="textile")

    print("列表数据示例:")
    print(markdown_table_list)
    print()

    # 测试不同的表格格式
    data_simple: List[List[Any]] = [
        ["ID", "Name", "Score"],
        [1, "张三", 95.5],
        [2, "李四", 88.0],
        [3, "王五", 92.5],
    ]

    formats: List[str] = ["pipe", "grid", "simple", "rst", "html", "latex"]

    for fmt in formats:
        print(f"\n格式: {fmt}")
        print("-" * 40)
        try:
            table_result: str = table_to_markdown(data_simple, headers="firstrow", tablefmt=fmt, showindex=True)
            print(table_result)
        except Exception as e:
            print(f"错误: {e}")

    # 测试带索引的表格
    print("\n\n带行索引的表格:")
    print("-" * 40)
    indexed_table: str = table_to_markdown(data_simple, headers="firstrow", tablefmt="simple", showindex=True)
    print(indexed_table)
