# coding: utf-8
"""
@File    :   tabulate_utils.py
@Time    :   2024/08/03 17:54:47
@Author  :   lijc210@163.com
@Desc    :   None
"""

from tabulate import tabulate


def table_to_markdown(data, headers=(), tablefmt="simple_outline", showindex=False):
    """
    https://github.com/astanin/python-tabulate
    将数据转换为 Markdown 格式的表格。

    :param data: 需要转换的二维数据列表。例如: [[1, 'Alice', 24], [2, 'Bob', 30]]
    :param headers: 可选的列标题。例如: ['ID', 'Name', 'Age'],"firstrow","keys"
    :param tablefmt: 表格格式。例如: "pipe", "grid", "simple", "orgtbl", "rst", "mediawiki", "latex", "latex_booktabs"等
    :param showindex: 是否显示行索引。例如: True, False
    :return: Markdown 格式的表格
    """
    # 使用 tabulate 库将数据转换为 Markdown 格式
    markdown_table = tabulate(data, headers=headers, tablefmt=tablefmt, showindex=showindex)
    return markdown_table


if __name__ == "__main__":
    # 示例使用
    # data = {"Name": ["Alice", "Bob", "Charlie"], "Age": [30, 25, 35], "City": ["New York", "Los Angeles", "Chicago"]}

    # # 生成 Markdown 表格
    # markdown_table = table_to_markdown(data, headers="keys")

    # print(markdown_table)

    # 数据：一个包含多个子列表的列表，每个子列表代表一行
    data = [
        ["Name", "Age", "City"],
        ["Alice", 30, "New York"],
        ["Bob", 25, "Los Angeles"],
        ["Charlie", 35, "Chicago"],
    ]

    # 生成 Markdown 表格
    markdown_table = table_to_markdown(data, tablefmt="simple_outline")

    print(markdown_table)
