import asyncio
import os

from jcutils.client import AsyncEtcdClient

ETCD_HOST = os.getenv("ETCD_HOST", default="")
ETCD_PORT = int(os.getenv("ETCD_PORT", default=""))
ETCD_SCHEME = os.getenv("ETCD_SCHEME", default="")
ETCD_USER = os.getenv("ETCD_USER", default="")
ETCD_PASSWORD = os.getenv("ETCD_PASSWORD", default="")

print("=" * 60)
print("ETCD 配置信息:")
print("=" * 60)
print(f"服务器地址: {ETCD_HOST}")
print("=" * 60)


etcd_client = AsyncEtcdClient(host="etcd-grpc.cizai.dpdns.org", port=2379, username=ETCD_USER, password=ETCD_PASSWORD)


async def main():
    # 获取配置客户端
    content = await etcd_client.get_raw(key="test")
    print("当前配置内容:")
    print(content)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
