# Created on: 2021/3/11 11:11
# Email: lijicong@163.com
# desc
import base64
import hashlib

import requests
from retry import retry


def send_markdown(key, content, mentioned_list=None):
    if mentioned_list is None:
        mentioned_list = []
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        },
    }
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    res = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    if res.json().get("errcode") == 45009:  # 接口调用超过限制
        raise ValueError(res.text)
    elif res.json().get("errcode") != 0:
        data = {
            "msgtype": "text",
            "text": {
                "content": res.json().get("errmsg", ""),
                "mentioned_list": mentioned_list,
            },
        }
        requests.post(url, json=data, headers={"Content-Type": "application/json"})
    else:
        print(res.text)
    return res.json()


@retry(tries=2, delay=60)
def send_text(key, content, mentioned_list=None):
    if mentioned_list is None:
        mentioned_list = []
    data = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": mentioned_list,
        },
    }
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    res = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    if res.json().get("errcode") == 45009:  # 接口调用超过限制
        raise ValueError(res.text)
    elif res.json().get("errcode") != 0:
        data = {
            "msgtype": "text",
            "text": {
                "content": res.json().get("errmsg", ""),
                "mentioned_list": mentioned_list,
            },
        }
        requests.post(url, json=data, headers={"Content-Type": "application/json"})
    else:
        print(res.text)
    return res.json()


@retry(tries=2, delay=60)
def send_img(key, md5, base64_data):
    data = {"msgtype": "image", "image": {"base64": base64_data, "md5": md5}}
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    res = requests.post(url, json=data, headers={"Content-Type": "text/plain"})
    if res.json().get("errcode") == 45009:  # 接口调用超过限制
        raise ValueError(res.text)
    elif res.json().get("errcode") != 0:
        data = {
            "msgtype": "text",
            "text": {
                "content": res.json().get("errmsg", ""),
                "mentioned_list": ["@all"],
            },
        }
        requests.post(url, json=data, headers={"Content-Type": "application/json"})
    else:
        print(res.text)
    return res.json()


@retry(tries=2, delay=60)
def upload_media(key, file_name, data):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file"
    res = requests.post(url, files={"image": (file_name, data)})
    if res.json().get("errcode") == 45009:  # 接口调用超过限制
        raise ValueError(res.text)
    elif res.json().get("errcode") != 0:
        data = {
            "msgtype": "text",
            "text": {
                "content": res.json().get("errmsg", ""),
                "mentioned_list": ["@all"],
            },
        }
        requests.post(url, json=data, headers={"Content-Type": "application/json"})
    else:
        print(res.text)
    return res.json()


@retry(tries=2, delay=60)
def send_file(key, media_id):
    data = {"msgtype": "file", "file": {"media_id": media_id}}
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    res = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    if res.json().get("errcode") == 45009:  # 接口调用超过限制
        raise ValueError(res.text)
    elif res.json().get("errcode") != 0:
        data = {
            "msgtype": "text",
            "text": {
                "content": res.json().get("errmsg", ""),
                "mentioned_list": ["@all"],
            },
        }
        requests.post(url, json=data, headers={"Content-Type": "application/json"})
    else:
        print(res.text)
    return res.json()


if __name__ == "__main__":
    # content = """
    # 你好，这是一条测试消息
    # """
    # send_text("d94aa6fc-1ee7-4515-8704-54aec79a2a68", content, ["@all"])

    # 发送markdow
    # content = """
    #     实时新增用户反馈<font color=\"warning\">132例</font>，请相关同事注意。\n
    #      >类型:<font color=\"comment\">用户反馈</font>
    #      >普通用户反馈:<font color=\"comment\">117例</font>
    #      >VIP用户反馈:<font color=\"comment\">15例</font>
    # """
    # send_markdown("d94aa6fc-1ee7-4515-8704-54aec79a2a68", content, ["@all"])

    # 发送图片
    file_path = "data/test.png"
    with open(file_path, "rb") as file:
        data = file.read()
        # 转换图片成base64格式
        encodestr = base64.b64encode(data)
        base64_data = str(encodestr, "utf-8")

        # 计算图片的MD5值
        md = hashlib.md5()
        md.update(data)
        md5 = md.hexdigest()

    send_img("d94aa6fc-1ee7-4515-8704-54aec79a2a68", md5, base64_data)
