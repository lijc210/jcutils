"""
Created on 2017/6/15 0015
@author: lijc210@163.com
Desc: 功能描述。
"""

import json
import os
import sys
import time
import traceback
import warnings

import requests

warnings.filterwarnings("ignore")


class Weixin:
    """
    save corp_id, secret
    save token and refresh every 7200 Seconds

    #企业号开发者平台，发送消息文档
    http://qydev.weixin.qq.com/wiki/index.php?title=%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F
    """

    URL_GET_TOKEN = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"  # get method, 1)corpid,2)corpsecret
    # access_token=ACCESS_TOKEN, post method
    URL_SEND_MSG = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
    TOKEN_COTENT = ".TOKEN_CONTENT"
    TOKEN_TIMESTAMP = ".TOKEN_TIMESTAMP"

    def __init__(self, corp_id, secret):
        self.corp_id = corp_id
        self.secret = secret
        self.diff = 7000

    def send(self, text=None, agentid="", touser="", toparty=""):
        try:
            token = self.refresh_token(self.corp_id, self.secret, agentid)
            payload = {
                "touser": touser,
                "toparty": agentid,
                "msgtype": "text",
                "agentid": agentid,
                "text": {"content": str(text)},
                "safe": "0",
            }
            response = requests.post(self.URL_SEND_MSG + token, json=payload, verify=False)
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
        token = self.refresh_token(self.corp_id, self.secret, agentid)
        media_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type={type}"
        files = {"media": open(path, "rb")}
        r = requests.post(media_url, files=files)
        print(r.text)
        re = json.loads(r.text)
        # print("media_id: " + re['media_id'])
        return re["media_id"]

    def send_pic(self, path="", agentid="", touser="", toparty=""):
        media_id = self.media_upload(path, "image", agentid)
        token = self.refresh_token(self.corp_id, self.secret, agentid)
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
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

    def refresh_token(self, _corp_id, _secret, agentid):
        print(_secret, agentid)
        self.TOKEN_COTENT_PATH = self.TOKEN_COTENT + str(agentid)
        self.TOKEN_TIMESTAMP_PATH = self.TOKEN_TIMESTAMP + str(agentid)
        last_time = 0
        need_refresh = False
        if os.path.exists(self.TOKEN_TIMESTAMP_PATH):
            f_time = open(self.TOKEN_TIMESTAMP_PATH)
            last_time = float(f_time.read())

        current_time = time.time()
        if current_time - last_time > self.diff:  # need refresh
            need_refresh = True

        if not os.path.exists(self.TOKEN_COTENT_PATH):
            need_refresh = True

        if need_refresh:
            f_time = open(self.TOKEN_TIMESTAMP_PATH, "w")
            f_time.write(str(time.time()))
            f_time.close()

            payload = {"corpid": _corp_id, "corpsecret": _secret}
            response = requests.get(self.URL_GET_TOKEN, params=payload, verify=False)
            response_json = response.json()
            # print response_json

            token = response_json["access_token"]
            f_content = open(self.TOKEN_COTENT_PATH, "w")
            f_content.write(token)
            f_content.close()
        else:
            f_content = open(self.TOKEN_COTENT_PATH)
            token = f_content.read()
            f_content.close()
        return token


if __name__ == "__main__":
    if len(sys.argv) == 2:
        content = sys.argv[1]
    else:
        content = "测试"
    corp_id = ("ww72ecd238ebxxxxxx",)
    secret = ("rmP-6p-DHkMRG8FWioqjtal_bOYKypWcdEhdxxxxxxx",)
    weixin = Weixin(corp_id, secret)
    weixin.send(text=content, agentid=1000003, touser="@all", toparty="1")

    # secret = "Ar8PCuygDR8cKSaQ8d23HkVbPvyYwmqsTNTYpo6p3PE",
    weixin = Weixin(corp_id, secret)
    weixin.send_pic(path="D:\\1.jpg", agentid=1000003, touser="@all", toparty="1")
