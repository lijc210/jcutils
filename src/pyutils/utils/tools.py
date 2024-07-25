"""
Created on 2016/5/10
@author: lijc210@163.com
Desc: 功能描述。
https://docs.guandata.com/?g=Doc&m=Article&a=index&id=1&aid=user-api
"""

import json
import time
from concurrent import futures

import requests

from src.api.config import CONFIG

token = CONFIG.SHENCE_API_SECRET
user_token = CONFIG.GUANYUAN_USER_TOKEN
databi_url = CONFIG.DATABI_URL

max_workers = 1
user_group_set = {"店驰加盟商", "店驰全国", "店驰省份", "店驰城市经理", "店驰公司绩效"}


def shence_transform(payload):
    res = requests.post(
        CONFIG.SHENCE_URL + f"/api/events/report?token={token}&project=production",
        json=payload,
    )
    res_dict = res.json()
    field_name = []
    name_list = [adict["name"] for adict in payload["measures"]]
    by_fields = [field.split(".")[-1] for field in payload["by_fields"]]
    field_name.extend(by_fields)
    field_name.extend(name_list)
    rows = res_dict["detail_result"]["rows"]
    items = []
    unit = payload["unit"]
    if unit == "hour":
        series = res_dict["detail_result"]["series"]
        series = [x[5:13] for x in series]
        total = len(name_list)
        series.insert(0, "指标")
        for row in rows:
            values = row["values"]
            values.insert(0, name_list)
            for i, _name in enumerate(name_list):
                adict = {}
                for j, field in enumerate(series):
                    value_list = values[j]
                    adict[field] = value_list[i]
                items.append(adict)
    else:
        total = res_dict["detail_result"]["total_rows"]
        for row in rows:
            # print(json.dumps(row))
            value_list = []
            values = row["values"][0]
            by_values = row["by_values"]
            value_list.extend(by_values)
            value_list.extend(values)
            adict = dict(zip(field_name, value_list, strict=True))
            items.append(adict)
    data = {"total": total, "items": items}
    return data


def users_modify(users):
    # 批量更新用户
    data_dict = {"token": user_token, "userPropertyType": 1, "users": users}
    response = requests.post(f"{databi_url}/public-api/users/modify", json=data_dict)
    result = response.json()["result"]
    if result == "fail":
        raise (ValueError(response.text))
    msg2 = response.json()["response"]
    return msg2


def del_user_groups_func(data_dict):
    print("更新组")
    loginId = data_dict["loginId"]

    # 通过指定的用户的loginid查询对应的uid
    adict = {"token": data_dict["token"], "loginId": loginId}
    response = requests.post(f"{databi_url}/public-api/user/info", json=adict)
    result = response.json()["result"]
    if result == "fail":
        raise (ValueError(response.text))
    uId = response.json()["response"]["uId"]

    # 获取用户组
    bdict = {"token": data_dict["token"]}
    response = requests.post(f"{databi_url}/public-api/user/{uId}/groups", json=bdict)
    print(f"{databi_url}/public-api/user/{loginId}/groups")
    result = response.json()["result"]
    if result == "fail":
        raise (ValueError(response.text))
    # print(response.text)
    response = response.json()["response"]
    ugIds = [row["ugId"] for row in response if row["name"] in user_group_set]

    # 删除用户组
    cdict = {
        "token": data_dict["token"],
        "loginId": data_dict["loginId"],
        "ugIds": ugIds,
        "isExternal": False,
    }
    # print(cdict)
    response = requests.post(
        f"{databi_url}/public-api/user/remove-from-groups", json=cdict
    )
    result = response.json()["result"]
    if result == "fail":
        raise (ValueError(response.text))
    return response


def users_create(users, update=True):
    # 创建观远账号
    # 判断是否存在，存在就更新（覆盖组与用户信息），不存在就创建
    users_list = [user["loginId"] for user in users]
    data_dict = {"token": user_token, "users": users_list}

    response = requests.post(f"{databi_url}/public-api/users/get", json=data_dict)
    # print(response.text)
    result = response.json()["result"]
    if result == "fail":
        raise (ValueError(response.text))
    userExist = response.json()["response"]["userExist"]
    userExistSet = set(userExist)
    # print(userExistSet)

    add_users = []
    modify_users = []
    add_to_groups = []
    for user in users:
        if user["loginId"] not in userExistSet:
            add_users.append(user)
        else:
            modify_users.append(user)
            add_to_groups.append(
                {
                    "token": user_token,
                    "loginId": user["loginId"],
                    "ugIds": user["userGroupIds"],
                    "isExternal": True,
                }
            )

    # print(add_users)
    # print(modify_users)

    # 新增（只有新增接口，才能添加进组）
    data_dict = {"token": user_token, "userPropertyType": 1, "users": add_users}

    response = requests.post(f"{databi_url}/public-api/users/add", json=data_dict)
    result = response.json()["result"]
    if result == "fail":
        message = response.json()["error"]["message"]
        if "bindKey already exists" not in message:
            raise (ValueError(response.text))
    msg1 = response.json()["response"]

    # 更新用户
    msg2 = "update=False， 不更新用户"
    if update:
        data_dict = {"token": user_token, "userPropertyType": 1, "users": modify_users}
        response = requests.post(
            f"{databi_url}/public-api/users/modify", json=data_dict
        )
        result = response.json()["result"]
        if result == "fail":
            raise (ValueError(response.text))
        msg2 = response.json()["response"]

        # 清空用户组
        with futures.ThreadPoolExecutor(max_workers) as executor:
            res = executor.map(del_user_groups_func, add_to_groups)
        for r in res:
            print(r.text)

        # 将用户添加至用户组
        def add_to_groups_func(data_dict):
            time.sleep(0.5)
            response = requests.post(
                f"{databi_url}/public-api/user/add-to-groups", json=data_dict
            )
            result = response.json()["result"]
            if result == "fail":
                raise (ValueError(response.text))
            return response

        with futures.ThreadPoolExecutor(max_workers) as executor:
            res = executor.map(add_to_groups_func, add_to_groups)
        for r in res:
            print(r.text)

    return msg1 + "，" + msg2


def users_update(users, cover_shopcode=False):
    # 创建观远账号
    # 判断是否存在，存在就更新（合并组与用户信息），不存在就创建
    users_list = [user["loginId"] for user in users]
    data_dict = {"token": user_token, "users": users_list}

    response = requests.post(f"{databi_url}/public-api/users/get", json=data_dict)
    # print(response.text)
    result = response.json()["result"]
    if result == "fail":
        raise (ValueError(response.text))
    userExist = response.json()["response"]["userExist"]
    userExistSet = set(userExist)
    # print(userExistSet)

    add_users = []
    modify_users = []
    add_to_groups = []
    for user in users:
        if user["loginId"] not in userExistSet:
            add_users.append(user)
        else:
            modify_users.append(user)
            add_to_groups.append(
                {
                    "token": user_token,
                    "loginId": user["loginId"],
                    "ugIds": user["userGroupIds"],
                    "isExternal": True,
                }
            )

    # print(add_users)
    # print(modify_users)

    # 新增（只有新增接口，才能添加进组）
    data_dict = {"token": user_token, "userPropertyType": 1, "users": add_users}

    response = requests.post(f"{databi_url}/public-api/users/add", json=data_dict)
    result = response.json()["result"]
    if result == "fail":
        raise (ValueError(response.text))
    msg1 = response.json()["response"]

    for modify_user in modify_users:
        loginId = modify_user["loginId"]
        # 获取用户信息
        adict = {"token": data_dict["token"], "loginId": loginId}
        response = requests.post(f"{databi_url}/public-api/user/info", json=adict)
        result = response.json()["result"]
        if result == "fail":
            raise (ValueError(response.text))
        res_dict = response.json()["response"]
        userProperties = res_dict["userProperties"]
        role_old = res_dict["role"][0]
        province_old = userProperties.get(
            "1f07a04c-20b2-3c66-5d70-8dbeca2bb831", ""
        ).replace("省", "")
        city_old = userProperties.get(
            "efda09a2-edb1-3cb8-cb8c-52c6ba5d8428", ""
        ).replace("市", "")
        code_old = userProperties.get("e16cc2b4-fa72-70ce-f1ed-ffcc22aeff4b", "")
        province = modify_user["userDefinedProperties"]["省份"]
        city = modify_user["userDefinedProperties"]["城市"]
        code = modify_user["userDefinedProperties"]["门店"]
        modify_user["userDefinedProperties"]["省份"] = ",".join(
            set(
                list(filter(None, province_old.split(",")))
                + list(filter(None, province.split(",")))
            )
        )

        modify_user["userDefinedProperties"]["城市"] = ",".join(
            set(
                list(filter(None, city_old.split(",")))
                + list(filter(None, city.split(",")))
            )
        )

        if cover_shopcode:  # 覆盖
            modify_user["userDefinedProperties"]["门店"] = ",".join(
                set(filter(None, code.split(",")))
            )
        else:  # 合并
            modify_user["userDefinedProperties"]["门店"] = ",".join(
                set(
                    list(filter(None, code_old.split(",")))
                    + list(filter(None, code.split(",")))
                )
            )

        modify_user["role"] = role_old
    #     print(res_dict)
    #     print(modify_user)
    # print(modify_users)

    # 更新用户
    data_dict = {"token": user_token, "userPropertyType": 1, "users": modify_users}
    response = requests.post(f"{databi_url}/public-api/users/modify", json=data_dict)
    result = response.json()["result"]
    if result == "fail":
        raise (ValueError(response.text))
    msg2 = response.json()["response"]

    # 将用户添加至用户组
    def add_to_groups_func(data_dict):
        response = requests.post(
            f"{databi_url}/public-api/user/add-to-groups", json=data_dict
        )
        result = response.json()["result"]
        if result == "fail":
            raise (ValueError(response.text))
        return response

    with futures.ThreadPoolExecutor(max_workers) as executor:
        res = executor.map(add_to_groups_func, add_to_groups)
    for r in res:
        print(r.text)

    return msg1 + "，" + msg2


if __name__ == "__main__":
    payload = """{
        "measures": [
            {"event_name": "$MPLaunch", "aggregator": "unique", "name": "小程序启动的用户数"},
            {"event_name": "$MPLaunch", "aggregator": "general", "name": "小程序启动的总次数"},
            {
                "event_name": "$MPLaunch",
                "aggregator": "unique",
                "name": "首次访问UV",
                "editName": "首次访问UV",
                "filter": {
                    "conditions": [
                        {
                            "field": "event.$Anything.$is_first_time",
                            "function": "isTrue",
                            "params": [],
                            "$$searchValue": "是否",
                            "functionsOpen": true,
                            "$$render_index": 0,
                        }
                    ]
                },
            },
            {
                "event_name": "$MPLaunch",
                "aggregator": "general",
                "name": "首次访问PV",
                "editName": "首次访问PV",
                "filter": {
                    "conditions": [
                        {
                            "field": "event.$Anything.$is_first_time",
                            "function": "isTrue",
                            "params": [],
                            "$$searchValue": "是否",
                            "functionsOpen": true,
                            "$$render_index": 0,
                        }
                    ]
                },
            },
        ],
        "from_date": "2022-09-28 00:00:00",
        "to_date": "2022-09-28 23:59:59",
        "unit": "hour",
        "by_fields": [],
        "detail_and_rollup": true,
        "enable_detail_follow_rollup_by_values_rank": true,
        "sub_task_type": "SEGMENTATION",
        "time_zone_mode": "",
        "server_time_zone": "",
        "include_today": true,
        "chartType": "line",
        "compareKey": "",
    }"""
    payload = json.loads(payload)
    data = shence_transform(payload)
    print(json.dumps(data, ensure_ascii=False))
