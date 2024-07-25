import requests

from src.api.config import CONFIG
from src.pyutils.utils.tools import user_token

databi_url = CONFIG.DATABI_URL

# 通过指定的用户的loginid查询对应的uid
adict = {"token": user_token, "loginId": "oss254TEST"}
response = requests.post(f"{databi_url}/public-api/user/info", json=adict)
print(response.text)
uId = response.json()["response"]["uId"]

# 获取用户组
bdict = {"token": user_token}
response = requests.post(f"{databi_url}/public-api/user/{uId}/groups", json=bdict)
print(f"{databi_url}/public-api/user/{uId}/groups")
print(response.text)

if __name__ == "__main__":
    pass
