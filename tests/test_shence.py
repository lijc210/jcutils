import requests

from src.api.config import CONFIG
from src.jcutils.utils.datetime_ import day_now, day_ops

token = CONFIG.SHENCE_API_SECRET

start_time = day_ops(days=-1, outfmt="%Y-%m-%d 00:00:00")
end_time = day_now(outfmt="%Y-%m-%d 00:00:00")

# 上传的
data = {
    "q": f"select count(1) as total from events where event ='PayOrder'\
    and time between '{start_time}' and '{end_time}' /*MAX_QUERY_EXECUTION_TIME=1800*/"
}
print(data)
r = requests.post(CONFIG.SHENCE_URL + f"/api/sql/query?token={token}&project=production", data=data)
total2 = int(r.text.replace("total", "").replace("\n", ""))
print(total2)
