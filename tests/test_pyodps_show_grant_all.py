"""
@File    :   test_pyodps.py
@Time    :   2021/02/02 10:35:06
@Author  :   lijc210@163.com
@Desc    :   None
"""

import codecs
import csv
import os
import re

from odps import ODPS

from src.api.config import CONFIG

# dataworks
odps1 = ODPS(
    CONFIG.ACCESS_ID,
    CONFIG.ACCESS_KEY,
    "Data_Kezhi",
    endpoint="http://service.cn-beijing.maxcompute.aliyun.com/api",
)

odps2 = ODPS(
    CONFIG.ACCESS_ID,
    CONFIG.ACCESS_KEY,
    "vip_center",
    endpoint="http://service.cn-beijing.maxcompute.aliyun.com/api",
)

odps3 = ODPS(
    CONFIG.ACCESS_ID,
    CONFIG.ACCESS_KEY,
    "bas",
    endpoint="http://service.cn-beijing.maxcompute.aliyun.com/api",
)

data_list = [["用户名", "项目名称", "表名"]]

for odps in [odps1, odps2, odps3]:
    sql = "list users;"
    with odps.execute_sql(sql).open_reader() as reader:
        raw = reader.raw
        # 定义正则表达式来匹配表名
        pattern = r'RAM\$锅圈供应链上海有限公司:([^"]+)\\'
        # 使用正则表达式查找所有匹配的表名
        matches = re.findall(pattern, raw)
        # 打印所有匹配的表名
        user_list = []
        for match in matches:
            user_list.append(match)

        print(user_list)
        for user in user_list:
            sql = f"show grants for RAM$锅圈供应链上海有限公司:{user};"
            # print(sql)
            with odps.execute_sql(sql).open_reader() as reader:
                raw = reader.raw
                # print(raw)
                # 定义正则表达式来匹配表名
                pattern = r'acs:odps:\*:projects/([^/]+)/tables/([^"]+)\\'
                # 使用正则表达式查找所有匹配的表名
                matches = re.findall(pattern, raw)
                # 打印所有匹配的表名
                for match in matches:
                    print(user, match)
                    data_list.append([user, match[0], match[1]])
        #     break
        # break


file_path = os.path.join(CONFIG.TEMP_DIR, "show_grant_all.csv")
with codecs.open(file_path, "wb", "gbk") as csvfile:
    spamwriter = csv.writer(csvfile)
    # spamwriter.writerows(date_list)
    for row in data_list:
        spamwriter.writerow(row)
