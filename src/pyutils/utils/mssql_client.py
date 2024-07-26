from typing import Any
import pymssql


class MsSqlClient:
    def __init__(self, conn_dict, charset="utf8", cursorclass="dict"):
        self.host = conn_dict["host"]
        self.user = conn_dict["user"]
        self.passwd = conn_dict["passwd"]
        self.db = conn_dict["db"]
        self.charset = charset
        self.port = conn_dict["port"]
        self.cursorclass = cursorclass
        self.conn, self.cursor = self.connection()

    def check_connection(self):
        try:
            self.cursor.execute("SELECT 1 AS test_column")
        except Exception as e:
            print("Unexpected error: ", e)
            print("Connection lost, reconnecting...")
            self.conn, self.cursor = self.connection()

    def connection(self):
        conn = pymssql.connect(
            host=self.host,
            user=self.user,
            password=self.passwd,
            database=self.db,
            charset=self.charset,
            port=self.port,
            autocommit=True,
        )
        if self.cursorclass == "dict":
            cursor = conn.cursor(as_dict=True)
        else:
            cursor = conn.cursor()
        return conn, cursor

    def query(self, sql):
        self.check_connection()
        self.cursor.execute(sql)
        results: list[tuple[Any, ...]] | None = self.cursor.fetchall()
        self.conn.close()
        return results

    def query_cursor(self, sql):
        """
        游标查询，需要返回大数量时使用
        :param sql:
        :return:
        """
        self.check_connection()
        self.cursor.execute(sql)
        self.conn.close()
        return self.cursor

    def execute(self, sql):
        """
        INSERT INTO table_name ( field1, field2,...fieldN )
                       VALUES
                       ( value1, value2,...valueN );
        :param sql:
        :return:
        """
        self.check_connection()
        self.cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def executemany(self, sql, sqlDataList):
        # tests = [['a','b','c'],['d','f','e']]
        self.check_connection()
        self.cursor.executemany(sql, sqlDataList)
        lastrowid = self.cursor.lastrowid
        self.conn.commit()
        self.conn.close()
        return lastrowid

    # def __del__(self):
    #     self.cursor.close()
    #     self.conn.close()


if __name__ == "__main__":
    MSSQL_DB = {
        "host": "47.94.219.54",
        "user": "xxxxx",
        "passwd": "9o8l&JPQ*c_M^fxxxx",
        "db": "AIS20201114183546",
        "port": 1433,
    }
    mssql_client = MsSqlClient(conn_dict=MSSQL_DB)
    sql = "select top 10 * from dbo.t_pur_requisition"
    print(mssql_client.query(sql))
