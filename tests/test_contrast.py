from src.jcutils.utils.clickhouse_client import ClickhouseClient

CK_DB1 = {
    "host": "clickhouse.gqshintra.com",
    "user": "ck_readonly",
    "passwd": "shgqsh2020",
    "db": "ads",
    "port": 9000,
}

CK_DB2 = {
    "host": "10.193.58.255",
    "user": "biread",
    "passwd": "YYds78suhdh%899",
    "db": "ads",
    "port": 9000,
}

ck_client1 = ClickhouseClient(conn_dict=CK_DB1)
ck_client2 = ClickhouseClient(conn_dict=CK_DB2)

sql = "select * FROM system.tables where engine = 'Distributed'"

res1 = ck_client1.query(sql)
tables1 = [row[0] + "." + row[1] for row in res1]

res2 = ck_client2.query(sql)
tables2 = [row[0] + "." + row[1] for row in res2]

print(set(tables1) - set(tables2))

print("*" * 20)

print(set(tables2) - set(tables1))

table_num_dict1 = {}
for table1 in tables1:
    try:
        sql11 = f"select count(1) from {table1}"
        res11 = ck_client1.query(sql11)
        table_num_dict1[table1] = res11[0][0]
    except Exception:
        print("aaaaa")
        print(table1)

table_num_dict2 = {}
for table2 in tables2:
    try:
        sql22 = f"select count(1) from {table2}"
        res22 = ck_client2.query(sql22)
        table_num_dict2[table2] = res22[0][0]
    except Exception:
        print("bbbbb")
        print(table2)

for table, num1 in table_num_dict1.items():
    num2 = table_num_dict2.get(table, 0)
    if num1 != num2:
        print(table + "\t" + str(num1) + "\t" + str(num2))
