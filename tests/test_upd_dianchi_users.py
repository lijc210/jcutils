"""
@File    :   upd_weather.py
@Time    :   2021/02/02 09:19:09
@Author  :   lijc210@163.com
@Desc    :
"""

import requests

from src.api.config import CONFIG
from src.api.conn_pool import apocalypse_client as mysql_client

token = CONFIG.SHENCE_API_SECRET
user_token = CONFIG.GUANYUAN_USER_TOKEN
databi_url = CONFIG.DATABI_URL

sql = """select *  from upd_dianchi_users
where group_name ='店驰城市经理'
and status ='enable'
and user_name like '%dianchi%'
"""
print(sql)
res = mysql_client.query(sql)
users = []
for i, row in enumerate(res):
    user_name = row["user_name"]
    print(i, user_name)
    # 获取用户信息
    adict = {"token": user_token, "loginId": user_name}
    res = requests.post(f"{databi_url}/public-api/user/info", json=adict)
    res_dict = res.json()
    # print(res_dict)
    # break
    response = res_dict["response"]
    userProperties = response.get("userProperties")
    update = False
    if userProperties:
        p = userProperties.get("1f07a04c-20b2-3c66-5d70-8dbeca2bb831")
        c = userProperties.get("efda09a2-edb1-3cb8-cb8c-52c6ba5d8428")
        code = userProperties.get("e16cc2b4-fa72-70ce-f1ed-ffcc22aeff4b")
        if code.startswith(","):
            code = ",".join(list(filter(None, code.split(","))))
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
                "enabled": response["enabled"],
                "userDefinedProperties": {"省份": p, "城市": c, "门店": code},
            }
            # print(user)
            # 更新用户
            data_dict = {"token": user_token, "userPropertyType": 1, "users": [user]}
            response = requests.post(
                f"{databi_url}/public-api/users/modify", json=data_dict
            )
            result = response.json()["result"]
            print(i, user_name, result)
            # break


if __name__ == "__main__":
    pass
