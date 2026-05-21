"""
Created on 2017/6/15 0015
@author: lijc210@163.com
Desc: 功能描述。
#企业号开发者平台，发送消息文档
http://qydev.weixin.qq.com/wiki/index.php?title=%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F
"""

import json
import os
import tempfile
import time
import traceback
import warnings

import requests

warnings.filterwarnings("ignore")


class QyWeixinClient(object):
    """
    描述：企业号发送消息
    """

    def __init__(self, corp_id, secret):
        self.corp_id = corp_id
        self.secret = secret
        self.diff = 7000
        # 临时目录，跨平台兼容
        self.temp_dir = tempfile.gettempdir()
        self.qyapi_url = "https://qyapi.weixin.qq.com"

    def refresh_token(self, agentid):
        TOKEN_PATH = os.path.join(self.temp_dir, f"{self.corp_id}_{agentid}.token")
        TOKEN_TIMESTAMP_PATH = os.path.join(self.temp_dir, f"{self.corp_id}_{agentid}.timestamp")
        last_time = 0
        need_refresh = False
        if os.path.exists(TOKEN_TIMESTAMP_PATH):
            f_time = open(TOKEN_TIMESTAMP_PATH)
            last_time = float(f_time.read())

        current_time = time.time()
        if current_time - last_time > self.diff:  # need refresh
            need_refresh = True

        if not os.path.exists(TOKEN_PATH):
            need_refresh = True

        if need_refresh:
            with open(TOKEN_TIMESTAMP_PATH, "w") as f:
                f.write(str(time.time()))

            payload = {"corpid": self.corp_id, "corpsecret": self.secret}
            response = requests.get(
                f"{self.qyapi_url}/cgi-bin/gettoken",
                params=payload,
                verify=False,
            )
            response_json = response.json()
            # print response_json
            access_token = response_json.get("access_token")
            if response_json.get("errcode") != 0:
                raise Exception(response_json)

            with open(TOKEN_PATH, "w") as f:
                f.write(access_token)
        else:
            with open(TOKEN_PATH, "r") as f:
                access_token = f.read()
        return access_token

    def send(self, text=None, agentid="", touser="", toparty=""):
        try:
            token = self.refresh_token(agentid)
            payload = {
                "touser": touser,
                "toparty": agentid,
                "msgtype": "text",
                "agentid": agentid,
                "text": {"content": str(text)},
                "safe": "0",
            }
            response = requests.post(
                f"{self.qyapi_url}/cgi-bin/message/send?access_token=" + token,
                json=payload,
                verify=False,
            )
            response_json = response.json()
            if response_json["errcode"] == 0:
                print("success")
            else:
                print("fail")
        except Exception:
            traceback.print_exc()

    def media_upload(
        self, path, type, agentid
    ):  ##上传临时素材 媒体文件类型，分别有图片（image）、语音（voice）、视频（video），普通文件（file）
        token = self.refresh_token(agentid)
        media_url = f"{self.qyapi_url}/cgi-bin/media/upload?access_token={token}&type={type}"
        files = {"media": open(path, "rb")}
        r = requests.post(media_url, files=files)
        print(r.text)
        re = json.loads(r.text)
        # print("media_id: " + re['media_id'])
        return re["media_id"]

    def send_pic(self, path="", agentid="", touser="", toparty=""):
        media_id = self.media_upload(path, "image", agentid)
        token = self.refresh_token(agentid)
        url = f"{self.qyapi_url}/cgi-bin/message/send?access_token={token}"
        data = {
            "touser": touser,
            "toparty": toparty,
            "msgtype": "image",
            "agentid": agentid,
            "image": {"media_id": media_id},
            "safe": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800,
        }
        response = requests.post(url=url, data=json.dumps(data))
        response_json = response.json()
        print(response_json)
        if response_json["errcode"] == 0:
            print("success")
        return response_json


if __name__ == "__main__":
    import os

    corp_id = os.environ["QYWEIXIN_CORP_ID"] = ""
    secret = os.environ["QYWEIXIN_SECRET"] = ""
    qyweixin_client = QyWeixinClient(corp_id, secret)

    qyweixin_client.send(text="测试消息")
