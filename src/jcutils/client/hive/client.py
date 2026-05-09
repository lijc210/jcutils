"""
Created on 2016/11/22 0022 17:31
@author: lijc210@163.com
Desc: python下远程查询hive
"""

import sys

if sys.version_info < (2, 7):
    import pyhs2
else:
    from pyhive import hive


class HiveClient:
    def __init__(self, host="10.10.23.11", port=10000, authMechanism="PLAIN", username="lijicong"):
        self.host = host
        self.port = port
        self.authMechanism = authMechanism
        self.username = username

    def Conn(self):
        if sys.version_info < (2, 7):
            conn = pyhs2.connect(
                host=self.host,
                port=self.port,
                authMechanism=self.authMechanism,
                user=self.username,
            )
            cursor = conn.cursor()
        else:
            conn = hive.Connection(host=self.host, port=self.port, username=self.username)
            cursor = conn.cursor()
            return conn, cursor
        return conn, cursor

    def query(self, sql):
        conn, cursor = self.Conn()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results


if __name__ == "__main__":
    hive_client = HiveClient()
    sql = "select keywords from dw.kn1_tf_documents_idf limit 10"
    print(hive_client.query(sql))
