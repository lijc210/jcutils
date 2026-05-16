import asyncio
import os

import consul.aio

CONSUL_HOST = os.getenv("CONSUL_HOST", default="")
CONSUL_PORT = os.getenv("CONSUL_PORT", default="")
CONSUL_TOKEN = os.getenv("CONSUL_TOKEN", default="")

kv_prefix = "jcutils/dev"

# kv_prefix = "test"


async def _fetch() -> dict:
    client = consul.aio.Consul(
        host=CONSUL_HOST,
        port=CONSUL_PORT,
        token=CONSUL_TOKEN or None,
    )
    try:
        _, data = await client.kv.get(kv_prefix, recurse=True)
    finally:
        # python-consul2 aio 底层使用 aiohttp，需手动关闭 session
        if hasattr(client.http, "_session") and client.http._session:
            await client.http._session.close()

    if not data:
        raise Exception(f"Consul KV 配置为空或路径不存在: prefix={kv_prefix}")

    # print("data:", data)

    result = {}
    for item in data:
        # print(item)
        key = item.get("Key")
        value = item.get("Value").decode("utf-8")
        # print("value:", value)
        line = value.splitlines()
        for aline in line:
            alist = aline.split("=", 1)
            if len(alist) == 2:
                k, v = alist
                result[k.strip()] = v.strip()
            else:
                if "/" in key:
                    continue
                result[key.strip()] = aline.strip()
    return result


consul_config = asyncio.run(_fetch())

print(consul_config)
