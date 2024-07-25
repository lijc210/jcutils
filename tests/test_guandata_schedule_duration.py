"""
@File    :   test_guandata_schedule_duration.py
@Time    :   2021/02/02 09:19:09
@Author  :   lijc210@163.com
@Desc    :   检测观远订阅的耗时情况
"""

import codecs
import csv
import datetime
import os

import requests

from src.api.config import CONFIG
from src.api.logger import logger
from src.pyutils.utils.datetime_ import day_now, day_ops

# from src.pyutils.utils.work_weixin_bot import send_text

databi_url = CONFIG.DATABI_URL
event_descriptions = {
    "ETL_COMBINED": "智能ETL运行",
    "ETL_PREVIEW_WRAPPER": "智能ETL预览",
    "CARD_DATA_FROM_DB": "获取直连卡片数据",
    "CARD_DATA_FROM_CASSANDRA": "获取Guan-Index卡片数据",
    "UPDATE_DIRECT_DATASOURCE": "更新直连数据集",
    "UPDATE_DIRECT_DB_DATASOURCE_NEW": "更新直连数据集",
    "GUANINDEX": "更新Guan-Index数据集",
    "UPDATE_EXTRACT_DB_DATASOURCE_NEW": "更新Guan-Index数据集",
    "ACCOUNT_DS": "更新账户数据集",
    "SPARK_HIVE": "更新spark-hive数据集",
    "WEB_SERVICE": "更新Web Service数据集",
    "CARD_IMAGE_EXPORT": "图片导出",
    "PAGEPDF_IMAGE_EXPORT": "PDF导出",
    "FILE_IMPORT": "文件导入",
    "FILE_EXPORT": "文件导出",
    "FILE_EXPORT_COMBINED": "批量卡片导出",
    "COMPLEX_REPORT_GENERATE": "中国式报表生成",
    "COMPLEX_REPORT_EXPORT": "中国式报表导出",
    "COMPLEX_REPORT_PRO_GENERATE": "中国式报表Pro生成",
    "COMPLEX_REPORT_PRO_EXPORT": "中国式报表Pro导出",
    "GET_DIRECT_DS_ROWCOUNT": "直连数据集获取行数",
    "DATASOURCE_CLEARING": "数据清理",
    "DATASOURCE_CHANGING_PRIMARYKEYS": "数据集更换主键",
    "CLICKHOUSE_ACC": "数据集加速",
    "CARD_RESULT_STORE": "卡片分析结果存储",
    "GUANINDEX_WITH_FILE": "文件方式更新Guan-Index数据集",
    "AUGMENTED_ANALYSIS": "增强分析运行",
    "DATASET_PREVIEW": "数据集预览",
    "DATA_EXPLAIN": "数据解释运行",
    "SECOND_DATA_EXPLAIN": "数据解释二次下钻",
    "CARD_BATCH_EXPORT": "批量导出EXCEL",
    "DATA_WRITE_BACK": "数据回写运行",
    "INTELLIGENT_INSIGHT": "获取规则洞察卡片数据",
    "RESOURCE_EXPORT": "资源导出",
    "RESOURCE_IMPORT": "资源导入",
    "COMPLEX_REPORT_DATA_WRITE": "填报数据回写",
    "CARD_DATASET": "更新卡片数据集",
}


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


def task_detail():
    token = get_token()
    url = f"{databi_url}/api/task/guandata/history/details"
    adict = {
        "userName": "自动更新",
        "startTime": "2024-07-01 09:00:00",
        "endTime": "2024-07-01 09:01:00",
    }
    headers = {"X-Auth-Token": token}
    r = requests.post(url, json=adict, headers=headers)
    # print(r.text)
    res_list = r.json()
    print(len(res_list))
    return res_list


def task_hour_detail():
    # 指定开始时间和结束时间
    start_time = datetime.datetime(2024, 7, 1, 0, 0, 0)
    end_time = datetime.datetime(2024, 7, 1, 10, 0, 0)

    # 当前时间初始化为开始时间
    current_time = start_time

    data_list = []
    # 遍历每小时
    while current_time <= end_time:
        print(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        current_time += datetime.timedelta(hours=1)
        startTime = current_time.strftime("%Y-%m-%d %H:00:00")
        endTime = (current_time + datetime.timedelta(hours=1)).strftime(
            "%Y-%m-%d %H:00:00"
        )
        print(startTime, endTime)

        token = get_token()
        url = f"{databi_url}/api/task/guandata/history/details"
        adict = {"userNameLike": "自动更新", "startTime": startTime, "endTime": endTime}
        headers = {"X-Auth-Token": token}
        r = requests.post(url, json=adict, headers=headers)
        print(r.text)
        res_list = r.json()
        data_list.extend(res_list)
        break
    return data_list


def check(start_time, end_time):
    data_list = [["操作对象", "类型", "用户", "耗时", "运行时间", "完成时间"]]
    # 获取任务耗时
    res_list = task_detail()

    for adict in res_list:
        # print(adict)
        objectName = adict.get("objectName", "")
        type = adict.get("type", "")
        userName = adict.get("userName", "")
        duration = adict.get("duration", "")
        runningTime = adict.get("runningTime", "")
        finishedTime = adict.get("finishedTime", "")
        data_list.append(
            [objectName, type, userName, duration, runningTime, finishedTime]
        )

    file_path = os.path.join(CONFIG.TEMP_DIR, "schedule_duration.csv")
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
