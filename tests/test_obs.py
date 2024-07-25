# 引入模块
from obs import ObsClient

# 创建ObsClient实例
obsClient = ObsClient(
    access_key_id="CJ9IBNVGQVDAMG3PQYX2",
    secret_access_key="9RvpScV6ZaLywXpbE3hOnIUaSEyOPgAupTZJdIPj",
    server="obs.cn-north-4.myhuaweicloud.com",
)
# 使用访问OBS
print(obsClient.listBuckets())

# 关闭obsClient
obsClient.close()
