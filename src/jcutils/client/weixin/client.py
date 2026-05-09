# coding: utf-8
"""
@File    :   weixin_offiaccount.py
@Time    :   2024/01/08 14:31:53
@Author  :   lijc210@163.com
@Desc    :   微信公众号api
"""

import os
import sys
import time
import warnings

import requests

warnings.filterwarnings("ignore")


class WeixinClient:
    """
    微信公众平台开发
    https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
    """

    def __init__(self, appid, secret):
        self.url = "https://api.weixin.qq.com"
        self.appid = appid
        self.secret = secret
        self.expired_time = 7200
        self.token_path = ".WeixinOffiaccount" + appid

    def get_token(self):
        # 获取当前时间
        current_time = time.time()
        if os.path.exists(self.token_path) and current_time - os.path.getmtime(self.token_path) < self.expired_time:
            with open(self.token_path, "r") as f:
                token = f.read()
        else:
            url = f"{self.url}/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.secret}"
            response = requests.get(url, verify=False)
            response_json = response.json()
            if "access_token" in response_json:
                token = response_json["access_token"]
                with open(self.token_path, "w") as f:
                    f.write(token)
            else:
                raise Exception("get token error:{}".format(response_json))
        return token

    def menu_create(self):
        token = self.get_token()
        url = f"{self.url}/cgi-bin/menu/create?access_token={token}"
        data = {
            "button": [
                {"type": "click", "name": "今日歌曲", "key": "V1001_TODAY_MUSIC"},
                {
                    "name": "菜单",
                    "sub_button": [
                        {"type": "view", "name": "搜索", "url": "http://www.soso.com/"},
                        {
                            "type": "miniprogram",
                            "name": "wxa",
                            "url": "http://mp.weixin.qq.com",
                            "appid": "wx286b93c14bbf93aa",
                            "pagepath": "pages/lunar/index",
                        },
                        {"type": "click", "name": "赞一下我们", "key": "V1001_GOOD"},
                    ],
                },
            ]
        }
        response = requests.post(url, json=data)
        print(response.text)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        content = sys.argv[1]
    else:
        content = "测试"
    # 测试
    appid = "wx2512d0f2fssfsf64"
    secret = "782cce1b848251sfsfsfsfd5035c"

    # 音频搜索
    appid = "wx58ffsfsfsfsf190"
    secret = "f32e23d1863a5f298fsfsfs3d0d50"
    weixin = WeixinClient(appid, secret)
    weixin.menu_create()
