"""
@Time   : 2018/12/14
@author : lijc210@163.com
@Desc:  : 功能描述 - 操作系统平台检测工具
"""

import socket
import sys
from platform import uname


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
    # 测试所有平台检测函数
    print(f"Is Windows: {is_windows()}")
    print(f"Is macOS: {is_mac()}")
    print(f"Is Linux: {is_linux()}")
    print(f"Is WSL: {is_wsl()}")
    print(f"Hostname: {get_hostname()}")
    print(f"Platform: {sys.platform}")
    print(f"Uname: {uname()}")
