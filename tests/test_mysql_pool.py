from src.api.conn_pool import apocalypse_client

res = apocalypse_client.query("select * from upd_auto_screen_component limit 10")
print(res)

sql = "insert into flink_hw_source(id,name,age,status) values(%s,%s,%s,%s)"
data_list1 = [[5, "a", 20, 1], [6, "b", 20, 1]]
data_list2 = [[7, "a", 20, 1], [8, "b", 20, 1]]
lastrowid = apocalypse_client.executemany(sql, data_list1)
print(lastrowid)

apocalypse_client.executemany(sql, data_list2)
