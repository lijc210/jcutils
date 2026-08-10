import os

from src.jcutils.client import QyWeixinBot

webhook_key = os.getenv("QYWEIXIN_WEBHOOK_KEY")
bot = QyWeixinBot(webhook_key=webhook_key)

# 发送文本消息
content = """
你好，这是一条测试消息
"""
bot.send_text(content, ["@all"])
