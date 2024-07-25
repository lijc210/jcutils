import json
import os
from datetime import datetime

import openpyxl
from api.config import CONFIG


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


fileName = "1.xlsx"
file_path = os.path.join(CONFIG.TEMP_DIR, fileName)

wb = openpyxl.load_workbook(file_path)
ws = wb.active

data = []
for row in ws.iter_rows(min_row=2, max_col=4, values_only=True):
    data.append(row)


json_data = json.dumps(data, default=datetime_converter, ensure_ascii=False)
print(json_data)
