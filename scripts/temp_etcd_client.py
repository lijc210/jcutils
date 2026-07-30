import os

from jcutils.client import EtcdClient

ETCD_HOST = os.getenv("ETCD_HOST", default="")
ETCD_PORT = int(os.getenv("ETCD_PORT", default=""))
ETCD_SCHEME = os.getenv("ETCD_SCHEME", default="")

print("=" * 60)
print("ETCD 配置信息:")
print("=" * 60)
print(f"服务器地址: {ETCD_HOST}")
print("=" * 60)


etcd_client = EtcdClient(host="etcd.cizai.dpdns.org", port=443, protocol="https")


def main():
    # 获取配置客户端
    content = etcd_client.get_raw(key="test")
    print("当前配置内容:")
    print(content)
    print("=" * 60)


if __name__ == "__main__":
    main()
