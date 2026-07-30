import asyncio
import os

from jcutils.client import NacosClient

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

nacos_client = NacosClient(
    server=NACOS_SERVER, namespace=NACOS_NAMESPACE, username=NACOS_USERNAME, password=NACOS_PASSWORD
)


async def config_listener(tenant, data_id, group, content):
    print("listen, tenant:{} data_id:{} group:{} ".format(tenant, data_id, group))
    print("content:{}".format(content))


async def main():
    # 添加监听器
    print("正在添加配置监听器...")
    await nacos_client.add_listener(config_listener, data_id=NACOS_DATA_ID, group=NACOS_GROUP)
    print("监听器已添加，等待配置变更...")
    print("按 Ctrl+C 退出")
    print("=" * 60)

    # 保持程序运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭连接...")
        await nacos_client.shutdown()
        print("已退出")


if __name__ == "__main__":
    asyncio.run(main())
