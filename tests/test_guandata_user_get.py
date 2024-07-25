import requests

from src.api.config import CONFIG
from src.pyutils.utils.tools import user_token

databi_url = CONFIG.DATABI_URL

# 获取用户组列表
bdict = {"token": user_token, "loginId": "oss254TEST"}
response = requests.post(f"{databi_url}/public-api/user/info", json=bdict)
print(response.json())

if __name__ == "__main__":
    pass
