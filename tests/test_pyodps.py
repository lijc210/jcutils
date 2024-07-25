"""
@File    :   test_pyodps.py
@Time    :   2021/02/02 10:35:06
@Author  :   lijc210@163.com
@Desc    :   None
"""

from collections import defaultdict

from odps import ODPS

from src.api.config import CONFIG

odps = ODPS(
    CONFIG.ACCESS_ID,
    CONFIG.ACCESS_KEY,
    "Data_Kezhi",
    endpoint="http://service.cn-beijing.maxcompute.aliyun.com/api",
)

sql = """
select fnumber,province,shop_name,min_first_saletime
from Data_Kezhi.dim_jd_erp_shop
where min_first_saletime>="2021-02-01" and valid_flag=1
group by fnumber,province,shop_name,min_first_saletime
"""
# new_shop_dict = defaultdict(list)
# with odps.execute_sql(sql).open_reader() as reader:
#     for record in reader:
#         print(record[0])
#         print(record)
#         new_shop_dict[record.province].append(record)
# print(new_shop_dict)


sql = """
show grants for RAM$锅圈供应链上海有限公司:tietuo;
"""
new_shop_dict = defaultdict(list)
with odps.execute_sql(sql).open_reader() as reader:
    for record in reader:
        print(record)
