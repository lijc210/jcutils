from src.api.conn import mssql_client

sql = "select top 10 * from dbo.t_pur_requisition"
print(mssql_client.query(sql))
