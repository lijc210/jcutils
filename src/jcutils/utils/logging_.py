"""
@File    :   logging_.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :   日志配置

Python 的 logging 模块默认情况下将日志消息输出到标准错误 (stderr) 流中，
原因主要是为了与标准输出 (stdout) 区分开来，以便在需要时能够轻松地将日志消息重定向到文件或其他位置。

"""

from __future__ import annotations

import logging
import os
import tempfile
from logging.handlers import RotatingFileHandler

# 日志格式
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(filename)s[%(lineno)d]: %(message)s"

# 这些取值表示显式关闭日志初始化
_LOG_LEVEL_OFF_VALUES = {"OFF", "NONE", "DISABLE", "DISABLED"}

# 支持的输出方式
_OUTPUT_VALUES = {"console", "file", "both"}


def parse_log_level(log_level: str | int | None = None) -> int | None:
    """
    解析日志级别，优先级：入参 > LOG_LEVEL 环境变量 > INFO。

    入参支持 20、"INFO"、"logging.INFO" 等写法；
    返回 None 表示显式关闭日志（LOG_LEVEL 为 OFF/NONE/DISABLE 等）。
    """
    if isinstance(log_level, int):
        return log_level

    level_name = (log_level or os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    if level_name in _LOG_LEVEL_OFF_VALUES:
        return None

    if level_name.startswith("LOGGING."):
        level_name = level_name[len("LOGGING.") :]

    level = getattr(logging, level_name, None)
    if isinstance(level, int):
        return level

    logging.getLogger(__name__).warning("[logging] 无效的日志级别 %s，已回退为 INFO", level_name)
    return logging.INFO


def configure_logging(
    log_filename: str = "",
    log_level: str | int | None = None,
    max_bytes: int = 10485760,
    backup_count: int = 5,
    name: str = "",
    output: str = "console",
    propagate: bool = True,
) -> logging.Logger:
    """
    配置并返回 logger，默认只输出到屏幕。

    - log_level: 优先级为 入参 > LOG_LEVEL 环境变量 > INFO；传 OFF 时不初始化
    - output: "console"（默认，仅屏幕）、"file"（仅文件）、"both"（屏幕 + 文件）
    - propagate: 是否向父级 logger 传播，自带 handler 时通常应设为 False 避免重复输出

    同一 logger 重复调用时不会重复添加同类型的 handler。
    """
    output = (output or "console").strip().lower()
    if output not in _OUTPUT_VALUES:
        raise ValueError(f"不支持的输出方式: {output}，可选值: console / file / both")

    logger = logging.getLogger(name)
    level = parse_log_level(log_level)
    # 显式关闭：不添加 handler，交给使用方的 logging 配置
    if level is None:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)

    # 已有的 handler 类型，避免重复调用时重复输出
    has_console = any(
        isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    )
    has_file = any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)

    if output in {"console", "both"} and not has_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if output in {"file", "both"} and not has_file:
        if not log_filename:
            log_filename = os.path.join(tempfile.gettempdir(), f"{name or 'app'}.log")
        file_handler = RotatingFileHandler(log_filename, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = propagate
    return logger


if __name__ == "__main__":
    tempdir: str = tempfile.gettempdir()
    log_filename: str = os.path.join(tempdir, "app.log")

    # 默认只输出到屏幕，级别取 LOG_LEVEL，未设置时为 INFO
    logger: logging.Logger = configure_logging(name="app")

    # 同时输出到屏幕和文件
    logger_both: logging.Logger = configure_logging(log_filename=log_filename, name="app_both", output="both")

    # 只输出到文件
    logger_file: logging.Logger = configure_logging(log_filename=log_filename, name="app_file", output="file")

    logger.debug("debug")
    logger.info("info")
    logger_both.info("info both")
    logger_file.info("info file")

    # 要输出到其他文件，需要换一个 name
    other_log: str = os.path.join(tempdir, "other.log")
    other_logger: logging.Logger = configure_logging(log_filename=other_log, name="other_log", output="file")
    other_logger.info("info other")
