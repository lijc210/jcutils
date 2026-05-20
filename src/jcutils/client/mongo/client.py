"""
@File    :   mongo_client.py
@Time    :   2016/05/10
@Author  :   lijc210@163.com
@Desc    :
MongoDB 连接客户端，支持单机、副本集、分片集群
"""

from typing import Any, Dict, Generator, List, Optional, Union

try:
    import pymongo
    from bson import Timestamp
    from pymongo import MongoClient as PyMongoClient
    from pymongo.collection import Collection
    from pymongo.cursor import Cursor
    from pymongo.database import Database
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install pymongo or uv add "pymongo"')
except Exception as e:
    raise ImportError(f"pymongo 导入失败: {e}")


class MongoClient:
    def __init__(
        self,
        url: Optional[str] = None,
        database: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        replica_set: Optional[str] = None,
    ) -> None:
        """
        MongoDB 连接客户端

        :param url: MongoDB 连接 URL
        :param database: 数据库名称
        :param host: 主机地址
        :param port: 端口
        :param username: 用户名
        :param password: 密码
        :param replica_set: 副本集名称
        """
        self.url = url
        self.database = database
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.replica_set = replica_set

        # 构建连接 URL
        if not self.url:
            if self.username and self.password:
                self.url = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"
            else:
                self.url = f"mongodb://{self.host}:{self.port}/"

    def get_client(self) -> PyMongoClient:
        """
        获取 MongoDB 客户端

        :return: MongoDB 客户端对象
        """
        return pymongo.MongoClient(self.url, replicaSet=self.replica_set)

    def get_database(self, database: Optional[str] = None) -> Database:
        """
        获取数据库

        :param database: 数据库名称，如果不指定则使用初始化时的数据库名
        :return: 数据库对象
        """
        db_name = database or self.database
        if not db_name:
            raise ValueError("Database name is required")
        return self.get_client()[db_name]

    def get_collection(self, collection: str, database: Optional[str] = None) -> Collection:
        """
        获取集合

        :param collection: 集合名称
        :param database: 数据库名称
        :return: 集合对象
        """
        return self.get_database(database)[collection]

    def find_one(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        database: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        查询单条记录

        :param collection: 集合名称
        :param filter: 查询条件
        :param projection: 投影（字段选择）
        :param sort: 排序，如 [("field", pymongo.DESCENDING)]
        :param database: 数据库名称
        :return: 单条记录
        """
        coll = self.get_collection(collection, database)
        kwargs: Dict[str, Any] = {}
        if filter:
            kwargs["filter"] = filter
        if projection:
            kwargs["projection"] = projection
        if sort:
            kwargs["sort"] = sort
        return coll.find_one(**kwargs)

    def find(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        database: Optional[str] = None,
    ) -> Cursor:
        """
        查询多条记录

        :param collection: 集合名称
        :param filter: 查询条件
        :param projection: 投影（字段选择）
        :param sort: 排序
        :param limit: 限制返回数量
        :param skip: 跳过数量
        :param database: 数据库名称
        :return: 游标对象
        """
        coll = self.get_collection(collection, database)
        kwargs: Dict[str, Any] = {}
        if filter:
            kwargs["filter"] = filter
        if projection:
            kwargs["projection"] = projection
        if sort:
            kwargs["sort"] = sort
        if limit:
            kwargs["limit"] = limit
        if skip:
            kwargs["skip"] = skip
        return coll.find(**kwargs)

    def find_iter(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        batch_size: int = 100,
        database: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式查询多条记录

        :param collection: 集合名称
        :param filter: 查询条件
        :param projection: 投影（字段选择）
        :param sort: 排序
        :param batch_size: 批量获取大小
        :param database: 数据库名称
        :return: 生成器
        """
        cursor = self.find(
            collection=collection,
            filter=filter,
            projection=projection,
            sort=sort,
            database=database,
        )
        cursor = cursor.batch_size(batch_size)
        for document in cursor:
            yield document

    def insert_one(
        self,
        collection: str,
        document: Dict[str, Any],
        database: Optional[str] = None,
    ) -> pymongo.results.InsertOneResult:
        """
        插入单条记录

        :param collection: 集合名称
        :param document: 文档
        :param database: 数据库名称
        :return: 插入结果
        """
        coll = self.get_collection(collection, database)
        return coll.insert_one(document)

    def insert_many(
        self,
        collection: str,
        documents: List[Dict[str, Any]],
        ordered: bool = True,
        database: Optional[str] = None,
    ) -> pymongo.results.InsertManyResult:
        """
        批量插入记录

        :param collection: 集合名称
        :param documents: 文档列表
        :param ordered: 是否有序插入
        :param database: 数据库名称
        :return: 插入结果
        """
        coll = self.get_collection(collection, database)
        return coll.insert_many(documents, ordered=ordered)

    def update_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
        database: Optional[str] = None,
    ) -> pymongo.results.UpdateResult:
        """
        更新单条记录

        :param collection: 集合名称
        :param filter: 查询条件
        :param update: 更新内容
        :param upsert: 如果不存在是否插入
        :param database: 数据库名称
        :return: 更新结果
        """
        coll = self.get_collection(collection, database)
        return coll.update_one(filter, update, upsert=upsert)

    def update_many(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
        database: Optional[str] = None,
    ) -> pymongo.results.UpdateResult:
        """
        批量更新记录

        :param collection: 集合名称
        :param filter: 查询条件
        :param update: 更新内容
        :param upsert: 如果不存在是否插入
        :param database: 数据库名称
        :return: 更新结果
        """
        coll = self.get_collection(collection, database)
        return coll.update_many(filter, update, upsert=upsert)

    def replace_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        replacement: Dict[str, Any],
        upsert: bool = False,
        database: Optional[str] = None,
    ) -> pymongo.results.UpdateResult:
        """
        替换单条记录

        :param collection: 集合名称
        :param filter: 查询条件
        :param replacement: 替换文档
        :param upsert: 如果不存在是否插入
        :param database: 数据库名称
        :return: 更新结果
        """
        coll = self.get_collection(collection, database)
        return coll.replace_one(filter, replacement, upsert=upsert)

    def delete_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        database: Optional[str] = None,
    ) -> pymongo.results.DeleteResult:
        """
        删除单条记录

        :param collection: 集合名称
        :param filter: 查询条件
        :param database: 数据库名称
        :return: 删除结果
        """
        coll = self.get_collection(collection, database)
        return coll.delete_one(filter)

    def delete_many(
        self,
        collection: str,
        filter: Dict[str, Any],
        database: Optional[str] = None,
    ) -> pymongo.results.DeleteResult:
        """
        批量删除记录

        :param collection: 集合名称
        :param filter: 查询条件
        :param database: 数据库名称
        :return: 删除结果
        """
        coll = self.get_collection(collection, database)
        return coll.delete_many(filter)

    def count_documents(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> int:
        """
        统计文档数量

        :param collection: 集合名称
        :param filter: 查询条件
        :param database: 数据库名称
        :return: 文档数量
        """
        coll = self.get_collection(collection, database)
        return coll.count_documents(filter or {})

    def distinct(
        self,
        collection: str,
        key: str,
        filter: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Any]:
        """
        获取不重复的值

        :param collection: 集合名称
        :param key: 字段名
        :param filter: 查询条件
        :param database: 数据库名称
        :return: 不重复的值列表
        """
        coll = self.get_collection(collection, database)
        return coll.distinct(key, filter or {})

    def aggregate(
        self,
        collection: str,
        pipeline: List[Dict[str, Any]],
        database: Optional[str] = None,
    ) -> Cursor:
        """
        聚合查询

        :param collection: 集合名称
        :param pipeline: 聚合管道
        :param database: 数据库名称
        :return: 游标对象
        """
        coll = self.get_collection(collection, database)
        return coll.aggregate(pipeline)

    def create_index(
        self,
        collection: str,
        keys: Union[str, List[tuple]],
        database: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        创建索引

        :param collection: 集合名称
        :param keys: 索引字段，如 "field" 或 [("field", pymongo.ASCENDING)]
        :param database: 数据库名称
        :param kwargs: 其他参数
        :return: 索引名称
        """
        coll = self.get_collection(collection, database)
        return coll.create_index(keys, **kwargs)

    def drop_index(
        self,
        collection: str,
        index_name: str,
        database: Optional[str] = None,
    ) -> None:
        """
        删除索引

        :param collection: 集合名称
        :param index_name: 索引名称
        :param database: 数据库名称
        """
        coll = self.get_collection(collection, database)
        coll.drop_index(index_name)

    def drop_collection(
        self,
        collection: str,
        database: Optional[str] = None,
    ) -> None:
        """
        删除集合

        :param collection: 集合名称
        :param database: 数据库名称
        """
        coll = self.get_collection(collection, database)
        coll.drop()

    # ============ Oplog 监听 ============

    def oplog(
        self,
        ts: Optional[Timestamp] = None,
        database: Optional[str] = None,
    ) -> Cursor:
        """
        监听 MongoDB Oplog（操作日志）

        使用示例:
        ```python
        from bson.timestamp import Timestamp
        ts = Timestamp(1541660421, 3)

        for doc in mongo_client.oplog(ts):
            print(doc)
            ts = doc['ts']
        ```

        Oplog 操作类型:
        - "i": insert
        - "u": update
        - "d": delete
        - "c": db cmd
        - "db": 声明当前数据库
        - "n": no op, 空操作

        :param ts: 时间戳，如果不指定则从最新的开始
        :param database: 数据库名称（可选，用于过滤）
        :return: 游标对象
        """
        client = self.get_client()
        is_master = client.admin.command("isMaster")
        replica_set = is_master.get("setName", None)

        if not replica_set:
            raise RuntimeError("Oplog requires a replica set")

        # 使用副本集名称重新连接
        client = pymongo.MongoClient(self.url, replicaSet=replica_set)
        oplog = client.local.oplog.rs

        if not ts:
            first = oplog.find().sort("$natural", pymongo.ASCENDING).limit(-1).next()
            ts = first["ts"]

        query: Dict[str, Any] = {"ts": {"$gt": ts}}
        if database:
            query["ns"] = {"$regex": f"^{database}\\."}

        cursor = oplog.find(query)
        # 设置游标为可追踪
        cursor = cursor.add_option(pymongo.CursorType.TAILABLE_AWAIT)
        return cursor

    # ============ 上下文管理器 ============

    def __enter__(self) -> "MongoClient":
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出上下文"""
        client = self.get_client()
        client.close()


if __name__ == "__main__":
    # 单机模式
    mongo_client = MongoClient(
        host="127.0.0.1",
        port=27017,
        database="test_db",
    )

    # 使用 URL 连接
    mongo_client = MongoClient(
        url="mongodb://127.0.0.1:27017/",
        database="test_db",
    )

    # 使用用户名密码连接
    mongo_client = MongoClient(
        url="mongodb://username:password@127.0.0.1:27017/",
        database="test_db",
    )

    # 副本集连接
    # mongo_client = MongoClient(
    #     url="mongodb://user:pass@host1:27017,host2:27017,host3:27017/",
    #     database="test_db",
    #     replica_set="myReplicaSet",
    # )

    # 插入单条记录
    result = mongo_client.insert_one("users", {"name": "Alice", "age": 30})
    print("InsertOneResult:", result.inserted_id)

    # 批量插入
    documents = [
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35},
        {"name": "David", "age": 28},
    ]
    result = mongo_client.insert_many("users", documents)
    print("InsertManyResult:", result.inserted_ids)

    # 查询单条记录
    user = mongo_client.find_one("users", {"name": "Alice"})
    print("find_one:", user)

    # 查询多条记录
    cursor = mongo_client.find("users", {"age": {"$gte": 25}}, sort=[("age", pymongo.ASCENDING)])
    for user in cursor:
        print("find:", user)

    # 流式查询
    for user in mongo_client.find_iter("users", batch_size=2):
        print("find_iter:", user)

    # 更新记录
    result = mongo_client.update_one("users", {"name": "Alice"}, {"$set": {"age": 31}})
    print("UpdateOneResult:", result.modified_count)

    # 替换记录
    result = mongo_client.replace_one("users", {"name": "Bob"}, {"name": "Bob", "age": 26, "city": "New York"})
    print("ReplaceOneResult:", result.modified_count)

    # 批量更新
    result = mongo_client.update_many("users", {"age": {"$lt": 30}}, {"$inc": {"age": 1}})
    print("UpdateManyResult:", result.modified_count)

    # 删除记录
    result = mongo_client.delete_one("users", {"name": "Alice"})
    print("DeleteOneResult:", result.deleted_count)

    # 批量删除
    result = mongo_client.delete_many("users", {"age": {"$gt": 30}})
    print("DeleteManyResult:", result.deleted_count)

    # 统计数量
    count = mongo_client.count_documents("users")
    print("count_documents:", count)

    # 去重查询
    cities = mongo_client.distinct("users", "city")
    print("distinct:", cities)

    # 聚合查询
    pipeline = [{"$group": {"_id": "$name", "total": {"$sum": 1}}}]
    for result in mongo_client.aggregate("users", pipeline):
        print("aggregate:", result)

    # 创建索引
    index_name = mongo_client.create_index("users", "name")
    print("create_index:", index_name)

    # 使用上下文管理器
    with MongoClient(url="mongodb://127.0.0.1:27017/", database="test_db") as mongo_ctx:
        result = mongo_ctx.find_one("users", {"name": "Alice"})
        print("with context:", result)
