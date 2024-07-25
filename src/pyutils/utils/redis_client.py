"""
Created on 2016/5/10
@author: lijc210@163.com
Desc: 功能描述。

pip install redis-py-cluster

"""

import redis
from rediscluster import RedisCluster


class RedisClient:
    def __init__(
        self,
        host=None,
        port=None,
        db=None,
        password=None,
        pool=False,
        startup_nodes=None,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.pool = pool
        self.startup_nodes = startup_nodes
        self.client = self.conn()

    def conn(self):
        """
        连接
        集群模式只有一个db
        :return:
        """
        if self.startup_nodes:
            conn = RedisCluster(
                startup_nodes=self.startup_nodes, decode_responses=True
            )  # 连接集群
        elif self.pool:
            pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
            )
            conn = redis.Redis(connection_pool=pool)  # 连接池
        else:
            conn = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
            )
        return conn

    def _set(self):
        """
        设置字符串类型
        :return:
        """
        self.client.set("test", "test")
        self.client.set("test_num", 5)
        print(self.client.get("test"))
        print(self.client.mset({"test1": "test1", "test2": "test2"}))
        print(self.client.mget(["test1", "test2"]))

    def _lpush(self):
        """
        设置列表
        :return:
        """
        self.client.delete("test_list")
        self.client.lpush("test_list", 1)
        self.client.lpush("test_list", 2)
        self.client.lpush("test_list", 3)
        print(self.client.lrange("itemcf_list", 0, 10))  # 取出
        print(self.client.lrange("test_list", 0, 10))  # 取出
        print(
            self.client.brpop("test_list")
        )  # 移出并获取列表的最开始的一个元素，如果没有会阻塞
        print(
            self.client.llen("test_list")
        )  # 移出并获取列表的最开始的一个元素，如果没有会阻塞

    def _sadd(self):
        """
        设置无序集合类型
        :return:
        """
        self.client.sadd("test_set", *[1, 2, 3, 4])
        print(self.client.smembers("test_set"))
        self.client.sadd("test_set2", *[3, 4, 5, 6])
        self.client.sadd("test_set3", *[4, 6, 8])
        print(self.client.sinter(["test_set", "test_set2", "test_set3"]))  # 返回交集
        print(self.client.sunion(["test_set", "test_set2", "test_set3"]))  # 返回并集
        print(self.client.scard("test_set"))  # 返回元素个数

    def _zadd(self):
        """
        设置有序集合类型
        交集并集在集群环境不可用
        :return:
        """
        self.client.zadd("test_zset", **{"a": 1, "b": 10})
        self.client.zadd("test_zset1", **{"b": 2, "c": 20})
        print(
            self.client.zinterstore(
                "sum_zinter", ["test_zset", "test_zset1"], aggregate="SUM"
            )
        )  # 返回交集，aggregate的值为: SUM  MIN  MAX
        print(
            self.client.zunionstore(
                "sum_zunion", ["test_zset", "test_zset1"], aggregate="SUM"
            )
        )  # 返回并集，aggregate的值为: SUM  MIN  MAX
        print(
            self.client.zrevrange("sum_zinter", 0, 4, withscores=True)
        )  # 得分最大的5篇
        print(
            self.client.zrevrange("sum_zunion", 0, 4, withscores=True)
        )  # 得分最大的5篇
        print(
            self.client.zrangebyscore("test_zset", 0, 5, withscores=True)
        )  # 得分0-5之间
        print(self.client.zrange("test_zset", 0, -1, withscores=True))  # 正序返回所有
        print(
            self.client.zrevrange("test_zset", 0, -1, withscores=True)
        )  # 倒序返回所有
        self.client.zremrangebyrank(
            "test_zset", 0, self.client.zcard("test_zset") - 3 - 1
        )  # 保留得分最高的3个key，其他都删除

    def _hmset(self):
        """
        设置哈希类型
        :return:
        """
        self.client.hmset("test_hash", {"a": 1, "b": 10})
        print(self.client.hgetall("test_hash"))

    def _incr(self):
        """
        自增
        :return:
        """
        return self.client.incr("test_num")

    def _decr(self):
        """
        自增
        :return:
        """
        return self.client.decr("test_num")

    def _lua(self):
        """
        script1 原生不支持返回交集的长度，配合lua可以实现
        script2 支持keys中的第一个集合和后面的所有集合取交集，并返回长度
        :return:
        """
        # lua1 = """
        #   return #redis.call('sinter',unpack(KEYS))
        # """
        # script1 = self.client.register_script(lua1)
        # print(script1(keys=['test_set', 'test_set2', 'test_set3']))

        lua1 = """
        local res = {}
        local base_set = KEYS[1]
        local i = 2
        while(i <= #KEYS) do
            res[i-1] = #redis.call('sinter',unpack({base_set,KEYS[i]}))
            i = i+1
        end
        return res
        """
        script1 = self.client.register_script(lua1)
        print(script1(keys=["test_set", "test_set2", "test_set3", "test_set4"]))

    def scan_del(self, match="djes:", size=10000):
        pipe = self.client.pipeline()
        for i, key in enumerate(
            self.client.scan_iter(match=match + "*", count=1000), 1
        ):
            pipe.delete(key)
            if i % size == 0:
                print(i)
                pipe.execute()
            pipe.execute()


if __name__ == "__main__":
    # startup_nodes = [{"host": "10.10.20.97", "port": "7000"}, {"host": "10.10.20.97", "port": "7001"}]
    # rc = RedisClient(startup_nodes=startup_nodes).client
    rc = RedisClient(host="10.10.20.165", port=6379, db=0)
    # print (rc.get("test"))
    # # 验证redis服务是否正常
    # rc = RedisClient(startup_nodes=startup_nodes)
    # rc._set()
    # rc._lpush()
    # rc._sadd()
    # rc._zadd()
    # rc._hmset()

    # print (r.smembers('unitSet')

    # print(rc._set())
    # print(rc._incr())
    # print(rc._decr())
    # rc._sadd()
    # rc._lua()
