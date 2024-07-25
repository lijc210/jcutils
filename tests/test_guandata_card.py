"""
token填入其中测试是否有效
https://databi.zzgqsh.com/m/app/c034d70f3fC364a07b9c2ab6?provider=guanbi&ssoToken=&m25fbc2bb7edb4fdc8e134e8=411316

"""

import requests

from src.api.config import CONFIG

DATABI_URL = CONFIG.DATABI_URL


def card(cardId):
    url = f"{DATABI_URL}/public-api/card/{cardId}/data"
    adict = {
        "offset": 0,
        "limit": 200,
        "filters": [],
        "dynamicParams": [],
        "name": "未命名的卡片 2023-04-13 17:02",
    }
    Token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxLXdHRGdOWW1GU1FOOTNZZHhyZTVXVThVcmEyNk9RQWRZTlB2cnpaV1NBSTNHeWYxRjJvdFR0UzVJbHNyWTdOZlNnT0o5czYzMVQ1UEpCOGN5RmlmWnJDZnNqZ1JCNmFxbUVhUGExdGI2d21zYW5abk56WnZnXC96MD0iLCJpc3MiOiJndWFuZGF0YS5jb20iLCJleHAiOjE3MjAxNTA5NjAsImlhdCI6MTcxODk0MTM2MCwiaW5pdFRpbWUiOiIyMDI0LTA2LTIxIDExOjQyOjQwLjgwNyIsImp0aSI6IjcwOWY4OGUzNDE1MWY4NWI5NWMxYTBlYjM0MWNmZjllNzg5ZmE5NzE4NjAxYzAyYzcyOWI0N2E4Y2Q2ZmYzMjE1MDUxZmU0NWQ0NDVlMGVkNGNmYzgyMTk2YjE3MjdlMDY2NmExZjg5YTg1ZDMxNzcyYjQ4OTNmNWRkZGMyNDk5YTMzODA3ZmVhOGU4OTU5MDdiYzNhN2I3NGU3ZmQ1ZmJjMTgxMGZiNjJkYjIwYTI1OWQyNmZiZjUzZjIyYzIwMDc5YmU5NmExNDczMGQ1ZTEwNTcyMmZhY2E2YTdmOWRiMTQzM2U0MWQ5ODZmNTRmODJlNmNiMWU0NmE2ZTA2MTMiLCJwd2RWZXJzaW9uIjowfQ.kMDcUG7mRA8EGmdx6aEcQ36M8Ec2uVfERlHbnm2FmUc"
    # headers = {"X-Auth-Token":"b694a58287e924a2b9c60194"}
    headers = {"X-Auth-Token": Token}
    r = requests.post(url, json=adict, headers=headers)
    print(r.text)


if __name__ == "__main__":
    card("w621fa1bdf87b49a79aafadb")
