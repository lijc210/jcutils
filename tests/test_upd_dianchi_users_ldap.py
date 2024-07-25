"""
@File    :   upd_weather.py
@Time    :   2021/02/02 09:19:09
@Author  :   lijc210@163.com
@Desc    :
"""

import requests

from src.api.config import CONFIG
from src.api.conn_pool import apocalypse_client as mysql_client
from src.api.conn_pool import ecology_client

token = CONFIG.SHENCE_API_SECRET
user_token = CONFIG.GUANYUAN_USER_TOKEN
databi_url = CONFIG.DATABI_URL


def get_user_dict(employee_no):
    sql = f"select * from hrmresource where workcode = '{employee_no}'"
    # print(sql)
    res = ecology_client.query(sql)
    user_dict = {}
    if res:
        user_dict = res[0]
    # print(user_dict)
    return user_dict


sql = """select *  from upd_dianchi_users
where employee_no is not null and employee_no !='' and group_name ='店驰城市经理'
and status ='enable'
and shop_code !='' and shop_code is not null
"""
print(sql)
res = mysql_client.query(sql)
users = []
for i, row in enumerate(res):
    # print(row)
    employee_no = row["employee_no"]
    user_dict = get_user_dict(employee_no)
    if not user_dict:
        print("user_dict为空")
        continue
    LASTNAME = user_dict["LASTNAME"]
    LOGINID = user_dict["LOGINID"]
    EMAIL = user_dict["EMAIL"]
    MOBILE = user_dict["MOBILE"]
    if not LOGINID:
        LOGINID = EMAIL.replace("@guoquan.cn", "")
    row["nick_name"] = LASTNAME
    row["user_name"] = LOGINID
    row["email"] = EMAIL
    row["phone_no"] = MOBILE
    row["code"] = row["shop_code"]

    # 获取用户信息
    adict = {"token": user_token, "loginId": LOGINID}
    res = requests.post(f"{databi_url}/public-api/user/info", json=adict)
    res_dict = res.json()
    # print(res_dict)
    response = res_dict["response"]
    userProperties = response.get("userProperties")
    update = False
    if userProperties:
        p = userProperties["1f07a04c-20b2-3c66-5d70-8dbeca2bb831"]
        c = userProperties["efda09a2-edb1-3cb8-cb8c-52c6ba5d8428"]
        code = userProperties["e16cc2b4-fa72-70ce-f1ed-ffcc22aeff4b"]
        pl = []
        for x in p.split(","):
            x2 = (
                x.replace("新疆维吾尔自治区", "新疆")
                .replace("内蒙古自治区", "内蒙古")
                .replace("宁夏回族自治区", "宁夏")
                .replace("广西壮族自治区", "广西")
            )
            x2 = x2.replace("市", "")
            pl.append(x2)
            if len(x) > 3 or "市" in x:
                update = True
        if update:
            # print(res_dict)
            user = {
                "name": response["name"],
                "loginId": response["loginId"],
                "password": "",  # SSO登录可不提供该字段信息，密码必须BASE64加密
                "role": response["role"][
                    0
                ],  # 用户角色，目前可支持admin，editor，participant三类
                "email": response["email"],
                "mobile": response["mobile"],
                # 用户状态，非必填。布尔值，只能填true和false。true对应“启用”，false对应“禁用”。
                "enabled": True,
                "userDefinedProperties": {
                    "省份": ",".join(pl),
                    "城市": c,
                    "门店": code,
                },
            }
            # print(user)
            # 更新用户
            data_dict = {"token": user_token, "userPropertyType": 1, "users": [user]}
            response = requests.post(
                f"{databi_url}/public-api/users/modify", json=data_dict
            )
            result = response.json()["result"]
            print(i, result, LOGINID, p)
            # print(result)
            # break


if __name__ == "__main__":
    pass
