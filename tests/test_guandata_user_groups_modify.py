import requests

from src.api.config import CONFIG
from src.jcutils.utils.tools import user_token

databi_url = CONFIG.DATABI_URL

adict = {
    "token": user_token,
    "userGroups": [{"name": "店驰公司绩效", "externalGroupId": "exta240866b7742c6b87b6cc"}],
}
response = requests.post(f"{databi_url}/public-api/user-groups/add", json=adict)
print(response.text)

if __name__ == "__main__":
    pass
