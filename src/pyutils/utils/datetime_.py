# Created on: 2018/3/2 11:11
# Email: lijicong@163.com
# desc
import calendar
import time
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta


def dt2ts(dt, infmt="%Y-%m-%d %H:%M:%S"):
    """
    时间转时间戳
    :param dt: 2018-03-02 11:13:37
    :return:  timestamp
    >>> dt2ts("2018-03-02 11:13:37")
    1519960417.0
    """
    return time.mktime(time.strptime(dt, infmt))


def ts2dt(ts):
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
    dt=None, days=0, infmt="%Y-%m-%d %H:%M:%S", outfmt="%Y-%m-%d %H:%M:%S"
):
    """
    指定日期加减days天
    :param dt: 默认当前时间，2018-03-02 11:13:37
    :param dasy: 1/-1
    :param infmt: '%Y-%m-%d %H:%M:%S'
    :param outfmt: '%Y-%m-%d %H:%M:%S'
    :return: datetime str
    """
    return (datetime.strptime(dt, infmt) + timedelta(days=days)).strftime(outfmt)


def day_fmt(dt=None, infmt="%Y-%m-%d %H:%M:%S", outfmt="%Y-%m-%d %H:%M:%S"):
    """
    指定日期格式化
    :param dt: 默认当前时间，2018-03-02 11:13:37
    :param dasy: 1/-1
    :param infmt: '%Y-%m-%d %H:%M:%S'
    :param outfmt: '%Y-%m-%d %H:%M:%S'
    :return: datetime str
    """
    return time.strftime(outfmt, time.strptime(dt, infmt))


def day_now(outfmt="%Y-%m-%d %H:%M:%S"):
    """
    当前时间格式化
    :param days:
    :param outfmt:
    :return:
    """
    return time.strftime(outfmt, time.localtime(time.time()))


def day_ops(days=0, outfmt="%Y-%m-%d %H:%M:%S"):
    """
    当前时间加减天
    :param days:
    :param outfmt:
    :return:
    """
    return (datetime.now() + timedelta(days=days)).strftime(outfmt)


def hour_ops(hours=0, outfmt="%Y-%m-%d %H:%M:%S"):
    """
    当前时间加减小时
    :param hours:
    :param outfmt:
    :return:
    """
    return (datetime.now() + timedelta(hours=hours)).strftime(outfmt)


def second_ops(seconds=0, outfmt="%Y-%m-%d %H:%M:%S"):
    """
    当前时间加减秒
    :param hours:
    :param outfmt:
    :return:
    """
    return (datetime.now() + timedelta(seconds=seconds)).strftime(outfmt)


def get_month_days(dt=None, infmt="%Y-%m-%d %H:%M:%S"):
    """
    获取指定年月天数
    :return:
    """
    datetime.today()
    year = time.strptime(dt, infmt).tm_year
    month = time.strptime(dt, infmt).tm_mon
    days = calendar.monthrange(year, month)[1]
    return days


def firstDay_lastDay(dt=None, infmt="%Y-%m-%d %H:%M:%S", outfmt="%Y-%m-%d %H:%M:%S"):
    """
    获取指定时间的月份第一天和最后一天日期
    :return:
    """
    year = time.strptime(dt, infmt).tm_year
    month = time.strptime(dt, infmt).tm_mon
    firstDayWeekDay, monthRange = calendar.monthrange(
        year, month
    )  # 第一天的星期和当月的总天数
    firstDay = date(year=year, month=month, day=1).strftime(outfmt)
    lastDay = date(year=year, month=month, day=monthRange).strftime(outfmt)
    return firstDay, lastDay


def get_before_month(dt=None, infmt="%Y-%m-%d %H:%M:%S", outfmt="%Y-%m-%d %H:%M:%S"):
    """
    获取指定时间的上一个年月
    :return:
    """
    year = time.strptime(dt, infmt).tm_year
    month = time.strptime(dt, infmt).tm_mon
    before_month = (date(year=year, month=month, day=1) + timedelta(days=-1)).strftime(
        outfmt
    )
    return before_month


def get_next_month(dt=None, infmt="%Y-%m-%d %H:%M:%S", outfmt="%Y-%m-%d %H:%M:%S"):
    """
    获取指定时间的下一个年月
    :return:
    """
    year = time.strptime(dt, infmt).tm_year
    month = time.strptime(dt, infmt).tm_mon
    firstDayWeekDay, monthRange = calendar.monthrange(
        year, month
    )  # 第一天的星期和当月的总天数
    next_month = (
        date(year=year, month=month, day=monthRange) + timedelta(days=1)
    ).strftime(outfmt)
    return next_month


def get_day_range(dt1=None, dt2=None, infmt="%Y-%m-%d %H:%M:%S", outfmt="%Y-%m-%d"):
    """
    获取获取两个日期之间的所有日期
    :return:
    """
    dt1 = datetime.strptime(dt1, infmt)
    dt2 = datetime.strptime(dt2, infmt)
    delta = dt2 - dt1
    date_range = []
    for i in range(delta.days + 1):
        dt = (dt1 + timedelta(i)).strftime(outfmt)
        date_range.append(dt)
    return date_range


def get_month_range(dt1=None, dt2=None, infmt="%Y-%m-%d %H:%M:%S", outfmt="%Y-%m"):
    """
    获取获取两个日期之间的所有年月
    :return:
    """
    start_day = datetime.strptime(dt1, infmt)
    end_day = datetime.strptime(dt2, infmt)

    tmp_start_day = date(start_day.year, start_day.month, 1)
    tmp_end_day = date(end_day.year, end_day.month, 1)
    # print (tmp_start_day,tmp_end_day)
    month_range = []
    while tmp_start_day <= tmp_end_day:
        year_month = tmp_start_day.strftime(outfmt)
        month_range.append(year_month)
        tmp_start_day += relativedelta(months=1)
    return month_range


def seconds2dt(seconds):
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


def get_this_monday(outfmt="%Y-%m-%d"):
    """
    获取本周周一日期
    :return: 返回周一的日期
    """
    return datetime.strftime(
        datetime.now() - timedelta(datetime.now().weekday()), outfmt
    )


def give_day_monday(dt=None, infmt="%Y-%m-%d", outfmt="%Y-%m-%d"):
    """
    获取指定日期周一日期
    :return: 返回周一的日期
    """
    dt_s = datetime.strptime(str(dt), infmt)
    return datetime.strftime(dt_s - timedelta(dt_s.weekday()), outfmt)


if __name__ == "__main__":
    # print((dt2ts("1970-01-01 08:00:00")))
    # print((day_now()))
    # print((int(dt2ts(day_now()))))
    # print ts2dt(0)
    # print give_day_ops("2018-03-02 11:13:37",1)
    # print give_day_ops("2018-03-02 11:13:37",-1)
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
    print(
        get_day_range(dt1="20190401", dt2="20190430", infmt="%Y%m%d", outfmt="%Y-%m-%d")
    )
