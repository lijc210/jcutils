import requests

from src.api.config import CONFIG
from src.jcutils.utils.tools import user_token

databi_url = CONFIG.DATABI_URL

# 运营门户
adict = {
    "token": user_token,
    "userGroups": [{"name": "运营门户", "externalGroupId": "yunyingmenhu"}],
}

adict = {
    "token": user_token,
    "userGroups": [
        {
            "name": "报表中心配置管理",
            "externalGroupId": "reportCenter",
            "externalParentGroupId": "yunyingmenhu",
        }
    ],
}

adict = {
    "userGroups": [
        {
            "externalParentGroupId": "yunyingmenhu",
            "name": "POS管理平台管理员角色",
            "externalGroupId": "oss-app-pos-web-admin",
        }
    ],
    "token": "b694a58287e924a2b9c60194",
}

response = requests.post(f"{databi_url}/public-api/user-groups/add", json=adict)
print(response.text)

if __name__ == "__main__":
    pass
