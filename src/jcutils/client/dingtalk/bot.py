"""
@Time   : 2019/1/8
@author : lijc210@163.com
@Desc:  : 钉钉机器人 Webhook 客户端

"""

import base64
import hashlib
import hmac
import os
import time
import urllib.parse
import warnings
from typing import Optional

import requests
from retry import retry

warnings.filterwarnings("ignore")


class DingTalkBot:
    """
    钉钉机器人 Webhook 客户端

    通过 Webhook 方式向钉钉群发送消息，支持文本、Markdown、图片、文件等。
    文档参考：https://open.dingtalk.com/document/groups/robot-overview
    """

    def __init__(self, access_token: Optional[str] = None, secret: Optional[str] = None):
        """
        初始化钉钉机器人

        :param access_token: 机器人 access_token
        :param secret: 机器人签名密钥
        """
        self.access_token = access_token
        self.secret = secret
        self.base_url = "https://oapi.dingtalk.com"

    def _get_sign(self) -> tuple:
        """
        生成钉钉机器人签名

        :return: (timestamp, sign) 元组
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def _get_webhook_url(self) -> str:
        """
        获取完整的 Webhook URL（包含签名）

        :return: Webhook URL
        """
        if self.secret:
            timestamp, sign = self._get_sign()
            return f"{self.base_url}/robot/send?access_token={self.access_token}&timestamp={timestamp}&sign={sign}"
        else:
            return f"{self.base_url}/robot/send?access_token={self.access_token}"

    def _handle_response(self, res: requests.Response, mentioned_list=None):
        """
        处理 API 响应，处理错误码并返回结果

        :param res: requests 响应对象
        :param mentioned_list: @提醒列表
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
                    "at": {
                        "isAtAll": mentioned_list is not None and "@all" in mentioned_list,
                    },
                },
            }
            webhook_url = self._get_webhook_url()
            requests.post(webhook_url, json=fallback_data, headers={"Content-Type": "application/json"})

        return result

    def send_markdown(self, content: str, title: str = "", mentioned_list=None):
        """
        发送 Markdown 消息

        :param content: Markdown 内容
        :param title: 消息标题
        :param mentioned_list: @提醒列表
        :return: 响应 JSON
        """
        if mentioned_list is None:
            mentioned_list = []
        webhook_url = self._get_webhook_url()
        data = {
            "msgtype": "markdown",
            "markdown": {
                "text": content,
                "title": title,
            },
        }
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res, mentioned_list)

    @retry(tries=2, delay=60)
    def send_text(self, content: str = "", mentioned_list=None):
        """
        发送文本消息

        :param content: 文本内容
        :param mentioned_list: @提醒列表，默认为空
        :return: 响应 JSON
        """
        if mentioned_list is None:
            mentioned_list = []
        webhook_url = self._get_webhook_url()
        data = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {
                "isAtAll": "@all" in mentioned_list,
                "atMobiles": [item for item in mentioned_list if item != "@all"],
            },
        }
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res, mentioned_list)

    @retry(tries=2, delay=60)
    def send_image(self, base64_data: str, md5: str):
        """
        发送图片消息

        :param base64_data: 图片的 Base64 编码数据
        :param md5: 图片的 MD5 值
        :return: 响应 JSON
        """
        webhook_url = self._get_webhook_url()
        data = {"msgtype": "image", "image": {"base64": base64_data, "md5": md5}}
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res)

    @retry(tries=2, delay=60)
    def upload_media(self, file_name: str, data: bytes):
        """
        上传临时素材

        :param file_name: 文件名
        :param data: 文件二进制数据
        :return: 响应 JSON（包含 media_id）
        """
        webhook_url = self._get_webhook_url()
        res = requests.post(webhook_url, files={"media": (file_name, data)})
        return self._handle_response(res)

    @retry(tries=2, delay=60)
    def send_file(self, media_id: str):
        """
        发送文件消息（需先调用 upload_media 获取 media_id）

        :param media_id: 素材 ID（由 upload_media 返回）
        :return: 响应 JSON
        """
        webhook_url = self._get_webhook_url()
        data = {"msgtype": "file", "file": {"media_id": media_id}}
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res)

    @staticmethod
    def encode_image(file_path: str) -> tuple:
        """
        将图片文件编码为 Base64 和 MD5，用于 send_image 方法

        :param file_path: 图片文件路径
        :return: (base64_data, md5) 元组
        """
        with open(file_path, "rb") as f:
            data = f.read()
            base64_data = base64.b64encode(data).decode("utf-8")
            md5 = hashlib.md5(data).hexdigest()
        return base64_data, md5

    def send_action_card(self, title: str, text: str, btn_orientation: str = "0", btns: list = None):
        """
        发送 ActionCard 消息

        :param title: 消息标题
        :param text: Markdown 格式的消息内容
        :param btn_orientation: 按钮排列方向，0-竖排，1-横排
        :param btns: 按钮列表，格式：[{"title": "按钮标题", "actionURL": "跳转链接"}]
        :return: 响应 JSON
        """
        if btns is None:
            btns = []
        webhook_url = self._get_webhook_url()
        data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "btnOrientation": btn_orientation,
                "btns": btns,
            },
        }
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res)

    def send_feed_card(self, title: str, links: list):
        """
        发送 FeedCard 消息

        :param title: 消息标题
        :param links: 链接列表，格式：[{"title": "标题", "messageURL": "链接", "picURL": "图片链接"}]
        :return: 响应 JSON
        """
        webhook_url = self._get_webhook_url()
        data = {
            "msgtype": "feedCard",
            "feedCard": {
                "title": title,
                "links": links,
            },
        }
        res = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})
        return self._handle_response(res)


if __name__ == "__main__":
    access_token = os.getenv("DINGTALK_ACCESS_TOKEN")
    secret = os.getenv("DINGTALK_SECRET")
    bot = DingTalkBot(access_token=access_token, secret=secret)

    # 发送文本消息
    content = """
    你好，这是一条测试消息
    """
    bot.send_text(content, ["@all"])

    # 发送 Markdown 测试消息
    content = """
        你好，这是一条测试消息
        实时新增用户反馈<font color="warning">132例</font>，请相关同事注意。\n
     >类型:<font color="comment">用户反馈</font>
         >普通用户反馈:<font color="comment">117例</font>
         >VIP用户反馈:<font color="comment">15例</font>
    """
    bot.send_markdown(content, title="用户反馈", mentioned_list=["@all"])

    # # 发送图片
    # file_path = "data/test.png"
    # base64_data, md5 = bot.encode_image(file_path)
    # bot.send_image(base64_data, md5)

    # # 发送 ActionCard
    # bot.send_action_card(
    #     title="ACTIONCARD",
    #     text="### 乔布斯\n 你小时候就该认真玩iPhone了\n\n![img](http://www.wailian.link/images/2016/02/05/icon.png)\n\n"
    #          "[选择按钮](http://www.taobao.com)",
    #     btns=[{"title": "选择1", "actionURL": "https://www.dingtalk.com"}]
    # )

    # # 发送 FeedCard
    # bot.send_feed_card(
    #     title="FEEDCARD",
    #     links=[{
    #         "title": "时代峰峻--TFBOYS",
    #         "messageURL": "https://www.dingtalk.com",
    #         "picURL": "http://www.wailian.link/images/2016/02/05/tfboys.jpg"
    #     }]
    # )
