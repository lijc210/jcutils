from src.api.conn_pool import pg_client

res = pg_client.query("""select * from ods_frame_db_com_department_mid""")
print(res)

sql = "insert into ods_frame_db_com_department_mid(id,breadcrumb) values(2,'b')"
pg_client.insert(sql)

sql = "insert into ods_frame_db_com_department_mid(id,breadcrumb) values(%s,%s)"
pg_client.insertmany(sql, [[3, "c"]])

sql = "insert into ods_frame_db_com_department_mid(id,breadcrumb) values(%s,%s) \
on conflict(id,breadcrumb) do update set breadcrumb=%s"
pg_client.insertmany(sql, [[3, "c", "d"]])

sql = """insert into ads_dianchi_user(user_id,code,province,city,nick_name,employee_no,status)
                values(%s,%s,%s,%s,%s,%s,%s)
                on conflict(user_id) do update set
                code=%s,province=%s,city=%s,nick_name=%s,employee_no=%s,status=%s
                """
pg_client.insertmany(
    sql, [["1", "1", "1", "1", "1", "1", "1", "2", "2", "2", "2", "2", "2"]]
)
