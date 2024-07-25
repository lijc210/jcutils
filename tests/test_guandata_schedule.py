import requests

from src.api.config import CONFIG

databi_url = CONFIG.DATABI_URL


def get_token():
    data = {"domain": "guanbi", "email": "xuanji-api", "password": "U3lzejAyMTA="}
    r = requests.post(
        CONFIG.XUANJI_URL + "/api/v1/instant/function/sign-in",
        json=data,
    )
    print(r.text)
    res = r.json()
    token = res.get("data", {}).get("token", "")
    return token


def CARD():
    url = f"{databi_url}/api/schedule/CARD"
    adict = {"scType": "CARD", "offset": 20, "limit": 20, "qEnabled": "enabled"}
    Token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxLXpjXC9zaHVUa3RGNHk3M2FBSkx4K0VYRlN4Z2ZoY09XMEdUcUhsQ1YwWDVkWk9NS1pZR00wRGJWU0N4VDBMdVU5Y1ZrQ2ZCQVZnSkl4SXhGZkFhSVwvNWNpV3hKcVlXUG9rUmRaQ1NyUFhVYmV3YzZpdThnPT0iLCJpc3MiOiJndWFuZGF0YS5jb20iLCJleHAiOjE3MjAxNTc4NzEsImlhdCI6MTcxODk0ODI3MSwiaW5pdFRpbWUiOiIyMDI0LTA2LTIxIDEzOjM3OjUxLjEwNiIsImp0aSI6Ijc5NjU2OWI0YjMxYmFlYmIwYmMyZmQ0NGE1NTE5ODQ1MjNhZWViZGYxOWQ1NTQ3MTkwOWMzOWZiZjNlM2UxYWZhZGJkYjYwNWU4MzQzYmQwZTk5YWM5MzZiNDY5MDBjODU1MTgzMjU1NjU0NDM3NTZiN2QwMTVkNGI5ZjcyOWEyZWJkZTIxN2UyM2EwMzAxMTZhNDY2YjZkYzczN2FkYzYxOGNkMGYzNTM4MmQxNjAwMGQxMDQ0YWU2NDZiOGJhMzRiMDVkNTc1YmZiNGIwOTM0NzA2NGFhMmIxOGU2NDBkZjBiOGNlOWNhNGJiMGIwNWRiMTdjYTFkMTI0ZmVkY2MiLCJwd2RWZXJzaW9uIjoxfQ.4H2-29CG-w0PvqEpxnRXauLoByA5KckzLD0suoEMf40"
    headers = {"X-Auth-Token": Token}
    r = requests.post(url, json=adict, headers=headers)
    print(r.text)


def MULTI_CARD():
    url = f"{databi_url}/api/schedule/MULTI_CARD"
    adict = {"scType": "MULTI_CARD", "offset": 20, "limit": 20, "qEnabled": "enabled"}
    Token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxLXpjXC9zaHVUa3RGNHk3M2FBSkx4K0VYRlN4Z2ZoY09XMEdUcUhsQ1YwWDVkWk9NS1pZR00wRGJWU0N4VDBMdVU5Y1ZrQ2ZCQVZnSkl4SXhGZkFhSVwvNWNpV3hKcVlXUG9rUmRaQ1NyUFhVYmV3YzZpdThnPT0iLCJpc3MiOiJndWFuZGF0YS5jb20iLCJleHAiOjE3MjAxNTc4NzEsImlhdCI6MTcxODk0ODI3MSwiaW5pdFRpbWUiOiIyMDI0LTA2LTIxIDEzOjM3OjUxLjEwNiIsImp0aSI6Ijc5NjU2OWI0YjMxYmFlYmIwYmMyZmQ0NGE1NTE5ODQ1MjNhZWViZGYxOWQ1NTQ3MTkwOWMzOWZiZjNlM2UxYWZhZGJkYjYwNWU4MzQzYmQwZTk5YWM5MzZiNDY5MDBjODU1MTgzMjU1NjU0NDM3NTZiN2QwMTVkNGI5ZjcyOWEyZWJkZTIxN2UyM2EwMzAxMTZhNDY2YjZkYzczN2FkYzYxOGNkMGYzNTM4MmQxNjAwMGQxMDQ0YWU2NDZiOGJhMzRiMDVkNTc1YmZiNGIwOTM0NzA2NGFhMmIxOGU2NDBkZjBiOGNlOWNhNGJiMGIwNWRiMTdjYTFkMTI0ZmVkY2MiLCJwd2RWZXJzaW9uIjoxfQ.4H2-29CG-w0PvqEpxnRXauLoByA5KckzLD0suoEMf40"
    headers = {"X-Auth-Token": Token}
    r = requests.post(url, json=adict, headers=headers)
    print(r.text)


def PAGE():
    url = f"{databi_url}/api/schedule/PAGE"
    adict = {"scType": "PAGE", "offset": 20, "limit": 20, "qEnabled": "enabled"}
    Token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxLXpjXC9zaHVUa3RGNHk3M2FBSkx4K0VYRlN4Z2ZoY09XMEdUcUhsQ1YwWDVkWk9NS1pZR00wRGJWU0N4VDBMdVU5Y1ZrQ2ZCQVZnSkl4SXhGZkFhSVwvNWNpV3hKcVlXUG9rUmRaQ1NyUFhVYmV3YzZpdThnPT0iLCJpc3MiOiJndWFuZGF0YS5jb20iLCJleHAiOjE3MjAxNTc4NzEsImlhdCI6MTcxODk0ODI3MSwiaW5pdFRpbWUiOiIyMDI0LTA2LTIxIDEzOjM3OjUxLjEwNiIsImp0aSI6Ijc5NjU2OWI0YjMxYmFlYmIwYmMyZmQ0NGE1NTE5ODQ1MjNhZWViZGYxOWQ1NTQ3MTkwOWMzOWZiZjNlM2UxYWZhZGJkYjYwNWU4MzQzYmQwZTk5YWM5MzZiNDY5MDBjODU1MTgzMjU1NjU0NDM3NTZiN2QwMTVkNGI5ZjcyOWEyZWJkZTIxN2UyM2EwMzAxMTZhNDY2YjZkYzczN2FkYzYxOGNkMGYzNTM4MmQxNjAwMGQxMDQ0YWU2NDZiOGJhMzRiMDVkNTc1YmZiNGIwOTM0NzA2NGFhMmIxOGU2NDBkZjBiOGNlOWNhNGJiMGIwNWRiMTdjYTFkMTI0ZmVkY2MiLCJwd2RWZXJzaW9uIjoxfQ.4H2-29CG-w0PvqEpxnRXauLoByA5KckzLD0suoEMf40"
    headers = {"X-Auth-Token": Token}
    r = requests.post(url, json=adict, headers=headers)
    print(r.text)


def HISTORY():
    url = f"{databi_url}/api/schedule/CARD/history"
    adict = {"offset": 0, "limit": 20, "scId": "we2b9203a955c4b15aba50b3"}
    Token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxLXpjXC9zaHVUa3RGNHk3M2FBSkx4K0VYRlN4Z2ZoY09XMEdUcUhsQ1YwWDVkWk9NS1pZR00wRGJWU0N4VDBMdVU5Y1ZrQ2ZCQVZnSkl4SXhGZkFhSVwvNWNpV3hKcVlXUG9rUmRaQ1NyUFhVYmV3YzZpdThnPT0iLCJpc3MiOiJndWFuZGF0YS5jb20iLCJleHAiOjE3MjAxNTc4NzEsImlhdCI6MTcxODk0ODI3MSwiaW5pdFRpbWUiOiIyMDI0LTA2LTIxIDEzOjM3OjUxLjEwNiIsImp0aSI6Ijc5NjU2OWI0YjMxYmFlYmIwYmMyZmQ0NGE1NTE5ODQ1MjNhZWViZGYxOWQ1NTQ3MTkwOWMzOWZiZjNlM2UxYWZhZGJkYjYwNWU4MzQzYmQwZTk5YWM5MzZiNDY5MDBjODU1MTgzMjU1NjU0NDM3NTZiN2QwMTVkNGI5ZjcyOWEyZWJkZTIxN2UyM2EwMzAxMTZhNDY2YjZkYzczN2FkYzYxOGNkMGYzNTM4MmQxNjAwMGQxMDQ0YWU2NDZiOGJhMzRiMDVkNTc1YmZiNGIwOTM0NzA2NGFhMmIxOGU2NDBkZjBiOGNlOWNhNGJiMGIwNWRiMTdjYTFkMTI0ZmVkY2MiLCJwd2RWZXJzaW9uIjoxfQ.4H2-29CG-w0PvqEpxnRXauLoByA5KckzLD0suoEMf40"
    headers = {"X-Auth-Token": Token}
    r = requests.post(url, json=adict, headers=headers)
    print(r.text)


if __name__ == "__main__":
    # CARD()
    # MULTI_CARD()
    # PAGE()
    HISTORY()
