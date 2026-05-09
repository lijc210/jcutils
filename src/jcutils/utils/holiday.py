"""
@author: lijc210@163.com
@file: holiday.py
@time: 2020/07/14
@desc: 节假日数据获取工具
"""

import traceback
from datetime import datetime, timedelta
from typing import Any, List, Optional

import requests


def day_ops(days: int = 0, outfmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    当前时间加减天

    :param days: 要加减的天数，正数为未来，负数为过去
    :param outfmt: 输出时间格式
    :return: 格式化后的时间字符串
    """
    return (datetime.now() + timedelta(days=days)).strftime(outfmt)


def get_day_range(
    dt1: Optional[str] = None, dt2: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y-%m-%d"
) -> List[str]:
    """
    获取获取两个日期之间的所有日期

    :param dt1: 开始日期字符串
    :param dt2: 结束日期字符串
    :param infmt: 输入日期格式
    :param outfmt: 输出日期格式
    :return: 日期列表
    """
    dt1 = datetime.strptime(dt1, infmt)
    dt2 = datetime.strptime(dt2, infmt)
    delta = dt2 - dt1
    date_range: List[str] = []
    for i in range(delta.days + 1):
        dt = (dt1 + timedelta(i)).strftime(outfmt)
        date_range.append(dt)
    return date_range


def get_holiday(year: str) -> List[List[Any]]:
    """
    获取指定年份的节假日数据

    :param year: 年份，如 "2020"
    :return: 节假日数据列表，每个元素是一个列表包含：
             [无分隔符日期, 带分隔符日期, 是否节假日, 节假日名称, 是否节后调休, 调休目标日, 星期几, 年份]
    """
    url = "http://timor.tech/api/holiday/year/{year}/".format(year=year)
    data_list: List[List[Any]] = []
    try:
        res_dict: dict = requests.get(url, timeout=10).json()
    except Exception:
        traceback.print_exc()
        print(traceback.format())
    else:
        code: int = res_dict["code"]
        date_range = get_day_range(year + "-01-01", year + "-12-31", infmt="%Y-%m-%d", outfmt="%Y-%m-%d")
        if code == 0:
            res_holiday: dict = res_dict["holiday"]
            holiday_dict: dict = {year + "-" + k: v for k, v in res_holiday.items()}
            for day2 in date_range:
                day1 = day2.replace("-", "")
                week: int = datetime.strptime(day2, "%Y-%m-%d").weekday()  # 表示星期几，0-6表示星期一到星期天
                holiday_one_dict: Optional[dict] = holiday_dict.get(day2)
                if holiday_one_dict:
                    holiday: Optional[bool] = holiday_one_dict["holiday"]  # true表示是节假日，false表示是调休
                    # 节假日的中文名。如果是调休，则是调休的中文名，例如'国庆前调休'
                    name: Optional[str] = holiday_one_dict["name"]
                    # 只在调休下有该字段。true表示放完假后调休，false表示先调休再放假
                    after: Optional[bool] = holiday_one_dict.get("after")
                    target: Optional[str] = holiday_one_dict.get("target")  # 只在调休下有该字段。表示调休的节假日
                else:
                    holiday, name, after, target = None, None, None, None
                alist: List[Any] = [day1, day2, holiday, name, after, target, week, year]
                data_list.append(alist)
        if not data_list:
            for day2 in date_range:
                day1 = day2.replace("-", "")
                week = datetime.strptime(day2, "%Y-%m-%d").weekday()  # 表示星期几，0-6表示星期一到星期天
                alist: List[Any] = [day1, day2, None, None, None, None, week, year]
    return data_list


def main() -> None:
    """
    主函数，获取并保存节假日数据
    每月1号执行，避免过多调用接口
    """
    # time.strftime("%d", time.localtime(time.time()))
    # if today != '01':
    #     return

    # year = time.strftime("%Y",time.localtime(time.time())) # 当前年
    start_year: str = "2016"
    end_year: str = day_ops(days=365 * 2, outfmt="%Y")
    data_list: List[List[Any]] = []
    for year_int in range(int(start_year), int(end_year) + 1):
        print(year_int)
        year_date: List[List[Any]] = get_holiday(str(year_int))
        data_list.extend(year_date)


if __name__ == "__main__":
    main()
