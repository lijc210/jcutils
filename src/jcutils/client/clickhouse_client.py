from clickhouse_driver import connect
from clickhouse_driver.dbapi.extras import DictCursor


class ClickhouseClient:
    def __init__(self, conn_dict, charset="utf8", cursorclass="dict"):
        self.host = conn_dict["host"]
        self.user = conn_dict["user"]
        self.passwd = conn_dict["passwd"]
        self.db = conn_dict["db"]
        self.charset = charset
        self.port = conn_dict["port"]
        self.cursorclass = cursorclass
        self.max_execution_time = 420

    def conn(self):
        conn = connect(
            host=self.host,
            user=self.user,
            password=self.passwd,
            database=self.db,
            port=self.port,
            settings={"max_execution_time": self.max_execution_time}
            if hasattr(self, "max_execution_time")
            else None,
        )
        if self.cursorclass == "dict":
            cursor = conn.cursor(DictCursor)
        else:
            cursor = conn.cursor()
        return conn, cursor

    def close(self, cursor, conn):
        cursor.close()
        conn.close()

    def query(self, sql, max_execution_time=None):
        if max_execution_time is not None:
            self.max_execution_time = max_execution_time
        conn, cursor = self.conn()
        cursor.execute(sql)
        results = cursor.fetchall()
        self.close(cursor, conn)
        return results

    def query_cursor(self, sql):
        """
        游标查询，需要返回大数量时使用
        使用方法：

        # 要查询的 SQL 语句
        sql = "SELECT * FROM your_table LIMIT 10000"

        # 执行游标查询
        cursor = ck_client.query_cursor(sql)

        # 逐步获取查询结果
        while True:
            row = cursor.fetchone()
            if not row:
                break
            print(row)  # 处理每一行数据

        # 关闭游标（不是必需，但是最好在使用完毕后关闭游标）
        cursor.close()

        :param sql:
        :return:
        """
        conn, cursor = self.conn()
        cursor.execute(sql)
        return cursor

    def execute(self, sql):
        """
        INSERT INTO table_name ( field1, field2,...fieldN )
                       VALUES
                       ( value1, value2,...valueN );
        :param sql:
        :return:
        """
        conn, cursor = self.conn()
        cursor.execute(sql)
        self.conn.commit()
        self.close(cursor, conn)

    def executemany(self, sql, sqlDataList):
        # tests = [['a','b','c'],['d','f','e']]
        conn, cursor = self.conn()
        cursor.executemany(sql, sqlDataList)
        lastrowid = cursor.lastrowid
        self.conn.commit()
        self.close(cursor, conn)
        return lastrowid

    # def __del__(self):
    #     cursor.close()
    #     self.conn.close()


if __name__ == "__main__":
    CK_DB = {}
    ck_client = ClickhouseClient(conn_dict=CK_DB)
    sql = "select * from dm_member_info_label limit 10"
    print(ck_client.query(sql))
    # mysql_client = MySqlClient(conn_dict=WORD_DB, cursorclass="ss_dict")
    # sql = "select * from spider_data.question where source='太平洋'"
    # for x in mysql_client.query_cursor(sql):
    #     print(x)
