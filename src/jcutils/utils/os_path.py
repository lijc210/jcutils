"""
@Time   : 2018/12/14
@author : lijc210@163.com
@Desc:  : 功能描述。
"""

import os
from typing import List


def get_file_path_list(rootdir: str) -> List[str]:
    """
    获取指定目录下所有文件的路径列表
    :param rootdir: 根目录路径
    :return: 文件路径列表
    """
    file_list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    file_path_list: List[str] = []
    for i in range(0, len(file_list)):
        path = os.path.join(rootdir, file_list[i])
        if os.path.isfile(path):
            file_path_list.append(path)
    return file_path_list


if __name__ == "__main__":
    get_file_path_list("/usr/local")
