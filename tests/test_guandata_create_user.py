import json

from src.pyutils.utils.tools import user_token, users_create

if __name__ == "__main__":
    user = {
        "name": "nameA",  # 必填，用户登录后显示名称
        # 必填，用以在用户界面登录的信息以及通过api管理用户属性的id，
        # 如邮箱、工号、手机号等。如果使用邮箱登录，则此处填写邮箱，和下述email字段并不冲突。
        "loginId": "Id1",
        "password": "",  # SSO登录可不提供该字段信息，密码必须BASE64加密
        "role": "participant",  # 用户角色，目前可支持admin，editor，participant三类
        "email": "sample1@qq.email.com",
        "mobile": "13200000000",
        "enabled": True,  # 用户状态，非必填。布尔值，只能填True和false。True对应“启用”，false对应“禁用”。
        "userGroupIds": ["qb0d53da637bd4599ba6643d"],  # External group ID
        "userDefinedProperties": {
            "企业微信账号": "value2",
            "钉钉账号": "value2",
            "企业微信公司名称": "value2",
            "userMobile": "value2",
            "飞书账号": "value2",
            "关联数据集属性": "value2",
        },  # 观远平台内已经添加的用户属性名称
    }
    users = [user]
    print(json.dumps(users))

    # 新增（只有新增接口，才能添加进组）
    data_dict = {"token": user_token, "userPropertyType": 1, "users": users}

    # response = requests.post(f"{databi_url}/public-api/users/add", json=data_dict)
    # result = response.json()["result"]
    # if result == "fail":
    #     raise(ValueError(response.text))
    # msg1 = response.json()["response"]
    # print(msg1)

    # response = requests.post(f"{databi_url}/public-api/users/modify", json=data_dict)
    # result = response.json()["result"]
    # if result == "fail":
    #     raise(ValueError(response.text))
    # msg1 = response.json()["response"]
    # print(msg1)

    msg = users_create(users)
    print(msg)
