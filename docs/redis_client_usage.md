# RedisClient 使用文档

## 简介

`RedisClient` 是一个简单易用的 Redis 客户端封装类，支持单机模式和集群模式，提供统一的 API 接口。

**主要特点：**
- 支持单机和集群两种模式
- 自动检测连接模式
- 统一的 API 接口
- 完整的类型注解
- 详细的使用文档和示例
- 支持上下文管理器

## 安装依赖

```bash
pip install redis
```

**注意：** 不需要安装 `redis-py-cluster`，直接使用 `redis` 官方库的集群功能即可。

## 快速开始

### 单机模式

```python
from jcutils.client.redis_client import RedisClient

# 创建客户端
rc = RedisClient(host="127.0.0.1", port=6379, password="your_password")

# 测试连接
if rc.ping():
    print("Redis 连接成功")

# 基本操作
rc.set("name", "张三", ex=3600)  # 设置键值，1小时后过期
value = rc.get("name")  # 获取值
print(value)  # 输出：张三

# 关闭连接
rc.close()
```

### 集群模式

```python
from jcutils.client.redis_client import RedisClient

# 配置集群节点
startup_nodes = [
    {"host": "10.10.20.97", "port": 7000},
    {"host": "10.10.20.97", "port": 7001},
    {"host": "10.10.20.97", "port": 7002}
]

# 创建集群客户端
rc = RedisClient(startup_nodes=startup_nodes, password="your_password")

# 使用方式与单机模式完全相同
rc.set("key", "value")
value = rc.get("key")
```

### 使用上下文管理器

```python
from jcutils.client.redis_client import RedisClient

# 自动管理连接
with RedisClient(host="127.0.0.1", port=6379) as rc:
    rc.set("key", "value")
    value = rc.get("key")
    # 退出 with 块时自动关闭连接
```

## 初始化参数说明

```python
RedisClient(
    host=None,              # Redis 服务器地址（单机模式）
    port=6379,              # Redis 服务器端口，默认 6379
    db=0,                   # 数据库编号（单机模式），默认 0，范围 0-15
    password=None,          # 密码
    startup_nodes=None,     # 集群节点列表（集群模式）
    decode_responses=True,  # 是否自动解码响应为字符串
    **kwargs                # 其他 Redis 连接参数
)
```

**参数说明：**

- `host`: 单机模式必需，Redis 服务器 IP 地址
- `port`: Redis 服务器端口，默认 6379
- `db`: 数据库编号，单机模式可用，范围 0-15
- `password`: Redis 密码，如果设置了密码则必须提供
- `startup_nodes`: 集群模式必需，格式：`[{"host": "ip", "port": 7000}, ...]`
- `decode_responses`: 是否将响应解码为字符串，默认 True
- `**kwargs`: 其他参数，如：
  - `socket_timeout`: Socket 超时时间
  - `socket_connect_timeout`: 连接超时时间
  - `max_connections`: 最大连接数
  - `retry_on_timeout`: 超时是否重试

## 方法列表

### 连接管理

#### ping()

测试 Redis 服务器连接是否正常。

**返回值：**
- `bool`: True 表示连接正常，False 表示连接失败

**示例：**
```python
rc = RedisClient(host="127.0.0.1")
if rc.ping():
    print("连接成功")
else:
    print("连接失败")
```

#### close()

关闭 Redis 连接，释放连接池资源。

**示例：**
```python
rc = RedisClient(host="127.0.0.1")
rc.set("key", "value")
rc.close()  # 显式关闭连接
```

---

### String 字符串操作

#### set(key, value, ex=None, px=None)

设置字符串键值对。如果键已存在，会覆盖旧值。

**参数：**
- `key` (str): 键名
- `value` (Any): 值，可以是字符串、数字等
- `ex` (int, optional): 过期时间（秒）
- `px` (int, optional): 过期时间（毫秒）

**返回值：**
- `bool`: True 表示设置成功

**示例：**
```python
# 设置永不过期的键
rc.set("name", "张三")

# 设置 1 小时后过期
rc.set("session", "abc123", ex=3600)

# 设置 5 秒后过期（毫秒）
rc.set("token", "xyz789", px=5000)

# 设置数字
rc.set("counter", 0)
```

#### get(key)

获取字符串值。

**参数：**
- `key` (str): 键名

**返回值：**
- `Optional[str]`: 键对应的值，如果键不存在返回 None

**示例：**
```python
rc.set("name", "张三")
name = rc.get("name")  # "张三"
age = rc.get("age")    # None，键不存在
```

#### mset(mapping)

批量设置多个键值对。原子性操作，要么全部成功，要么全部失败。

**参数：**
- `mapping` (Dict[str, Any]): 键值字典 `{key: value, ...}`

**返回值：**
- `bool`: True 表示设置成功

**示例：**
```python
rc.mset({
    "user:1:name": "张三",
    "user:1:age": "30",
    "user:1:city": "北京"
})
```

#### mget(keys)

批量获取多个键的值。

**参数：**
- `keys` (List[str]): 键名列表

**返回值：**
- `List[Optional[str]]`: 值列表，键不存在的位置返回 None

**示例：**
```python
rc.mset({"a": "1", "b": "2", "c": "3"})
values = rc.mget(["a", "b", "d"])
# 返回：["1", "2", None]
```

#### incr(key, amount=1)

递增计数器。将键存储的数字增加指定值，如果键不存在，会先初始化为 0 再增加。

**参数：**
- `key` (str): 键名
- `amount` (int): 增加的数值，默认 1

**返回值：**
- `int`: 增加后的值

**示例：**
```python
rc.set("counter", 10)
rc.incr("counter")      # 返回 11
rc.incr("counter", 5)   # 返回 16

# 键不存在时从 0 开始
rc.incr("new_counter")  # 返回 1
```

#### decr(key, amount=1)

递减计数器。将键存储的数字减少指定值，如果键不存在，会先初始化为 0 再减少。

**参数：**
- `key` (str): 键名
- `amount` (int): 减少的数值，默认 1

**返回值：**
- `int`: 减少后的值

**示例：**
```python
rc.set("counter", 10)
rc.decr("counter")      # 返回 9
rc.decr("counter", 3)   # 返回 6
```

---

### Hash 哈希表操作

#### hset(name, key, value)

设置哈希表字段值。

**参数：**
- `name` (str): 哈希表名
- `key` (str): 字段名
- `value` (Any): 字段值

**返回值：**
- `int`: 1 表示新字段，0 表示更新已有字段

**示例：**
```python
rc.hset("user:1", "name", "张三")  # 返回 1，新字段
rc.hset("user:1", "age", 30)      # 返回 1，新字段
rc.hset("user:1", "name", "李四")  # 返回 0，更新已有字段
```

#### hget(name, key)

获取哈希表字段值。

**参数：**
- `name` (str): 哈希表名
- `key` (str): 字段名

**返回值：**
- `Optional[str]`: 字段值，字段不存在返回 None

**示例：**
```python
rc.hset("user:1", "name", "张三")
name = rc.hget("user:1", "name")   # "张三"
email = rc.hget("user:1", "email") # None，字段不存在
```

#### hmset(name, mapping)

批量设置哈希表多个字段。

**参数：**
- `name` (str): 哈希表名
- `mapping` (Dict[str, Any]): 字段字典 `{field: value, ...}`

**返回值：**
- `bool`: True 表示设置成功

**示例：**
```python
rc.hmset("user:1", {
    "name": "张三",
    "age": 30,
    "city": "北京"
})
```

#### hgetall(name)

获取哈希表所有字段和值。

**参数：**
- `name` (str): 哈希表名

**返回值：**
- `Dict[str, str]`: 字典 `{field: value, ...}`，哈希表不存在返回空字典

**示例：**
```python
rc.hmset("user:1", {"name": "张三", "age": "30"})
user = rc.hgetall("user:1")
# 返回：{"name": "张三", "age": "30"}

# 哈希表不存在
empty = rc.hgetall("user:999")
# 返回：{}
```

#### hdel(name, *keys)

删除哈希表字段。

**参数：**
- `name` (str): 哈希表名
- `*keys` (str): 要删除的字段名

**返回值：**
- `int`: 成功删除的字段数量

**示例：**
```python
rc.hmset("user:1", {"name": "张三", "age": "30", "city": "北京"})
rc.hdel("user:1", "city")           # 返回 1
rc.hdel("user:1", "name", "age")    # 返回 2
```

---

### List 列表操作

#### lpush(name, *values)

从列表左侧插入元素。

**参数：**
- `name` (str): 列表名
- `*values` (Any): 要插入的值

**返回值：**
- `int`: 插入后列表的长度

**示例：**
```python
rc.lpush("queue", "task1")