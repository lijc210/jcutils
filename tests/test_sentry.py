import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from src.api.config import CONFIG

sentry_sdk.init(
    dsn=CONFIG.SENTRY_URL,
    traces_sample_rate=0.1,
    integrations=[
        LoggingIntegration(
            level=logging.INFO,  # 设置你希望发送到 Sentry 的日志级别
            event_level=logging.ERROR,  # 设置你希望发送到 Sentry 的事件级别
        )
    ],
)
logging.basicConfig(level=logging.INFO)

logging.debug("debuq4")
logging.info("info4")
logging.warning("warning4")
logging.error("error测试5")
# logging.exception("An exception happened")


# 发送信息到 Sentry
# sentry_sdk.capture_message("This is an info message")
# sentry_sdk.capture_exception("This is error info message")
