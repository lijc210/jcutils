import socket
import sys
from platform import uname


def is_windows():
    return sys.platform == "win32"


def is_mac():
    return sys.platform == "darwin"


def is_wsl():
    return "microsoft-standard" in uname().release


def is_linux():
    return sys.platform == "linux"


def get_hostname():
    return socket.gethostname()
