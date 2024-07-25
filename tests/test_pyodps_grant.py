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

table_list = [
    "data_kezhi.dwd_order_all_channel_detailed",
    "data_kezhi.dwd_order_goods_all_channel_detailed",
    "data_kezhi.ads_sales_inoutstock_shop_item_di",
    "vip_center.ads_member_coupon_used_detail",
    "data_kezhi.ads_report_enter_order_detailed",
    "data_kezhi.ads_member_points_bak",
    "data_kezhi.ads_sc_group_buy_activity_order_info",
    "data_kezhi.ads_gq_sc_activity_lottery_order_info",
    "bas.abs_shangcheng_item_shelves_detailed",
]

table1 = []
table2 = []

for table in table_list:
    sql = f"""desc {table};"""
    # new_shop_dict = defaultdict(list)
    with odps.execute_sql(sql).open_reader() as reader:
        print(reader.raw)
        if " province " in reader.raw:
            table1.append(table)
        else:
            table2.append(table)

print(",".join(table1))
print("#" * 20)
print(",".join(table2))
