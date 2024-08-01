"""
Created on 2016/6/28
@author: lijc210@163.com
Desc: 功能描述。。thrift2解决thrift1不能并发访问的问题，并且解决自己写的访问速度慢的问题，支持timeRange
"""

import easybase
import thriftpy2.protocol.cybin
import thriftpy2.thrift


class HbaseThrift2Client:
    def __init__(
        self, host="10.10.23.11", port=9091, timeout=120000, size=20, compat="0.98"
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.size = size
        self.compat = compat
        self.pool = easybase.ConnectionPool(
            size=self.size,
            host=self.host,
            port=self.port,
            timeout=self.timeout,
            compat=self.compat,
        )
        print("hbase初始化为", self.pool._queue.qsize())

    def conn(self):
        """

        :return:
        """
        if self.pool is None:
            self.pool = easybase.ConnectionPool(
                size=self.size * 2,
                host=self.host,
                port=self.port,
                timeout=self.timeout,
                compat=self.compat,
            )
        return self.pool.connection()

    def get(self, table_name="", key="", cols="info", columns=None):
        # table_name 表名
        # key 行键（user_id对应的值）
        # cols 列簇名
        # columns 期望的返回列值
        if columns is None:
            columns = []
        with self.conn() as conn:
            table = conn.table(table_name)
            columns = ["{}:{}".format(cols, column) for column in columns]
            try:
                row = table.row(key, columns=columns)
            except thriftpy2.protocol.cybin.ProtocolError:  # 多进程中会报错
                conn._refresh_thrift_client()
                row = table.row(key, columns=columns)
            except thriftpy2.thrift.TApplicationException:
                conn._refresh_thrift_client()
                row = table.row(key, columns=columns)
            return {
                k.encode(): v.encode() if isinstance(v, str) else v
                for k, v in row.items()
                if k
            }  # 和hbase_client.py保持一致

    def gets(self, table_name="", keys="", cols="info", columns=None):
        # table_name 表名
        # key 行键（user_id对应的值）
        # cols 列簇名
        # columns 期望的返回列值
        if columns is None:
            columns = []
        with self.conn() as conn:
            table = conn.table(table_name)
            # columns = ['{0}:{1}'.format(cols, column) for column in columns]
            try:
                rows = table.rows(keys)
            except thriftpy2.protocol.cybin.ProtocolError:  # 多进程中会报错
                conn._refresh_thrift_client()
                rows = table.rows(keys)
            except thriftpy2.thrift.TApplicationException:
                conn._refresh_thrift_client()
                rows = table.rows(keys)
            result = [
                (rowkey.encode(), {k.encode(): v.encode() for k, v in data.items()})
                for rowkey, data in rows
                if rowkey
            ]  # 和hbase_client.py保持一致

            return result

    def scan(
        self,
        table_name="",
        cols="info",
        filter=None,
        limit=10,
        columns=None,
        row_start=None,
        row_stop=None,
        timerange=None,
    ):
        """

        :param table_name: 表名
        :param cols: 列簇名
        :param filter: 查询条件
        :param limit: 期望的返回列值
        :param columns:
        :param row_start:
        :param row_stop:
        :param timeRange:时间范围
        :return:
        """
        if columns is None:
            columns = []
        with self.conn() as conn:
            table = conn.table(table_name)
            columns = ["{}:{}".format(cols, column) for column in columns]
            if filter:
                result = table.scan(
                    filter=" AND ".join(filter),
                    limit=limit,
                    columns=columns,
                    row_start=row_start,
                    row_stop=row_stop,
                    timerange=timerange,
                )
            else:
                result = table.scan(
                    limit=limit,
                    columns=columns,
                    row_start=row_start,
                    row_stop=row_stop,
                    timerange=timerange,
                )
            return result


if __name__ == "__main__":
    hbase_thrift2_client = HbaseThrift2Client(
        host="10.193.51.96", port=21305, compat="2.2.0"
    )
    # res = hbase_thrift2_client.get(table_name="tag", key="A2024", cols="info",
    # columns=["tag_class", "tag_class_code"])
    # print(res)

    # res = hbase_thrift2_client.gets(table_name="tag", keys=["A2024", "A2025"])
    # print(res)

    # res = hbase_thrift2_client.get(table_name="dim_store_shop", key="110126", cols="cf", columns=["id"])
    # print(res)

    # for x,y in  hbase_thrift2_client.scan(table_name='dim_store_shop', cols="cf",
    # filter=None, columns=["id"],limit=None):
    #     print (x,y)

    i = 1
    for _x, _y in hbase_thrift2_client.scan(
        table_name="dim_store_shop",
        cols="cf",
        filter=None,
        columns=["id"],
        limit=None,
        timerange=(1668873600000, 1669564800000),
    ):
        i += 1
    print(i)
