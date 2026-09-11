"""
@Time   : 2019/1/8
@author : lijc210@163.com
@Desc:  : 企业微信机器人 Webhook 客户端

"""

import base64
import hashlib
import os
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
        处理 API 响应，errcode 非 0 时抛出异常以触发重试

        :param res: requests 响应对象
        :param mentioned_list: @提醒列表
        :return: 响应 JSON
        :raises ValueError: errcode 非 0 时抛出异常
        """
        result = res.json()
        errcode = result.get("errcode")

        if errcode != 0:
            raise ValueError(f"发送失败, errcode={errcode}, errmsg={result.get('errmsg', '')}")

        return result

    def _send_fallback(self, content: str, mentioned_list=None):
        """
        重试全部失败后，向群里发送一条包含错误信息的文本消息

        :param content: 错误信息内容
        :param mentioned_list: @提醒列表
        """
        fallback_data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or ["@all"],
            },
        }
        webhook_url = f"{self.base_url}/cgi-bin/webhook/send?key={self.webhook_key}"
        requests.post(webhook_url, json=fallback_data, headers={"Content-Type": "application/json"})

    def _send_with_retry(self, send_once, mentioned_list=None, tries: int = 2, delay: int = 60):
        """
        带重试地执行发送；全部重试失败后仅发送一次兜底错误消息，再抛出异常

        :param send_once: 单次发送的可调用对象（无参数）
        :param mentioned_list: @提醒列表，用于兜底消息
        :param tries: 总尝试次数，默认 2
        :param delay: 重试间隔秒数，默认 60
        :return: 响应 JSON
        :raises Exception: 重试全部失败后重新抛出最后一个异常
        """

        @retry(tries=tries, delay=delay)
        def _send():
            return send_once()

        try:
            return _send()
        except Exception as exc:
            # 全部重试失败后，仅发送一次兜底错误消息
            self._send_fallback(str(exc), mentioned_list)
            raise

    def _post_message(self, msgtype: str, payload: dict, mentioned_list=None, headers: Optional[dict] = None):
        """
        单次发送 webhook 消息（不含重试与兜底逻辑）

        :param msgtype: 消息类型，如 text / markdown / image / file
        :param payload: 对应消息类型的参数体
        :param mentioned_list: @提醒列表
        :param headers: 请求头，默认 application/json
        :return: 响应 JSON
        """
        webhook_url = f"{self.base_url}/cgi-bin/webhook/send?key={self.webhook_key}"
        data = {"msgtype": msgtype, msgtype: payload}
        res = requests.post(
            webhook_url,
            json=data,
            headers=headers if headers is not None else {"Content-Type": "application/json"},
        )
        return self._handle_response(res, mentioned_list)

    def send_markdown(self, content: str, mentioned_list=None, msgtype: str = "markdown"):
        """
        发送 Markdown 消息

        :param content: Markdown 内容
        :param mentioned_list: @提醒列表
        :param msgtype: 消息类型，可选 markdown 或 markdown_v2
        :return: 响应 JSON
        """
        if mentioned_list is None:
            mentioned_list = []
        return self._send_with_retry(
            lambda: self._post_message(msgtype, {"content": content}, mentioned_list),
            mentioned_list,
        )

    def send_text(self, content: str = "", mentioned_list=None):
        """
        发送文本消息

        :param content: 文本内容
        :param mentioned_list: @提醒列表，默认为空
        :return: 响应 JSON
        """
        if mentioned_list is None:
            mentioned_list = []
        return self._send_with_retry(
            lambda: self._post_message(
                "text",
                {"content": content, "mentioned_list": mentioned_list},
                mentioned_list,
            ),
            mentioned_list,
        )

    def send_img(self, md5: str = "", base64_data: str = ""):
        """
        发送图片消息

        :param md5: 图片的 MD5 值
        :param base64_data: 图片的 Base64 编码数据
        :return: 响应 JSON
        """
        return self._send_with_retry(
            lambda: self._post_message(
                "image",
                {"base64": base64_data, "md5": md5},
                headers={"Content-Type": "text/plain"},
            )
        )

    def upload_media(self, file_name: str, data: bytes):
        """
        上传临时素材

        :param file_name: 文件名
        :param data: 文件二进制数据
        :return: 响应 JSON（包含 media_id）
        """

        def _upload_once():
            url = f"{self.base_url}/cgi-bin/webhook/upload_media?key={self.webhook_key}&type=file"
            res = requests.post(url, files={"media": (file_name, data)})
            return self._handle_response(res)

        return self._send_with_retry(_upload_once)

    def send_file(self, media_id: str):
        """
        发送文件消息（需先调用 upload_media 获取 media_id）

        :param media_id: 素材 ID（由 upload_media 返回）
        :return: 响应 JSON
        """
        return self._send_with_retry(lambda: self._post_message("file", {"media_id": media_id}))

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
