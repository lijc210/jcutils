"""
@File    :   logging_.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :   日志配置

Python 的 logging 模块默认情况下将日志消息输出到标准错误 (stderr) 流中，
原因主要是为了与标准输出 (stdout) 区分开来，以便在需要时能够轻松地将日志消息重定向到文件或其他位置。

"""

import logging
import os
import tempfile
from logging.handlers import RotatingFileHandler


def configure_logging(
    log_filename="",
    log_level="logging.INFO",
    max_bytes=10485760,
    backup_count=5,
    name="",
):
    """
    同时输出到控制台和文件
    """
    format = "[%(asctime)s] %(levelname)s %(filename)s[%(lineno)d]: %(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(eval(log_level))  # DEBUG输出调试日志，INFO则不输出日志
    formatter = logging.Formatter(format)

    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 添加文件处理器
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def configure_logging_file(
    log_filename="",
    log_level="logging.INFO",
    max_bytes=10485760,
    backup_count=5,
    name="",
):
    """
    只输出到文件
    """
    format = "[%(asctime)s] %(levelname)s %(filename)s[%(lineno)d]: %(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(eval(log_level))  # DEBUG输出调试日志，INFO则不输出日志
    formatter = logging.Formatter(format)

    # 添加文件处理器
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    tempdir = tempfile.gettempdir()
    print(tempfile.gettempdir())

    log_filename = os.path.join(tempdir, "app.log")

    # 输出到控制台和文件
    logger = configure_logging(log_filename=log_filename, name="app")

    # 只输出到文件(注意项目不能使用logging.basicConfig，否则配置会被覆盖)
    logger_file = configure_logging_file(log_filename=log_filename, name="app_file")
    logger.debug("debug")
    logger.info("info")
    logger_file.info("info file")

    # 要输出到其他文件，必须要修改 name 参数
    other_log = os.path.join(tempdir, "other.log")
    logger = configure_logging_file(log_filename=other_log, name="other_log")
