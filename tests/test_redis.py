import json

from src.api.config import CONFIG
from src.pyutils.utils.redis_client import RedisClient

REDIS_DB = CONFIG.REDIS_DB

rc = RedisClient(
    host=REDIS_DB["host"], port=6379, db=0, password=REDIS_DB["password"]
).client

r = rc.hgetall("dss:437928")
print("dimStoreShopHistoryRedis")
print(json.dumps(r, ensure_ascii=False))
print("#" * 20)
# r = rc.hgetall("dssf:118833")
# print("dimStoreShopFcustidHistoryRedis")
# print(json.dumps(r, ensure_ascii=False))
# print("#" * 20)
r = rc.hgetall("dps:92300971")
print("dimProductSkuHistoryRedis")
print(json.dumps(r, ensure_ascii=False))
print("#" * 20)
# r = rc.hgetall("dcc:21005601")
# print("dimCodeCategoryHistoryRedis")
# print(json.dumps(r, ensure_ascii=False))
# print("#" * 20)
# r = rc.hgetall("dmi:15678111")
# print("dimMemberInfoHistoryRedis")
# print(json.dumps(r, ensure_ascii=False))
# print("#" * 20)
# r = rc.hgetall("djes:356448")
# print("dimJdErpStockHistoryRedis")
# print(json.dumps(r, ensure_ascii=False))
# print("#" * 20)
# r = rc.hgetall("djem:594010")
# print("dimJdErpMaterialHistroyRedis")
# print(json.dumps(r, ensure_ascii=False))
# print("#" * 20)
# r = rc.hgetall("gba:36822")
# print("dimGroupBuyActivityRedis")
# print(json.dumps(r, ensure_ascii=False))
# r = rc.hgetall("gb:499060")
# print("dimGroupBuyRedis")
# print(json.dumps(r, ensure_ascii=False))
# r = rc.hgetall("cbi:GQYHQ20220804zhaoqiannan39")
# print("OdsCouponBasisInfoToRedis")
# print(json.dumps(r, ensure_ascii=False))

# print("OdsMemberCouponInfoToRedis")
# for coupon_code in ["GQD2023121215967900000062602","GQD2023121221751800000062602","GQD2023121238440100000062602"]:
#     r = rc.hgetall(f"mci:{coupon_code}")
#     print(json.dumps(r, ensure_ascii=False))
# r = rc.hgetall("gsw:415936")
# print("dimWarehouseRedis")
# print(json.dumps(r, ensure_ascii=False))

# r = rc.hgetall("dwusr:17656255655")
# print("dimWsUserShopRelationshipHistoryRedis")
# print(json.dumps(r, ensure_ascii=False))

# pipe = rc.pipeline()
# for i, key in enumerate(rc.scan_iter(match="djes:" + "*", count=1000), 1):
#     pipe.delete(key)
#     if i % 1000 == 0:
#         print (i)
#         pipe.execute()
#     pipe.execute()
