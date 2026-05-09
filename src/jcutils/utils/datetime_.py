# Created on: 2018/3/2 11:11
# Email: lijicong@163.com
# desc
import calendar
import time
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple, Union

from dateutil.relativedelta import relativedelta


def dt2ts(dt: str, infmt: str = "%Y-%m-%d %H:%M:%S") -> float:
    """
    时间转时间戳
    :param dt: 2018-03-02 11:13:37
    :return:  timestamp
    >>> dt2ts("2018-03-02 11:13:37")
    1519960417.0
    """
    return time.mktime(time.strptime(dt, infmt))


def ts2dt(ts: Union[int, float]) -> str:
    """
    时间戳转时间
    :param ts: 1519960417
    :return: datetime str
    """
    if len(str(int(ts))) == 13:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts / 1000))
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def give_day_ops(
    dt: str = "",
    days: int = 0,
    years: int = 0,
    months: int = 0,
    weeks: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    infmt: str = "%Y-%m-%d %H:%M:%S",
    outfmt: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """
    指定日期加减年,月,星期,天,小时,分钟,秒
    :param dt: 默认当前时间，2018-03-02 11:13:37
    :param dasy: 1/-1
    :param infmt: '%Y-%m-%d %H:%M:%S'
    :param outfmt: '%Y-%m-%d %H:%M:%S'
    :return: datetime str
    """
    if years or months:  # 年，月的的天数不固定，使用dateutil库
        return (
            datetime.strptime(dt, infmt)
            + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds)
        ).strftime(outfmt)
    else:
        return (
            datetime.strptime(dt, infmt)
            + timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
        ).strftime(outfmt)


def day_fmt(dt: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    指定日期格式化
    :param dt: 默认当前时间，2018-03-02 11:13:37
    :param dasy: 1/-1
    :param infmt: '%Y-%m-%d %H:%M:%S'
    :param outfmt: '%Y-%m-%d %H:%M:%S'
    :return: datetime str
    """
    return time.strftime(outfmt, time.strptime(dt, infmt))


def day_now(outfmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    当前时间格式化
    :param days:
    :param outfmt:
    :return:
    """
    return time.strftime(outfmt, time.localtime(time.time()))


def day_ops(days: int = 0, outfmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    当前时间加减天
    :param days:
    :param outfmt:
    :return:
    """
    return (datetime.now() + timedelta(days=days)).strftime(outfmt)


def hour_ops(hours: int = 0, outfmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    当前时间加减小时
    :param hours:
    :param outfmt:
    :return:
    """
    return (datetime.now() + timedelta(hours=hours)).strftime(outfmt)


def second_ops(seconds: int = 0, outfmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    当前时间加减秒
    :param hours:
    :param outfmt:
    :return:
    """
    return (datetime.now() + timedelta(seconds=seconds)).strftime(outfmt)


def year_ops(years: int = 0, outfmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    当前时间加减年
    :param days:
    :param outfmt:
    :return:
    """
    return (datetime.now() + relativedelta(years=years)).strftime(outfmt)


def get_month_days(dt: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S") -> int:
    """
    获取指定年月天数
    :return:
    """
    datetime.today()
    year = time.strptime(dt, infmt).tm_year
    month = time.strptime(dt, infmt).tm_mon
    days = calendar.monthrange(year, month)[1]
    return days


def firstDay_lastDay(
    dt: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y-%m-%d %H:%M:%S"
) -> Tuple[str, str]:
    """
    获取指定时间的月份第一天和最后一天日期
    :return:
    """
    year = time.strptime(dt, infmt).tm_year
    month = time.strptime(dt, infmt).tm_mon
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)  # 第一天的星期和当月的总天数
    firstDay = date(year=year, month=month, day=1).strftime(outfmt)
    lastDay = date(year=year, month=month, day=monthRange).strftime(outfmt)
    return firstDay, lastDay


def get_before_month(
    dt: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    获取指定时间的上一个年月
    :return:
    """
    year = time.strptime(dt, infmt).tm_year
    month = time.strptime(dt, infmt).tm_mon
    before_month = (date(year=year, month=month, day=1) + timedelta(days=-1)).strftime(outfmt)
    return before_month


def get_next_month(
    dt: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    获取指定时间的下一个年月
    :return:
    """
    year = time.strptime(dt, infmt).tm_year
    month = time.strptime(dt, infmt).tm_mon
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)  # 第一天的星期和当月的总天数
    next_month = (date(year=year, month=month, day=monthRange) + timedelta(days=1)).strftime(outfmt)
    return next_month


def get_day_range(
    dt1: Optional[str] = None, dt2: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y-%m-%d"
) -> List[str]:
    """
    获取获取两个日期之间的所有日期
    :return:
    """
    dt1 = datetime.strptime(dt1, infmt)
    dt2 = datetime.strptime(dt2, infmt)
    delta = dt2 - dt1
    date_range: List[str] = []
    for i in range(delta.days + 1):
        dt = (dt1 + timedelta(i)).strftime(outfmt)
        date_range.append(dt)
    return date_range


def get_month_range(
    dt1: Optional[str] = None, dt2: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y-%m"
) -> List[str]:
    """
    获取获取两个日期之间的所有年月
    :return:
    """
    start_day = datetime.strptime(dt1, infmt)
    end_day = datetime.strptime(dt2, infmt)

    tmp_start_day = date(start_day.year, start_day.month, 1)
    tmp_end_day = date(end_day.year, end_day.month, 1)
    # print (tmp_start_day,tmp_end_day)
    month_range: List[str] = []
    while tmp_start_day <= tmp_end_day:
        year_month = tmp_start_day.strftime(outfmt)
        month_range.append(year_month)
        tmp_start_day += relativedelta(months=1)
    return month_range


def get_year_range(
    dt1: Optional[str] = None, dt2: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y"
) -> List[int]:
    """
    获取获取两个日期之间的所有年月
    :return:
    """
    start_day = datetime.strptime(dt1, infmt)
    end_day = datetime.strptime(dt2, infmt)

    tmp_start_year = start_day.year
    tmp_end_year = end_day.year
    # print(tmp_start_year, tmp_end_year)
    year_range: List[int] = []
    while tmp_start_year <= tmp_end_year:
        year_range.append(tmp_start_year)
        tmp_start_year += 1
    return year_range


def seconds2dt(seconds: Union[int, float]) -> str:
    """
    秒数转时间
    :return:
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if seconds > 3600:
        return "%d:%02d:%02d" % (h, m, s)
    else:
        return "%02d:%02d" % (m, s)


def get_this_monday(outfmt: str = "%Y-%m-%d") -> str:
    """
    获取本周周一日期
    :return: 返回周一的日期
    """
    return datetime.strftime(datetime.now() - timedelta(datetime.now().weekday()), outfmt)


def give_day_monday(dt: Optional[str] = None, infmt: str = "%Y-%m-%d", outfmt: str = "%Y-%m-%d") -> str:
    """
    获取指定日期周一日期
    :return: 返回周一的日期
    """
    dt_s = datetime.strptime(str(dt), infmt)
    return datetime.strftime(dt_s - timedelta(dt_s.weekday()), outfmt)


def get_comp_seconds(
    dt1: Optional[str] = None, dt2: Optional[str] = None, infmt: str = "%Y-%m-%d %H:%M:%S", outfmt: str = "%Y-%m"
) -> float:
    """
    获取两个日期之间的时间差，单位秒
    :return: 返回周一的日期
    """
    d1 = datetime.strptime(dt1, infmt)
    d2 = datetime.strptime(dt2, infmt)
    seconds = (d2 - d1).total_seconds()
    return seconds


if __name__ == "__main__":
    # print((dt2ts("1970-01-01 08:00:00")))
    # print((day_now()))
    # print((int(dt2ts(day_now()))))
    # print ts2dt(0)
    print(give_day_ops("2018-03-02 11:13:37", 1))
    # print give_day_ops("2018-03-02 11:13:37",-1)
    print(give_day_ops("2018-03-02 11:13:37", years=1, months=2))
    # print day_fmt("2018-03-02 11:13:37")
    # print day_ops(-1)
    # print day_ops(-1)
    # print ts2dt(0/1000)
    # print timeit(stmt="time.mktime(time.strptime('2018-03-02 11:13:37', '%Y-%m-%d %H:%M:%S'))",number=1000)
    # print timeit(stmt="dt2ts('2018-03-02 11:13:37')", setup="from __main__ import dt2ts", number=1000)
    # import doctest
    # doctest.testmod()
    # print((second_ops(seconds=-3600)))
    # print ts2dt(0)
    # print(get_day_range(dt1="20190401", dt2="20190430", infmt="%Y%m%d", outfmt="%Y-%m-%d"))
    # print(get_comp_seconds(dt1="20240801", dt2="20240802", infmt="%Y%m%d", outfmt="%Y-%m-%d"))
    # print(get_year_range(dt1="2017-08-17", dt2="2024-10-16", infmt="%Y-%m-%d", outfmt="%Y-%m-%d"))
