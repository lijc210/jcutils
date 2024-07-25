"""
@File    :   test_pyodps.py
@Time    :   2021/02/02 10:35:06
@Author  :   lijc210@163.com
@Desc    :   None
"""

import os

from odps import ODPS

from src.api.config import CONFIG

# lijicong
# odps = ODPS(CONFIG.ACCESS_ID, CONFIG.ACCESS_KEY,
#  'Data_Kezhi',endpoint='http://service.cn-beijing.maxcompute.aliyun.com/api')

# dataworks
odps = ODPS(
    CONFIG.ACCESS_ID,
    CONFIG.ACCESS_KEY,
    "Data_Kezhi",
    endpoint="http://service.cn-beijing.maxcompute.aliyun.com/api",
)

sql = """
SELECT  unionid
        ,SUBSTR(register_time,1,10) as register_time
        ,first_consume_date
FROM    vip_center.dm_member_info_label
WHERE   dt = '20240118'
AND     SUBSTR(register_time,1,10) BETWEEN '2024-01-11' AND '2024-01-17'
GROUP BY unionid
         ,SUBSTR(register_time,1,10)
         ,first_consume_date
"""

file_path = os.path.join(CONFIG.TEMP_DIR, "dm_member_info_label.xlsx")
print(file_path)
with open(file_path, "w") as f:
    with odps.execute_sql(sql).open_reader() as reader:
        for record in reader:
            f1 = record[0] if record[0] else ""
            f2 = record[1] if record[1] else ""
            f3 = record[2] if record[2] else ""
            atext = f1 + "\t" + f2 + "\t" + f3 + "\n"
            print(atext)
            f.write(atext)
