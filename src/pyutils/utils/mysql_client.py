import pymysql
from pymysql.cursors import DictCursor


class MySqlClient:
    def __init__(self, conn_dict, charset="utf8", cursorclass="dict"):
        self.host = conn_dict["host"]
        self.user = conn_dict["user"]
        self.passwd = conn_dict["passwd"]
        self.db = conn_dict["db"]
        self.charset = charset
        self.port = conn_dict["port"]
        self.cursorclass = cursorclass

    def conn(self):
        if self.cursorclass == "dict":
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.db,
                charset=self.charset,
                port=self.port,
                cursorclass=DictCursor,
                autocommit=True,
            )
        elif self.cursorclass == "ss_dict":
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.db,
                charset=self.charset,
                port=self.port,
                cursorclass=pymysql.cursors.SSDictCursor,
                autocommit=True,
            )
        elif self.cursorclass == "ss_list":
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.db,
                charset=self.charset,
                port=self.port,
                cursorclass=pymysql.cursors.SSCursor,
                autocommit=True,
            )
        else:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.db,
                charset=self.charset,
                port=self.port,
                autocommit=True,
            )
        cursor = conn.cursor()
        return conn, cursor

    def close(self, cursor, conn):
        cursor.close()
        conn.close()

    def ping(self):
        conn, cursor = self.conn()
        results = conn.ping()
        self.close(cursor, conn)
        return results

    def query(self, sql):
        conn, cursor = self.conn()
        cursor.execute(sql)
        results = cursor.fetchall()
        self.close(cursor, conn)
        return results

    def query_cursor(self, sql):
        """
        游标查询，需要返回大数量时使用
        :param sql:
        :return:
        """
        conn, cursor = self.conn()
        cursor.execute(sql)
        conn.close()
        return cursor

    def execute(self, sql):
        conn, cursor = self.conn()
        cursor.execute(sql)
        conn.commit()
        self.close(cursor, conn)

    def executemany(self, sql, sqlDataList):
        # tests = [['a','b','c'],['d','f','e']]
        conn, cursor = self.conn()
        cursor.executemany(sql, sqlDataList)
        lastrowid = getattr(cursor, "lastrowid", 0)
        conn.commit()
        self.close(cursor, conn)
        return lastrowid

    # def __del__(self):
    #     cursor.close()
    #     conn.close()


if __name__ == "__main__":
    WORD_DB = {
        "host": "10.10.11.244",
        "user": "xxxxx",
        "passwd": "@biusxxxx",
        "db": "userdata",
        "port": 3309,
    }
    mysql_client = MySqlClient(conn_dict=WORD_DB)
    sql = "select * from userdata.dict_professionalterm limit 10"
    print(mysql_client.query(sql))
    # mysql_client = MySqlClient(conn_dict=WORD_DB, cursorclass="ss_dict")
    # sql = "select * from spider_data.question where source='太平洋'"
    # for x in mysql_client.query_cursor(sql):
    #     print(x)
