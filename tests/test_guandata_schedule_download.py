"""
@File    :   check_guandata_schedule.py
@Time    :   2021/02/02 09:19:09
@Author  :   lijc210@163.com
@Desc    :   检测观远订阅是否过于集中
"""

import codecs
import csv
import os

import requests

from src.api.config import CONFIG
from src.api.logger import logger
from src.pyutils.utils.datetime_ import day_now, day_ops

# from src.pyutils.utils.work_weixin_bot import send_text

databi_url = CONFIG.DATABI_URL


def get_token():
    data = {"domain": "guanbi", "email": "xuanji-api", "password": "U3lzejAyMTA="}
    r = requests.post(
        CONFIG.XUANJI_URL + "/api/v1/instant/function/sign-in",
        json=data,
    )
    # print(r.text)
    res = r.json()
    token = res.get("data", {}).get("token", "")
    return token


def check_curd(start_time, end_time):
    schedule_tyep = "卡片订阅"
    token = get_token()
    url = f"{databi_url}/api/schedule/CARD"
    adict = {"scType": "CARD", "offset": 0, "limit": 10000, "qEnabled": "enabled"}
    headers = {"X-Auth-Token": token}
    r = requests.post(url, json=adict, headers=headers)
    # print(r.text)
    res_dict = r.json()
    schedules = res_dict["schedules"]
    print(schedule_tyep, len(schedules))
    data_list = []
    for i, schedule in enumerate(schedules):
        # print(json.dumps(schedule, ensure_ascii=False))
        name = schedule["name"]
        triggerType = schedule["triggerType"]
        if triggerType == "CRON":
            resourceName = schedule["resourceName"]
            lastSendTime = schedule.get("lastSendTime", "")
            creator_name = schedule["creator"]["name"]
            cron_type = schedule["cron"]["cronType"]
            cron_value = schedule["cron"]["value"]
            alist = [
                schedule_tyep,
                name,
                resourceName,
                creator_name,
                cron_type,
                cron_value,
                lastSendTime,
            ]
            data_list.append(alist)
    # print(data_list)
    return data_list


def check_multi_curd(start_time, end_time):
    schedule_tyep = "合并订阅"
    token = get_token()
    url = f"{databi_url}/api/schedule/MULTI_CARD"
    adict = {"scType": "MULTI_CARD", "offset": 0, "limit": 10000, "qEnabled": "enabled"}
    headers = {"X-Auth-Token": token}
    r = requests.post(url, json=adict, headers=headers)
    # print(r.text)
    res_dict = r.json()
    schedules = res_dict["schedules"]
    print(schedule_tyep, len(schedules))
    data_list = []
    for i, schedule in enumerate(schedules):
        name = schedule["name"]
        triggerType = schedule["triggerType"]
        if triggerType == "CRON":
            resourceName = schedule.get("resourceName", "")
            lastSendTime = schedule.get("lastSendTime", "")
            creator_name = schedule["creator"]["name"]
            cron_type = schedule["cron"]["cronType"]
            cron_value = schedule["cron"]["value"]
            alist = [
                schedule_tyep,
                name,
                resourceName,
                creator_name,
                cron_type,
                cron_value,
                lastSendTime,
            ]
            data_list.append(alist)
    # print(data_list)
    return data_list


def check_page(start_time, end_time):
    schedule_tyep = "页面订阅"
    token = get_token()
    url = f"{databi_url}/api/schedule/PAGE"
    adict = {"scType": "PAGE", "offset": 0, "limit": 10000, "qEnabled": "enabled"}
    headers = {"X-Auth-Token": token}
    r = requests.post(url, json=adict, headers=headers)
    # print(r.text)
    res_dict = r.json()
    schedules = res_dict["schedules"]
    print(schedule_tyep, len(schedules))
    data_list = []
    for i, schedule in enumerate(schedules):
        name = schedule["name"]
        triggerType = schedule["triggerType"]
        if triggerType == "CRON":
            resourceName = schedule["resourceName"]
            lastSendTime = schedule.get("lastSendTime", "")
            creator_name = schedule["creator"]["name"]
            cron_type = schedule["cron"]["cronType"]
            cron_value = schedule["cron"]["value"]
            alist = [
                schedule_tyep,
                name,
                resourceName,
                creator_name,
                cron_type,
                cron_value,
                lastSendTime,
            ]
            data_list.append(alist)
    # print(data_list)
    return data_list


def check(start_time, end_time):
    data_list = [
        [
            "类型",
            "订阅名称",
            "资源名称",
            "创建人",
            "触发方式",
            "定时时间",
            "最后发送时间",
        ]
    ]
    list1 = check_curd(start_time, end_time)
    list2 = check_multi_curd(start_time, end_time)
    list3 = check_page(start_time, end_time)
    data_list.extend(list1)
    data_list.extend(list2)
    data_list.extend(list3)

    # new_list = []
    # for schedule_tyep, name, creator_name, cron_type, cron_value in data_list:
    #     print(schedule_tyep, name, creator_name, cron_type, cron_value)
    file_path = os.path.join(CONFIG.TEMP_DIR, "schedule.csv")
    with codecs.open(file_path, "wb", "gbk") as csvfile:
        spamwriter = csv.writer(csvfile)
        # spamwriter.writerows(date_list)
        for row in data_list:
            spamwriter.writerow(row)

    # with open(file_path, "w", newline="") as csvfile:
    #     spamwriter = csv.writer(csvfile)
    #     # spamwriter.writerows(date_list)
    #     for row in data_list:
    #         spamwriter.writerow(row)


def process():
    # 需要修改的参数
    dtime = day_now(outfmt="%Y-%m-%d %H:00:00")
    start_time = day_ops(days=-1, outfmt="%Y-%m-%d 00:00:00")
    end_time = day_now(outfmt="%Y-%m-%d 00:00:00")
    check(start_time, end_time)
    logger.info(dtime + "    " + "成功")


def main():
    process()


if __name__ == "__main__":
    main()
