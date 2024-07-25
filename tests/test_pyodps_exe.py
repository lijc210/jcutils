"""
@File    :   test_pyodps.py
@Time    :   2021/02/02 10:35:06
@Author  :   lijc210@163.com
@Desc    :   None
"""

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
grant Describe , Select  ON TABLE ods_gq_oc_gqsh_order_after_sales_binlogread TO RAM$锅圈供应链上海有限公司:luye;
"""
with odps.execute_sql(sql).open_reader() as reader:
    print(dir(reader))
    print(reader.read())
    for record in reader:
        print(record[0])
        print(record)
