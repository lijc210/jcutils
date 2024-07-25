import requests

from src.pyutils.utils.tools import databi_url, user_token

data_dict = {
    "token": user_token,
    "loginId": "dianchi41424",
    "ugIds": ["ew94cfdssdsafbsfsgwebdawec"],
    "isExternal": True,
}

data_dict = {
    "isExternal": True,
    "ugIds": ["reportCenter"],
    "token": "b694a58287e924a2b9c60194",
    "loginId": "oss254",
}

response = requests.post(f"{databi_url}/public-api/user/add-to-groups", json=data_dict)
print(response.text)
# break

if __name__ == "__main__":
    pass
