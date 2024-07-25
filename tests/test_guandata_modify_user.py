def test_guandata_modify_user():
    pass

    # users_list = [user[1] for user in alllist]
    # data_dict = {
    #     "token": user_token,
    #     "users": users_list
    # }

    # response = requests.post(
    #     f"{databi_url}/public-api/users/get", json=data_dict)
    # print(response.text)
    # # result = response.json()["result"]

    # modify_users = []
    # for alist in alllist:
    #     print(alist)
    #     user = {
    #         # 必填，用以在用户界面登录的信息以及通过api管理用户属性的id，如邮箱、工号、手机号等。
    #         # 如果使用邮箱登录，则此处填写邮箱，和下述email字段并不冲突。
    #         "loginId": alist[0],
    #         "userGroupIds": ["o8a00a053c2134824bfd58a1"],
    #         "userDefinedProperties": {
    #             "企业微信账号": alist[1],
    #             "省份":alist[2]
    #         }
    #     }
    #     modify_users.append(user)
    #     break

    # data_dict = {
    #     "token": user_token,
    #     "userPropertyType": 1,
    #     "users": modify_users
    # }
    # response = requests.post(
    #     f"{databi_url}/public-api/users/modify", json=data_dict)
    # result = response.json()["result"]
    # if result == "fail":
    #     raise (ValueError(response.text))
    # msg2 = response.json()["response"]
    # print(msg2)


if __name__ == "__main__":
    test_guandata_modify_user()
