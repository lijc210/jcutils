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
create VIEW  table_vs as
select
count(1)
from
data_kezhi.ods_gq_oc_gqsh_order_after_sales_binlogread
where dt='20211102' limit 100;
"""
# new_shop_dict = defaultdict(list)
with odps.execute_sql(sql).open_reader() as reader:
    for record in reader:
        print(record[0])
        print(record)
        # new_shop_dict[record.province].append(record)
# print(new_shop_dict)
