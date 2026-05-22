"""
@Time   : 2019/1/8
@author : lijc210@163.com
@Desc:  : 企业微信机器人 Webhook 客户端

"""

import base64
import hashlib
import warnings
from typing import Optional

import requests
from retry import retry

warnings.filterwarnings("ignore")


class QyWeixinBot:
    """
    企业微信机器人 Webhook 客户端

    通过 Webhook 方式向企业微信群发送消息，支持文本、Markdown、图片、文件等。
    文档参考：https://developer.work.weixin.qq.com/document/path/91770
    """

    def __init__(self, webhook_key: Optional[str] = None):
        """
        初始化企业微信机器人
        """
        self.webhook_key = webhook_key
        self.base_url = "https://qyapi.weixin.qq.com"

    def _handle_response(self, res: requests.Response, mentioned_list=None):
        """
        处理 API 响应，处理错误码并返回结果

        :param res: requests 响应对象
        :param mentioned_list: @提醒列表
        :param key: 机器人 Webhook Key（用于错误时的回退消息）
        :return: 响应 JSON
        """
        result = res.json()
        errcode = result.get("errcode")

        if errcode == 45009:  # 接口调用超过限制
            raise ValueError(result.get("errmsg", "接口调用超过限制"))
        elif errcode != 0:
            print("发送失败：", result)
            # 发送错误信息作为文本消息
            fallback_data = {
                "msgtype": "text",
                "text": {
                    "content": result.get("errmsg", ""),
                    "mentioned_list": mentioned_list or ["@all"],
                },
            }
            webhook_url = f"{self.base_url}/cgi-bin/webhook/send?key={self.webhook_key}"
            requests.post(webhook_url, json=fallback_data, headers={"Content-Type": "application/json"})

        return result

    def send_markdown(self, content: str, key: str, mentioned_list=None, msgtype: str = "markdown"):
        """
        发送 Markdown 消息

        :param content: Markdown 内容
        :param key: 机器人 Webhook Key
        :param mentioned_list: @提醒列表
        :param msgtype: 消息类型，可选 markdown 或 post
        :return: 响应 JSON
        """
        if mentioned_list is None:
            mentioned_list = []
        webhook_url = f"{self.base_url}/cgi-bin/webhook/send?key={key}"
        data = {
            "msgtype": msgtype,
            msgtype: {
                "content": content,
            },
        }
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res, mentioned_list)

    @retry(tries=2, delay=60)
    def send_text(self, content: str = "", mentioned_list=None):
        """
        发送文本消息

        :param content: 文本内容
        :param key: 机器人 Webhook Key
        :param mentioned_list: @提醒列表，默认为空
        :return: 响应 JSON
        """
        if mentioned_list is None:
            mentioned_list = []
        webhook_url = f"{self.base_url}/cgi-bin/webhook/send?key={self.webhook_key}"
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list,
            },
        }
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res, mentioned_list)

    @retry(tries=2, delay=60)
    def send_img(self, md5: str = "", base64_data: str = ""):
        """
        发送图片消息

        :param md5: 图片的 MD5 值
        :param base64_data: 图片的 Base64 编码数据
        :param key: 机器人 Webhook Key
        :return: 响应 JSON
        """
        webhook_url = f"{self.base_url}/cgi-bin/webhook/send?key={self.webhook_key}"
        data = {"msgtype": "image", "image": {"base64": base64_data, "md5": md5}}
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "text/plain"})
        return self._handle_response(res)

    @retry(tries=2, delay=60)
    def upload_media(self, file_name: str, data: bytes):
        """
        上传临时素材

        :param file_name: 文件名
        :param data: 文件二进制数据
        :param key: 机器人 Webhook Key
        :return: 响应 JSON（包含 media_id）
        """
        url = f"{self.base_url}/cgi-bin/webhook/upload_media?key={self.webhook_key}&type=file"
        res = requests.post(url, files={"media": (file_name, data)})
        return self._handle_response(res)

    @retry(tries=2, delay=60)
    def send_file(self, media_id: str, key: str):
        """
        发送文件消息（需先调用 upload_media 获取 media_id）

        :param media_id: 素材 ID（由 upload_media 返回）
        :param key: 机器人 Webhook Key
        :return: 响应 JSON
        """
        webhook_url = f"{self.base_url}/cgi-bin/webhook/send?key={key}"
        data = {"msgtype": "file", "file": {"media_id": media_id}}
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res)

    @staticmethod
    def encode_image(file_path: str) -> tuple:
        """
        将图片文件编码为 Base64 和 MD5，用于 send_img 方法

        :param file_path: 图片文件路径
        :return: (md5, base64_data) 元组
        """
        with open(file_path, "rb") as f:
            data = f.read()
            base64_data = base64.b64encode(data).decode("utf-8")
            md5 = hashlib.md5(data).hexdigest()
        return md5, base64_data


if __name__ == "__main__":
    import os

    webhook_key = os.getenv("QYWEIXIN_WEBHOOK_KEY")
    bot = QyWeixinBot(webhook_key=webhook_key)

    # 发送文本消息
    content = """
    你好，这是一条测试消息
    """
    bot.send_text(content, ["@all"])

    # # 发送 Markdown 消息
    # content = """
    #     实时新增用户反馈<font color=\"warning\">132例</font>，请相关同事注意。\n
    #  >类型:<font color=\"comment\">用户反馈</font>
    #      >普通用户反馈:<font color=\"comment\">117例</font>
    #      >VIP用户反馈:<font color=\"comment\">15例</font>
    # """
    # bot.send_markdown(content, ["@all"])

    # # 发送图片
    # file_path = "data/test.png"
    # md5, base64_data = bot.encode_image(file_path)
    # bot.send_img(md5, base64_data)
