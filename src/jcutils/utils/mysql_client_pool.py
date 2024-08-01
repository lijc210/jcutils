"""
@File    :   mysql_client_pool.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :
以下情况需要用连接池：
1. 常驻进程并且查询频率高，频繁创建，关闭连接，影响性能
2. 多线程并发查询，频繁创建，关闭连接，会导致报错
"""

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.cursors import Cursor, DictCursor, SSCursor, SSDictCursor


class MySqlClientPool:
    def __init__(
        self,
        conn_dict,
        charset="utf8",
        cursorclass="dict",
        maxconnections=100,
        maxcached=10,
    ):
        if cursorclass == "dict":
            CursorClass = DictCursor
        elif cursorclass == "ss_dict":
            CursorClass = SSDictCursor
        elif cursorclass == "ss_list":
            CursorClass = SSCursor
        else:
            CursorClass = Cursor

        self.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=maxconnections,  # 连接池允许的最大连接数，0和None表示不限制连接数
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
            port=conn_dict["port"],
            user=conn_dict["user"],
            password=conn_dict["passwd"],
            database=conn_dict["db"],
            charset=charset,
            cursorclass=CursorClass,
        )

    def get_connection(self):
        conn = self.pool.connection()
        cursor = conn.cursor()
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
        """
        游标查询，需要返回大数量时使用
        :param sql:
        :return:
        """
        conn, cursor = self.get_connection()
        cursor.execute(sql)
        return cursor

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
        # tests = [['a','b','c'],['d','f','e']]
        try:
            cursor.executemany(sql, sqlDataList)
            # lastrowid = cursor.lastrowid  # 连接池下不支持# 连接池下不支持
            conn.commit()
            # return lastrowid
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    WORD_DB = {
        "host": "10.10.11.244",
        "user": "xxxxx",
        "passwd": "@biusxxxx3",
        "db": "userdata",
        "port": 3309,
    }
    mysql_client = MySqlClientPool(conn_dict=WORD_DB, cursorclass="dict")
    sql = "select * from userdata.dict_professionalterm limit 10"
    print(mysql_client.query(sql))
    # mysql_client = MySqlClient(conn_dict=WORD_DB, cursorclass="ss_dict")
    # sql = "select * from spider_data.question where source='太平洋'"
    # for x in mysql_client.query_cursor(sql):
    #     print(x)
