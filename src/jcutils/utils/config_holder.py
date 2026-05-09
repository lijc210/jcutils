import asyncio
import os

from src.jcutils.utils.nacos_client import NacosClient

from .config_loader import ConfigLoader

nacos_config = ConfigLoader.load_config()


async def config_listener(tenant, data_id, group, content):
    config_dict = ConfigLoader._merge_with_env(nacos_config)
    print(f"配置已更新: tenant={tenant}, data_id={data_id}, group={group}")


NACOS_SERVER = os.getenv("NACOS_SERVER", default="")
NACOS_NAMESPACE = os.getenv("NACOS_NAMESPACE", default="")
NACOS_GROUP = os.getenv("NACOS_GROUP", default="")
NACOS_DATA_ID = os.getenv("NACOS_DATA_ID", default="")
NACOS_USERNAME = os.getenv("NACOS_USERNAME", default="")
NACOS_PASSWORD = os.getenv("NACOS_PASSWORD", default="")

nacos_client = NacosClient(
    server=NACOS_SERVER, namespace=NACOS_NAMESPACE, username=NACOS_USERNAME, password=NACOS_PASSWORD
)


async def main():
    # 添加监听器
    print("正在添加配置监听器...")
    await nacos_client.add_listener(config_listener, data_id=NACOS_DATA_ID, group=NACOS_GROUP)
    print("监听器已添加，等待配置变更...")


asyncio.run(main())
