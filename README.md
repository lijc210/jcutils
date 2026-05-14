# jcutils - Python 多功能工具库

一个高效封装的 Python 工具库，集成数据库客户端、云服务 API、消息队列及常用开发工具，助力快速开发与运维自动化。

## 特性

- 🚀 **开箱即用**：统一接口设计，降低学习成本
- 🛡️ **生产级代码**：内置连接池、异常重试、日志记录
- 📦 **模块化设计**：按需引用，无冗余依赖
- 📝 **完整类型注解**：Python 3.8+ 兼容，支持 IDE 智能提示

## 核心模块

### Client（客户端）

统一在 `jcutils.client` 包下，按功能模块化组织：

#### 数据库客户端
- **关系型数据库**
  - `mysql.client.MySqlClient` / `mysql.async_client.AsyncMySQLClient`：MySQL 客户端（同步/异步）
  - `postgres.client.PostgresClient` / `postgres.async_client.AsyncPostgresClient`：PostgreSQL 客户端（同步/异步）
  - `mssql.client.MsSqlClient`：SQL Server 客户端
  - `sqlite.client.Sqlite3Client`：SQLite 客户端
  - `odbc.client.PyodbcClient`：通用 ODBC 客户端

- **OLAP/大数据**
  - `clickhouse.client.ClickhouseClient`：ClickHouse 客户端
  - `presto.client.PrestoClient`：Presto/Trino 客户端
  - `hive.client.HiveClient`：Hive 客户端

- **NoSQL**
  - `mongo.client.MongoClient`：MongoDB 客户端
  - `redis.client.RedisClient` / `redis.async_client.AsyncRedisClient`：Redis 客户端（同步/异步）
  - `elasticsearch.client.EsClient` / `elasticsearch.client.EsClient6`：Elasticsearch 客户端（7.x/6.x）
  - `hbase.client.HbaseClient` / `hbase.thrift2_client.HbaseThrift2Client`：HBase 客户端

#### 云服务与存储
- `maxcompute.client.MaxComputeClient`：阿里云 MaxCompute（ODPS）
- `dataworks.client.DataworksClient`：阿里云 DataWorks
- `s3.client.S3Bucket`：AWS S3 兼容存储
- `qiniu.client.Qiniu`：七牛云存储
- `hdfs.client.HdfsClient`：HDFS 客户端

#### 消息与通信
- `kafka.client.KafkaClient`：Kafka 客户端
- `qyweixin.bot.QyWeixinBot` / `qyweixin.client.QyWeixinClient`：企业微信机器人/API
- `wecom.offiaccount.WeixinOffiaccount` / `wecom.qyapi.QYWeixinSend`：企业微信消息推送
- `weixin.client.WeixinClient`：微信公众号工具

#### 其他
- `ftp.client.FtpClient`：FTP 客户端
- `ldap.client.LdapClient`：LDAP 客户端
- `email.client.ImaplibClient`：IMAP 邮件客户端

### Utils（工具集）

所有工具位于 `jcutils.utils` 包下：

#### 日期时间
- `datetime_.py`：日期时间操作（转换、计算、范围查询）
- `relative_time.py`：相对时间计算（如"3分钟前"）
- `date_encoder.py`：日期 JSON 序列化
- `holiday.py`：节假日查询

#### 性能监控
- `run_time.py` / `run_func_time.py`：函数执行时间装饰器
- `run_line_time.py`：行级性能分析装饰器
- `run_log_time.py`：带日志的执行时间装饰器

#### 格式化与处理
- `format_utils.py`：字符串格式化（支持宽字符）
- `tabulate_utils.py`：表格美化输出
- `html.py` / `htmlstrip.py`：HTML 标签去除

#### 开发工具
- `try_except_.py`：异常捕获装饰器
- `logging_.py`：日志配置工具
- `tool_threading.py`：多线程工具
- `lazy_import.py`：懒加载模块导入
- `convert.py`：类型转换工具
- `built_in_tools.py`：pickle 序列化工具

#### 配置管理
- `config_holder.py`：配置持有器
- `config_loader.py`：配置加载器

#### 系统与网络
- `os_path.py` / `os_platform.py` / `platform_.py`：系统平台检测
- `nginx_log.py`：Nginx 日志分析
- `apscheduler_.py`：Cron 定时任务触发器
- `regeo.py`：高德地图逆地理编码

#### 通讯与集成
- `dingtalk.py` / `dingtalkoapi.py`：钉钉 API 客户端
- `nacos_client.py`：Nacos 配置中心客户端

## 安装

```bash
# 安装基础包
pip install jcutils
# 安装指定扩展
pip install jcutils[config]
pip install jcutils[mysql]
pip install jcutils[postgresql]
pip install jcutils[pymssql]
pip install jcutils[boto3]
pip install jcutils[redis]
pip install jcutils[kafka]
pip install jcutils[hdfs]
pip install jcutils[clickhouse]
pip install jcutils[alibabacloud]
pip install jcutils[huaweicloud]
pip install jcutils[sentry]
pip install jcutils[numpy]
pip install jcutils[elasticsearch]
# 安装所有
pip install jcutils[all]
```

## 快速开始

### 数据库查询

```python
from jcutils.client import ClickhouseClient

client = ClickhouseClient(host="localhost", user="default", passwd="", db="default")
result = client.execute("SELECT * FROM system.tables")
print(result)
```

### 消息推送

```python
from jcutils.client import QyWeixinBot

bot = QyWeixinBot()
bot.send_text("Alert: 服务器CPU负载超过90%",key="YOUR_WEBHOOK_KEY")
```

### 性能监控

```python
from jcutils.utils.run_func_time import run_time

@run_time
def slow_function():
    import time
    time.sleep(2)

slow_function()  # 输出执行时间
```

### 日期处理

```python
from jcutils.utils.datetime_ import day_ops, dt2ts, ts2dt

# 当前时间加一天
print(day_ops(days=1))

# 时间戳转换
print(ts2dt(1640995200))
```

## 贡献

欢迎提交 Issue 或 Pull Request！

## License

MIT
