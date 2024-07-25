# -*- coding:utf-8 -*-
"""
Created on 2016/5/10
@author: lijc210@163.com
Desc: 功能描述。
"""

import psycopg2
from psycopg2.extras import RealDictCursor


class PgClient:
    def __init__(
        self,
        conn_dict,
        cursor_factory=None,
    ):
        self.host = conn_dict["host"]
        self.user = conn_dict["user"]
        self.password = conn_dict["passwd"]
        self.database = conn_dict["db"]
        self.port = conn_dict["port"]
        self.cursor_factory = cursor_factory

    def Conn(self):
        conn = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
        )
        if self.cursor_factory == "dict":
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        return conn, cursor

    # 查询
    def query(self, sql):
        conn, cursor = self.Conn()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def executemany(self, sql, sqlDataList):
        # insert into ods_frame_db_com_department_mid(id,breadcrumb) values(%s,%s)
        # test = [[3,'c']]
        conn, cursor = self.Conn()
        cursor.executemany(sql, sqlDataList)
        # lastrowid = self.cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

    def execute(self, sql, extend=False):
        conn, cursor = self.Conn()
        if extend:
            cursor.execute("SET statement_timeout TO 0")
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()

    def execute_isolation(self, sql):
        conn, cursor = self.Conn()
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(0)
        cursor.execute(sql)
        conn.set_isolation_level(old_isolation_level)
        cursor.close()
        conn.close()


if __name__ == "__main__":
    conn_dict = {
        "host": "10.230.141.173",
        "user": "form_reader",
        "passwd": "xxxxxxxxxxxx",
        "db": "data",
        "port": 5432,
    }
    pg_client = PgClient(conn_dict, cursor_factory="dict")
    sql = """select ip_num,city from config.conf_ip_city_detail limit 10"""
    print(pg_client.query(sql))
