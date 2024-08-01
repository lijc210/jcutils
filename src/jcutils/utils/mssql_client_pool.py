"""
@File    :   mssql_client_pool.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :
以下情况需要用连接池：
1. 常驻进程并且查询频率高，频繁创建，关闭连接，影响性能
2. 多线程并发查询，频繁创建，关闭连接，会导致报错
"""

import pymssql
from dbutils.pooled_db import PooledDB


class MsSqlClientPool:
    def __init__(self, conn_dict, max_connections=5, maxcached=10, charset="utf8", cursorclass="dict"):
        self.pool = PooledDB(
            creator=pymssql,  # 使用链接数据库的模块
            maxconnections=max_connections,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=10,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=maxcached,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=100,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的
            # threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=0,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested,
            # 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host=conn_dict["host"],
            user=conn_dict["user"],
            password=conn_dict["passwd"],
            database=conn_dict["db"],
            charset=charset,
            port=conn_dict["port"],
        )
        self.cursorclass = cursorclass

    def get_connection(self):
        conn = self.pool.connection()
        cursor = conn.cursor(as_dict=True) if self.cursorclass == "dict" else conn.cursor()
        return conn, cursor

    def query(self, sql):
        conn, cursor = self.get_connection()
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
            conn.close()

    def query_cursor(self, sql):
        conn, cursor = self.get_connection()
        try:
            cursor.execute(sql)
            return cursor
        finally:
            conn.close()

    def execute(self, sql):
        conn, cursor = self.get_connection()
        try:
            cursor.execute(sql)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def executemany(self, sql, sqlDataList):
        conn, cursor = self.get_connection()
        try:
            cursor.executemany(sql, sqlDataList)
            lastrowid = cursor.lastrowid
            conn.commit()
            return lastrowid
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    MSSQL_DB = {
        "host": "47.94.219.54",
        "user": "xxxxxxxx",
        "passwd": "9o8l&JPQ*c_M^fxxxx",
        "db": "AIS2020111418xxxx",
        "port": 1433,
    }
    mssql_client = MsSqlClientPool(conn_dict=MSSQL_DB)
    sql = "select top 10 * from dbo.t_pur_requisition"
    print(mssql_client.query(sql))
