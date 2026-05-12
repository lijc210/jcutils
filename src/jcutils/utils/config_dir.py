# coding: utf-8
""" """

# import os
# from typing import Tuple

# from .config_loader import app_config
# from .platform_ import is_mac, is_windows

# APP_NAME = app_config.APP_NAME


# def get_dir() -> Tuple[str, str]:
#     if is_windows():
#         win_drive = "D:\\"  # Windows 路径
#         if os.path.exists(win_drive) is False:
#             win_drive = "C:\\"
#         DATA_DIR = os.path.join(f"{win_drive}data\\", APP_NAME)
#         LOGS_DIR = os.path.join(f"{win_drive}logs\\", APP_NAME)
#         return DATA_DIR, LOGS_DIR
#     elif is_mac():
#         # 获取用户目录
#         HOME_DIR = os.path.expanduser("~")
#         DATA_DIR = os.path.join(f"{HOME_DIR}/data/", APP_NAME)  # mac无法创建/data
#         LOGS_DIR = os.path.join(f"{HOME_DIR}/logs/", APP_NAME)
#         return DATA_DIR, LOGS_DIR
#     else:
#         DATA_DIR = os.path.join("/data/", APP_NAME)
#         LOGS_DIR = os.path.join("/logs/", APP_NAME)
#         return DATA_DIR, LOGS_DIR


# DATA_DIR, LOGS_DIR = get_dir()

# for dir_name in [DATA_DIR, LOGS_DIR]:
#     os.makedirs(dir_name, exist_ok=True)
