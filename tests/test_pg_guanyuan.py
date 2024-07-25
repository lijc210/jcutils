from src.api.conn_pool import guanyuan_client

sql = "SELECT * FROM pg_tables WHERE schemaname = 'public'"
req = guanyuan_client.query(sql)
for row in req:
    tablename = row["tablename"]
    sql2 = f"""select count(1) as total from "{tablename}" """
    req2 = guanyuan_client.query(sql2)
    total = req2[0]["total"]
    print(tablename, total)
