import json
import os

from pyapollo.client import ApolloClient

APOLLO_META_SERVER_ADDRESS = os.getenv("APOLLO_META_SERVER_ADDRESS")
APOLLO_APP_ID = os.getenv("APOLLO_APP_ID")
print(APOLLO_META_SERVER_ADDRESS, APOLLO_APP_ID)

# 无鉴权的 Apollo 同步客户端
apollo_client = ApolloClient(
    meta_server_address=APOLLO_META_SERVER_ADDRESS,
    app_id=APOLLO_APP_ID,
    env="DEV",
)

print(apollo_client)
config = apollo_client.get_current_config()
print(json.dumps(config, indent=2, ensure_ascii=False))


target_dict = apollo_client.get_json_value("dingtalk_process_code_json")
print(json.dumps(target_dict, indent=2, ensure_ascii=False))


# 读取内部缓存
all_configs = apollo_client._cache  # dict: {namespace: {key: value}}

# 打印默认 namespace（application）下所有配置
for key, value in all_configs.get("application", {}).items():
    print(f"{key} = {value}")
