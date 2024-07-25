import requests

from src.api.config import CONFIG
from src.pyutils.utils.tools import user_token

databi_url = CONFIG.DATABI_URL

users = [
    "879338965",
    "13917911032",
    "240976566",
    "13166235198",
    "1143599346",
    "936455045",
    "845779262",
    "269672681",
    "1300836229",
    "815077402",
    "2670627758",
    "2549528073",
    "80741472",
    "508936861",
    "364324474",
    "840833229",
    "1633803774",
    "523064046",
    "469348122",
    "1459964571",
    "123",
    "1343275548",
    "1226473738",
    "284814982",
    "466673586",
    "839797223",
    "657882782",
    "153337116",
    "865654489",
    "304884836",
    "47458085",
    "705108989",
    "47458085@qq.com",
]

# 批量删除用户
bdict = {"token": user_token, "users": users}
response = requests.post(f"{databi_url}/public-api/users/delete", json=bdict)
print(response.text)

if __name__ == "__main__":
    pass
