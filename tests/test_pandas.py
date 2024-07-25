import json
import os
from datetime import datetime

import pandas as pd
from api.config import CONFIG


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


fileName = "1.xlsx"
file_path = os.path.join(CONFIG.TEMP_DIR, fileName)
df = pd.read_excel(file_path, sheet_name=0, keep_default_na=False)
# 将数据转换为列表，并将 NaN 转换为 None
data_list = df.values.tolist()
data_dict = {"fileName": fileName, "data": data_list, "msg": "success"}
print(data_dict)
j = json.dumps(data_dict, ensure_ascii=False, default=datetime_converter)
print(j)
