from apscheduler.triggers.cron import CronTrigger


# 重写Cron定时
class my_CronTrigger(CronTrigger):
    # def __init__(self, year=None, month=None, day=None, week=None, day_of_week=None, hour=None,
    #              minute=None, second=None, start_date=None, end_date=None, timezone=None,
    #              jitter=None):
    #     super().__init__(year=None, month=None, day=None, week=None, day_of_week=None, hour=None,
    #              minute=None, second=None, start_date=None, end_date=None, timezone=None,
    #              jitter=None)
    @classmethod
    def my_from_crontab(cls, expr, timezone=None):
        values = expr.split()
        if len(values) not in (5, 7):
            raise ValueError(
                "Wrong number of fields; got {}, expected 5 or 7".format(len(values))
            )

        if len(values) == 5:
            return cls(
                minute=values[0],
                hour=values[1],
                day=values[2],
                month=values[3],
                day_of_week=values[4],
                timezone=timezone,
            )
        else:
            return cls(
                second=values[0],
                minute=values[1],
                hour=values[2],
                day=values[3],
                month=values[4],
                day_of_week=values[5],
                year=values[6],
                timezone=timezone,
            )
