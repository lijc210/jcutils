from src.api.conn_pool import apocalypse_client


def query():
    res = apocalypse_client.query("select * from upd_auto_screen_component limit 10")
    print(res)


query()
# res = apocalypse_client.query("select * from upd_auto_screen_component limit 10")
# print(res)

# sql = "insert into flink_hw_source(id,name,age,status) values(%s,%s,%s,%s)"
# data_list = [[1,"a",20,1],
#              [2,"b",20,1]
#              ]
# apocalypse_client.executemany(sql,data_list)


# sql = """
# insert into upd_dianchi_users(id,user_name,nick_name,group_id,group_name,phone_no,
# email,user_type,`status`,province,city,shop_code,employee_no)
# select t1.id,t1.user_name,t1.nick_name,t1.group_id,t1.group_name,t1.phone_no,
# t1.email,t1.user_type,t1.`status`,t1.province,t1.city,t1.shop_code,t1.employee_no
# from upd_dianchi_users_1687622400000 t1
# left join upd_dianchi_users t2
# on t1.user_name = t2.user_name
# where t2.user_name is null
# """
# apocalypse_client.execute(sql)

# with open("api/log/sql.txt") as f:
#     for line in f.readlines():
#         sql = line.strip()
#         print(sql)
#         apocalypse_client.execute(sql)
