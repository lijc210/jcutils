"""
@Time   : 2018/12/14
@author : lijc210@163.com
@Desc:  : 功能描述 - 平台信息获取工具
"""

import platform


def get_platform() -> str:
    """
    获取操作系统名称及版本号

    返回格式类似：'Linux-5.4.0-80-generic-x86_64-with-glibc2.29'
    或 'Windows-10-10.0.19041-SP0' 或 'Darwin-20.6.0-x86_64-i386-64bit'

    :return: 包含操作系统信息的字符串
    """
    return platform.platform()


def get_system() -> str:
    """
    获取操作系统名称

    返回值可能是：'Linux', 'Windows', 'Darwin' (macOS) 等

    :return: 操作系统名称字符串
    """
    return platform.system()


if __name__ == "__main__":
    print(f"Platform: {get_platform()}")
    print(f"System: {get_system()}")
