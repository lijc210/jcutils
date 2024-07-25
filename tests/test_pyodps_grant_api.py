"""
@File    :   test_pyodps.py
@Time    :   2021/02/02 10:35:06
@Author  :   lijc210@163.com
@Desc    :   https://help.aliyun.com/document_detail/27935.html

            use data_kezhi;
            list users;
            show grants for RAM$锅圈供应链上海有限公司:lijicong;
            grant role_project_erd to RAM$锅圈供应链上海有限公司:lijicong;
            grant All  ON project data_kezhi TO RAM$锅圈供应链上海有限公司:lijicong;

            grant role_project_guest,role_project_data_analyst to RAM$锅圈供应链上海有限公司:lijiahui;

            describe role role_project_data_analyst;
            grant CreateTable on project data_kezhi to ROLE role_project_data_analyst;

            create or replace view data_kezhi.view_dwd_ws_customer_group_user_liruipeng as
            select * from data_kezhi.dwd_ws_customer_group_user
            where dt='20231129' and owner='13523002741'

            grant Describe , Select  ON TABLE data_kezhi.view_dwd_ws_customer_group_user_liruipeng TO RAM$锅圈供应链上海有限公司:liruipeng
"""

import json

from odps import ODPS

from src.api.config import CONFIG

# lijicong
# odps = ODPS(CONFIG.ACCESS_ID, CONFIG.ACCESS_KEY,
#  'Data_Kezhi',endpoint='http://service.cn-beijing.maxcompute.aliyun.com/api')

# dataworks


def list_users(odps):
    """
    查看所有用户
    """
    sql = "list users;"
    with odps.execute_sql(sql).open_reader() as reader:
        res = reader.raw
        res_dict = json.loads(res)
        result = res_dict["result"]
        result_dict = json.loads(result)
        print((json.dumps(result_dict, ensure_ascii=False, indent=4)))
        # for record in reader:
        #     print(record)


def show_grants(odps, user):
    """
    查看某个用户的权限
    """
    sql = f"show grants for RAM$锅圈供应链上海有限公司:{user};"
    with odps.execute_sql(sql).open_reader() as reader:
        res = reader.raw
        res_dict = json.loads(res)
        result = res_dict["result"]
        result_dict = json.loads(result)
        print((json.dumps(result_dict, ensure_ascii=False, indent=4)))
        # for record in reader:
        #     print(record)


def grant_role_to_user(odps, user):
    """
    给某个用户授权分析角色
    """
    sql = f"grant role_project_guest,role_project_data_analyst to RAM$锅圈供应链上海有限公司:{user};"
    with odps.execute_sql(sql).open_reader() as reader:
        res = reader.raw
        res_dict = json.loads(res)
        result = res_dict["result"]
        result_dict = json.loads(result)
        print((json.dumps(result_dict, ensure_ascii=False, indent=4)))
        # for record in reader:
        #     print(record)


def describe_role(odps):
    """
    查看角色的权限
    """
    sql = "describe role role_project_data_analyst;"
    with odps.execute_sql(sql).open_reader() as reader:
        res = reader.raw
        res_dict = json.loads(res)
        result = res_dict["result"]
        result_dict = json.loads(result)
        print((json.dumps(result_dict, ensure_ascii=False, indent=4)))
        # for record in reader:
        #     print(record)


def grant_access_to_role(odps):
    """
    给某角色某权限
    """
    sql = "grant CreateTable on project data_kezhi to ROLE role_project_data_analyst;"
    with odps.execute_sql(sql).open_reader() as reader:
        res = reader.raw
        res_dict = json.loads(res)
        result = res_dict["result"]
        result_dict = json.loads(result)
        print((json.dumps(result_dict, ensure_ascii=False, indent=4)))
        # for record in reader:
        #     print(record)


def create_view(odps, user):
    """
    创建视图
    """
    sql = """
    create or replace view data_kezhi.view_dwd_ws_customer_group_user_liruipeng as
    select * from data_kezhi.dwd_ws_customer_group_user
    where dt='20231129' and owner='13523002741'
    """
    with odps.execute_sql(sql).open_reader() as reader:
        res = reader.raw
        res_dict = json.loads(res)
        result = res_dict["result"]
        result_dict = json.loads(result)
        print((json.dumps(result_dict, ensure_ascii=False, indent=4)))


def grant_table_to_user(odps, table_name, user):
    """
    授权某个用户查看表或视图
    """
    sql = f"grant Describe , Select  ON TABLE {table_name} TO RAM$锅圈供应链上海有限公司:{user}"
    with odps.execute_sql(sql).open_reader() as reader:
        res = reader.raw
        res_dict = json.loads(res)
        result = res_dict["result"]
        result_dict = json.loads(result)
        print((json.dumps(result_dict, ensure_ascii=False, indent=4)))


def add_user(odps, user):
    """
    添加用户
    """
    sql = f"add user RAM$锅圈供应链上海有限公司:{user}"
    with odps.execute_sql(sql).open_reader() as reader:
        res = reader.raw
        res_dict = json.loads(res)
        result = res_dict["result"]
        result_dict = json.loads(result)
        print((json.dumps(result_dict, ensure_ascii=False, indent=4)))


def main():
    odps = ODPS(
        CONFIG.ACCESS_ID,
        CONFIG.ACCESS_KEY,
        "Data_Kezhi",
        endpoint="http://service.cn-beijing.maxcompute.aliyun.com/api",
    )
    # # 查看所有用户
    # list_users(odps)
    # 查看某个用户的权限
    show_grants(odps, "lijicong")
    # # 给某个用户授权分析角色
    # grant_role_to_user(odps, "lijicong")
    # # 查看角色的权限
    # describe_role(odps)
    # # 给某角色某权限
    # grant_access_to_role(odps)
    # # 创建视图
    # create_view(odps, "lijicong")
    # # 授权某个用户查看表或视图
    # grant_table_to_user(odps, "data_kezhi.view_dwd_ws_customer_group_user_liruipeng", "lijicong")
    # 添加用户
    add_user(odps, "lijicong")


if __name__ == "__main__":
    main()
