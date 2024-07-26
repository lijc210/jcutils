from src.api.config import CONFIG
from src.jcutils.utils.mysql_client import MySqlClient

apocalypse_client = MySqlClient(conn_dict=CONFIG.APOCALYPSE_DB, cursorclass="dict")


def query():
    res = apocalypse_client.query("select * from upd_auto_screen_component limit 10")
    print(res)


query()
