"""
Created on 2016/11/22 0022 17:31
@author: lijc210@163.com
Desc: python下远程查询hive
"""

try:
    from pyhive import hive
except ModuleNotFoundError:
    raise ImportError('请先安装：pip install pyhive thrift thrift_sasl or uv add "pyhive pyhive thrift thrift_sasl"')
except Exception as e:
    raise ImportError(f"pyhive 导入失败: {e}")


class HiveClient:
    def __init__(self, host="10.10.23.11", port=10000, authMechanism="PLAIN", username="lijicong"):
        self.host = host
        self.port = port
        self.authMechanism = authMechanism
        self.username = username

    def Conn(self):
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
