"""
@File    :   __init__.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :   None
"""

import importlib
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 仅供 IDE 静态分析，运行时不执行
    from .clickhouse.client import ClickhouseClient
    from .dataworks.client import DataworksClient
    from .elasticsearch.client import EsClient, EsClient6
    from .email.client import ImaplibClient
    from .ftp.client import FtpClient
    from .hbase.client import HbaseClient
    from .hbase.thrift2_client import HbaseThrift2Client
    from .hdfs.client import HdfsClient
    from .hive.client import HiveClient
    from .kafka.client import KafkaClient
    from .ldap.client import LdapClient
    from .maxcompute.client import MaxComputeClient
    from .mongo.client import MongoClient
    from .mssql.client import MsSqlClient
    from .mysql.async_client import AsyncMySQLClient
    from .mysql.client import MySqlClient
    from .odbc.client import PyodbcClient
    from .postgres.async_client import AsyncPostgresClient
    from .postgres.client import PostgresClient
    from .presto.client import PrestoClient
    from .qiniu.client import Qiniu
    from .qyweixin.bot import QyWeixinBot
    from .qyweixin.client import QyWeixinClient
    from .redis.async_client import AsyncRedisClient
    from .redis.client import RedisClient
    from .s3.client import S3Bucket
    from .sqlite.client import Sqlite3Client
    from .weixin.client import WeixinClient


def _lazy_import(module_path, class_names):
    """尝试导入，失败时返回占位函数"""
    try:
        mod = importlib.import_module(module_path, package=__name__)
        return tuple(getattr(mod, name) for name in class_names)
    except ImportError:
        msg = traceback.format_exc().strip().splitlines()[-1]  # 取最后一行，即 ImportError: x

        def _placeholder(*args, **kwargs):
            raise ImportError(msg)

        return tuple(_placeholder for _ in class_names)


(ClickhouseClient,) = _lazy_import(".clickhouse.client", ["ClickhouseClient"])
(DataworksClient,) = _lazy_import(".dataworks.client", ["DataworksClient"])
(EsClient, EsClient6) = _lazy_import(".elasticsearch.client", ["EsClient", "EsClient6"])
(ImaplibClient,) = _lazy_import(".email.client", ["ImaplibClient"])
(FtpClient,) = _lazy_import(".ftp.client", ["FtpClient"])
(HbaseClient,) = _lazy_import(".hbase.client", ["HbaseClient"])
(HbaseThrift2Client,) = _lazy_import(".hbase.thrift2_client", ["HbaseThrift2Client"])
(HdfsClient,) = _lazy_import(".hdfs.client", ["HdfsClient"])
(HiveClient,) = _lazy_import(".hive.client", ["HiveClient"])
(KafkaClient,) = _lazy_import(".kafka.client", ["KafkaClient"])
(LdapClient,) = _lazy_import(".ldap.client", ["LdapClient"])
(MaxComputeClient,) = _lazy_import(".maxcompute.client", ["MaxComputeClient"])
(MongoClient,) = _lazy_import(".mongo.client", ["MongoClient"])
(MsSqlClient,) = _lazy_import(".mssql.client", ["MsSqlClient"])
(AsyncMySQLClient,) = _lazy_import(".mysql.async_client", ["AsyncMySQLClient"])
(MySqlClient,) = _lazy_import(".mysql.client", ["MySqlClient"])
(PyodbcClient,) = _lazy_import(".odbc.client", ["PyodbcClient"])
(AsyncPostgresClient,) = _lazy_import(".postgres.async_client", ["AsyncPostgresClient"])
(PostgresClient,) = _lazy_import(".postgres.client", ["PostgresClient"])
(PrestoClient,) = _lazy_import(".presto.client", ["PrestoClient"])
(Qiniu,) = _lazy_import(".qiniu.client", ["Qiniu"])
(QyWeixinBot,) = _lazy_import(".qyweixin.bot", ["QyWeixinBot"])
(QyWeixinClient,) = _lazy_import(".qyweixin.client", ["QyWeixinClient"])
(AsyncRedisClient,) = _lazy_import(".redis.async_client", ["AsyncRedisClient"])
(RedisClient,) = _lazy_import(".redis.client", ["RedisClient"])
(S3Bucket,) = _lazy_import(".s3.client", ["S3Bucket"])
(Sqlite3Client,) = _lazy_import(".sqlite.client", ["Sqlite3Client"])
(WeixinClient,) = _lazy_import(".weixin.client", ["WeixinClient"])

__all__ = [
    "AsyncMySQLClient",
    "MySqlClient",
    "AsyncPostgresClient",
    "PostgresClient",
    "AsyncRedisClient",
    "RedisClient",
    "ClickhouseClient",
    "DataworksClient",
    "EsClient",
    "EsClient6",
    "ImaplibClient",
    "FtpClient",
    "HbaseClient",
    "HbaseThrift2Client",
    "HdfsClient",
    "HiveClient",
    "KafkaClient",
    "LdapClient",
    "MaxComputeClient",
    "MongoClient",
    "MsSqlClient",
    "PyodbcClient",
    "PrestoClient",
    "Qiniu",
    "S3Bucket",
    "Sqlite3Client",
    "QyWeixinClient",
    "QyWeixinBot",
    "WeixinClient",
]
