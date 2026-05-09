"""
@File    :   sqlite3_client.py
@Time    :   2016/05/10
@Author  :   lijc210@163.com
@Desc    :
SQLite3 连接客户端，内部使用 with 上下文管理器自动管理连接
支持普通查询和流式查询
"""

import logging
import sqlite3
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union

logger = logging.getLogger(__name__)


class Sqlite3Client:
    def __init__(
        self,
        db_path: str,
        cursorclass: str = "tuple",
        isolation_level: Optional[str] = None,
        check_same_thread: bool = False,
    ) -> None:
        """
        SQLite3 连接客户端

        :param db_path: 数据库文件路径
        :param cursorclass: 游标类型，tuple/dict
        :param isolation_level: 隔离级别，None=自动提交
        :param check_same_thread: 是否检查同一线程，默认 False
        """
        self.db_path = db_path
        self.cursorclass = cursorclass
        self.isolation_level = isolation_level
        self.check_same_thread = check_same_thread

    @staticmethod
    def dict_factory(cursor: Any, row: Tuple[Any, ...]) -> Dict[str, Any]:
        """
        将行数据转换为字典

        :param cursor: 游标对象
        :param row: 行数据
        :return: 字典格式的行数据
        """
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def get_connection(self) -> Any:
        """
        获取一个数据库连接

        :return: 连接对象
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=self.check_same_thread)
        conn.isolation_level = self.isolation_level

        # 设置行工厂
        if self.cursorclass == "dict":
            conn.row_factory = self.dict_factory

        return conn

    def get_cursor(self, conn: Any) -> Any:
        """
        获取游标对象

        :param conn: 数据库连接
        :return: 游标对象
        """
        cursor = conn.cursor()
        return cursor

    def fetchone(
        self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Optional[Union[Dict[str, Any], Tuple[Any, ...]]]:
        """
        查询单条记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 单条记录
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                result = cursor.fetchone()
                return result
            except sqlite3.Error as e:
                logger.error(f"fetchone 查询失败: {e}")
                raise e
            finally:
                cursor.close()

    def fetchmany(
        self, sql: str, batch_size: int = 100, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Generator[Any, None, None]:
        """
        分批获取所有数据，每批返回一次

        :param sql: SQL 语句
        :param batch_size: 每批的数量，默认 100
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，每次返回一批数据
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                while True:
                    batch = cursor.fetchmany(batch_size)
                    if not batch:
                        break
                    yield batch
            except sqlite3.Error as e:
                logger.error(f"fetchmany 查询失败: {e}")
                raise e
            finally:
                cursor.close()

    def fetchall(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> List[Any]:
        """
        查询所有记录
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 所有记录列表
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                results = cursor.fetchall()
                return results
            except sqlite3.Error as e:
                logger.error(f"fetchall 查询失败: {e}")
                raise e
            finally:
                cursor.close()

    def fetch_iter(
        self, sql: str, batch_size: int = 1000, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None
    ) -> Generator[Any, None, None]:
        """
        流式查询，需要返回大数量时使用
        逐批获取数据，避免内存溢出
        :param sql: SQL 语句
        :param batch_size: 每批获取的记录数，默认 1000
        :param args: 参数化查询的参数，元组或字典类型
        :return: 生成器，可以迭代获取每条记录
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                while True:
                    results = cursor.fetchmany(batch_size)
                    if not results:
                        break
                    for row in results:
                        yield row
            except sqlite3.Error as e:
                logger.error(f"fetch_iter 查询失败: {e}")
                raise e
            finally:
                cursor.close()

    def execute(self, sql: str, args: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None) -> int:
        """
        执行 SQL 语句（insert/update/delete 等）
        :param sql: SQL 语句
        :param args: 参数化查询的参数，元组或字典类型
        :return: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(sql, args)
                if self.isolation_level is not None:
                    conn.commit()
                return cursor.rowcount
            except sqlite3.Error as e:
                if self.isolation_level is not None:
                    conn.rollback()
                logger.error(f"execute 执行失败: {e}")
                raise e
            finally:
                cursor.close()

    def executemany(self, sql: str, sqlDataList: Sequence[Sequence[Any]]) -> int:
        """
        批量执行 SQL 语句
        :param sql: SQL 语句
        :param sqlDataList: 数据列表，如 [['a','b','c'], ['d','f','e']]
        :return: lastrowid
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.executemany(sql, sqlDataList)
                if self.isolation_level is not None:
                    conn.commit()
                lastrowid = getattr(cursor, "lastrowid", 0)
                return lastrowid
            except sqlite3.Error as e:
                if self.isolation_level is not None:
                    conn.rollback()
                logger.error(f"executemany 执行失败: {e}")
                raise e
            finally:
                cursor.close()

    def transaction(self, sql_list: List[str]) -> None:
        """
        在事务中执行多个 SQL 语句

        :param sql_list: SQL 语句列表
        """
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                for sql in sql_list:
                    cursor.execute(sql)
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                logger.error(f"事务执行失败: {e}")
                raise e
            finally:
                cursor.close()

    def __enter__(self) -> "Sqlite3Client":
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """退出上下文"""
        pass


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 创建测试数据库
    sqlite3_client = Sqlite3Client(db_path="tests.db", cursorclass="dict")

    # 创建测试表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS COMPANY (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME TEXT NOT NULL,
        AGE INTEGER,
        ADDRESS TEXT,
        SALARY REAL
    )
    """
    sqlite3_client.execute(create_table_sql)

    # 插入示例
    insert_sql = "INSERT INTO COMPANY (NAME, AGE, ADDRESS, SALARY) VALUES (?, ?, ?, ?)"
    sqlite3_client.execute(insert_sql, ("Paul", 32, "California", 20000.00))
    sqlite3_client.execute(insert_sql, ("Allen", 25, "Texas", 15000.00))
    sqlite3_client.execute(insert_sql, ("Teddy", 23, "Norway", 20000.00))

    # 批量插入示例
    batch_data = [
        ("Mark", 25, "Rich-Mond", 65000.00),
        ("David", 27, "Texas", 85000.00),
        ("Kim", 22, "South-Hall", 45000.00),
    ]
    sqlite3_client.executemany(insert_sql, batch_data)

    # 查询单条记录
    sql = "SELECT * FROM COMPANY WHERE ID = 1"
    result = sqlite3_client.fetchone(sql)
    print("fetchone:", result)

    # 分批获取数据
    total_count = 0
    for batch in sqlite3_client.fetchmany("SELECT * FROM COMPANY", batch_size=2):
        print("当前批次数量:", len(batch))
        total_count += len(batch)
    print("fetchmany total:", total_count)

    # 查询所有记录
    results = sqlite3_client.fetchall("SELECT * FROM COMPANY")
    print("fetchall count:", len(results))

    # 流式查询
    count = 0
    for row in sqlite3_client.fetch_iter("SELECT * FROM COMPANY"):
        count += 1
    print("fetch_iter:", count)

    # 兼容旧版 API
    results = sqlite3_client.query("SELECT * FROM COMPANY")
    print("query count:", len(results))

    # 使用 tuple 游标
    sqlite3_client_tuple = Sqlite3Client(db_path="tests.db", cursorclass="tuple")
    result_tuple = sqlite3_client_tuple.fetchone("SELECT * FROM COMPANY WHERE ID = 1")
    print("fetchone (tuple):", result_tuple)

    # 事务示例
    transaction_sqls = [
        "UPDATE COMPANY SET SALARY = SALARY * 1.1 WHERE NAME = 'Paul'",
        "UPDATE COMPANY SET SALARY = SALARY * 1.05 WHERE NAME = 'Allen'",
    ]
    sqlite3_client.transaction(transaction_sqls)
    print("事务执行成功")
