"""
@Time   : 2018/12/14
@author : lijc210@163.com
@Desc:  : 功能描述 - 平台信息获取工具
"""

import platform
import socket
import sys
from platform import uname


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


def is_windows() -> bool:
    """
    检测当前系统是否为Windows

    :return: 如果是Windows返回True，否则返回False
    """
    return sys.platform == "win32"


def is_mac() -> bool:
    """
    检测当前系统是否为macOS

    :return: 如果是macOS返回True，否则返回False
    """
    return sys.platform == "darwin"


def is_wsl() -> bool:
    """
    检测当前系统是否为Windows Subsystem for Linux (WSL)

    :return: 如果是WSL返回True，否则返回False
    """
    return "microsoft-standard" in uname().release


def is_linux() -> bool:
    """
    检测当前系统是否为Linux

    :return: 如果是Linux返回True，否则返回False
    """
    return sys.platform == "linux"


def get_hostname() -> str:
    """
    获取当前主机名

    :return: 主机名字符串
    """
    return socket.gethostname()


if __name__ == "__main__":
    print(f"Platform: {get_platform()}")
    print(f"System: {get_system()}")
    print(f"Is Windows: {is_windows()}")
    print(f"Is macOS: {is_mac()}")
    print(f"Is Linux: {is_linux()}")
    print(f"Is WSL: {is_wsl()}")
    print(f"Hostname: {get_hostname()}")
    print(f"Platform: {sys.platform}")
    print(f"Uname: {uname()}")
