import asyncio
import os

from jcutils.client import AsyncNacosClient

NACOS_SERVER = os.getenv("NACOS_SERVER", default="")
NACOS_NAMESPACE = os.getenv("NACOS_NAMESPACE", default="")
NACOS_GROUP = os.getenv("NACOS_GROUP", default="")
NACOS_DATA_ID = os.getenv("NACOS_DATA_ID", default="")
NACOS_USERNAME = os.getenv("NACOS_USERNAME", default="")
NACOS_PASSWORD = os.getenv("NACOS_PASSWORD", default="")

print("=" * 60)
print("Nacos 配置信息:")
print("=" * 60)
print(f"服务器地址: {NACOS_SERVER}")
print(f"命名空间: {NACOS_NAMESPACE}")
print(f"配置组: {NACOS_GROUP}")
print(f"配置ID: {NACOS_DATA_ID}")
print(f"用户名: {NACOS_USERNAME}")
print("=" * 60)

nacos_client = AsyncNacosClient(
    server=NACOS_SERVER, namespace=NACOS_NAMESPACE, username=NACOS_USERNAME, password=NACOS_PASSWORD
)


async def main():
    # 获取配置客户端
    content = await nacos_client.get_raw(NACOS_DATA_ID, group=NACOS_GROUP)
    print("当前配置内容:")
    print(content)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
