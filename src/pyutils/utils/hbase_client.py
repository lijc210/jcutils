"""
Created on 2016/6/28
@author: lijc210@163.com
Desc: 功能描述。
"""

import happybase


class HbaseClient:
    def __init__(
        self, host="10.10.23.11", port=9090, timeout=120000, size=20, compat="0.98"
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.size = size
        self.compat = compat
        self.pool = happybase.ConnectionPool(
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
            self.pool = happybase.ConnectionPool(
                size=self.size * 2,
                host=self.host,
                port=self.port,
                timeout=self.timeout,
                compat=self.compat,
            )
        return self.pool.connection()

    def tables(self):
        """

        :return:
        """
        with self.conn() as conn:
            tables = conn.tables()
            return tables

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
            row = table.row(key, columns=columns)
            return row

    def gets(self, table_name="", keys="", cols="info", columns=None):
        # table_name 表名
        # key 行键（user_id对应的值）
        # cols 列簇名
        # columns 期望的返回列值
        if columns is None:
            columns = []
        with self.conn() as conn:
            table = conn.table(table_name)
            columns = ["{}:{}".format(cols, column) for column in columns]
            rows = table.rows(keys, columns=columns)
            return rows

    def scan(
        self,
        table_name="",
        cols="info",
        filter=None,
        limit=10,
        columns=None,
        row_start=None,
        row_stop=None,
    ):
        """

        :param table_name: 表名
        :param cols: 列簇名
        :param filter: 查询条件
        :param limit: 期望的返回列值
        :param columns:
        :param row_start:
        :param row_stop:
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
                )
            else:
                result = table.scan(
                    limit=limit, columns=columns, row_start=row_start, row_stop=row_stop
                )
            return result

    def delete(self, table_name=None, key=None):
        """
        删除一个rowkey
        :param table_name:
        :param key:
        :return:
        """
        conn = self.conn()
        table = conn.table(table_name)
        result = table.delete(key)
        conn.close()
        return result

    def put(self, table_name=None, key=None, data=None):
        """
        单个提交数据
        :return:
        """
        with self.conn() as conn:
            table = conn.table(table_name)
            table.put(key, data)

    def batch_put(self, table_name=None, key_data_dict=None):
        """
        批量提交数据
        :return:
        """
        with self.conn() as conn:
            table = conn.table(table_name)
            with table.batch() as bat:
                for key, data in key_data_dict.items():
                    bat.put(key, data)

    def batch_delete(self, keys, table_name=""):
        """
        批量提交数据
        :return:
        """
        with self.conn() as conn:
            table = conn.table(table_name)
            with table.batch() as bat:
                for key in keys:
                    bat.delete(key)


if __name__ == "__main__":
    hbase_client = HbaseClient(host="10.10.23.11", port=9090, timeout=120000, size=20)
    print(hbase_client.tables())
    # print(hbase_client.get(table_name='tag', key='A2026', columns=["data_value"]))
    # print(hbase_client.pool._queue.qsize())
    # print hbase_client.scan('tag', 'user_mobile', "556bf879edadb0118901fac74dbd4627")
    # print hbase_client.scan(table_name='user_crm_tag',
    # filter_data=[('user_mobile', "556bf879edadb0118901fac74dbd4627")])
    # for x, y in hbase_client.scan(table_name='attrresult:tag_quality_v9_news', limit=None, columns=[]):
    #     print(x, y)

    # for x,y in  hbase_client.scan(table_name='tag',filter_data=[('tag_class','用户基础标签表')],
    # columns=["tag_class","tag_name","hbasetable","data_class"],limit=None):
    #     print x,y

    # for x,y in  hbase_client.scan_timestamp(table_name='user_crm_tag',
    # columns=["lately_12month_crm_service_num"], batch_size=1000):
    #     print x,y

    # print hbase_client.gets(table_name='user_base_info_new', keys=["100000024", "754"],
    # columns=["phone_city","substation","ip_city"])
    # print hbase_client.gets(table_name='city_code_yzh', keys=["上海"], columns=["city_code"])
