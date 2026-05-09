"""
@File    :   apscheduler_.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :   AP Scheduler 自定义 Cron 定时触发器
             扩展了标准的 CronTrigger，支持标准 crontab 格式
"""

from typing import Optional

from apscheduler.triggers.cron import CronTrigger


class my_CronTrigger(CronTrigger):
    """
    自定义 Cron 定时触发器类

    继承自 APScheduler 的 CronTrigger，提供了从标准 crontab 表达式创建触发器的便捷方法。

    标准的 5 字段 crontab 格式：
    - minute hour day month day_of_week
    - 例如: "0 0 * * *" 表示每天午夜执行

    标准的 7 字段 crontab 格式（包含秒和年）：
    - second minute hour day month day_of_week year
    - 例如: "0 0 0 * * * 2024" 表示 2024 年每天午夜执行
    """

    @classmethod
    def my_from_crontab(cls, expr: str, timezone: Optional[str] = None) -> "my_CronTrigger":
        """
        从标准 crontab 表达式创建 CronTrigger 实例

        支持两种格式：
        1. 5 字段格式：minute hour day month day_of_week
        2. 7 字段格式：second minute hour day month day_of_week year

        :param expr: crontab 表达式字符串，各字段用空格分隔
                     例如: "0 0 * * *" 或 "0 0 0 * * * 2024"
        :param timezone: 时区字符串，例如 "Asia/Shanghai" 或 None
        :return: my_CronTrigger 实例
        :raises ValueError: 当字段数量不符合 5 或 7 时抛出
        :example:
            >>> trigger = my_CronTrigger.my_from_crontab("0 0 * * *")
            >>> trigger = my_CronTrigger.my_from_crontab("0 0 0 * * * 2024", timezone="Asia/Shanghai")
        """
        values: list[str] = expr.split()

        if len(values) not in (5, 7):
            raise ValueError(f"Wrong number of fields; got {len(values)}, expected 5 or 7")

        if len(values) == 5:
            # 5 字段格式: minute hour day month day_of_week
            return cls(
                minute=values[0],
                hour=values[1],
                day=values[2],
                month=values[3],
                day_of_week=values[4],
                timezone=timezone,
            )
        else:
            # 7 字段格式: second minute hour day month day_of_week year
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


if __name__ == "__main__":
    # 测试 5 字段 crontab 格式（每分钟执行）
    trigger_5_fields = my_CronTrigger.my_from_crontab("* * * * *")
    print(f"5 字段触发器: {trigger_5_fields}")
    print(f"下次执行时间: {trigger_5_fields.get_next_fire_time(None, None)}")

    # 测试 7 字段 crontab 格式（带时区）
    trigger_7_fields = my_CronTrigger.my_from_crontab("0 0 0 * * * 2024", timezone="Asia/Shanghai")
    print(f"\n7 字段触发器: {trigger_7_fields}")

    # 测试错误的字段数量
    try:
        trigger_error = my_CronTrigger.my_from_crontab("* * *")
    except ValueError as e:
        print(f"\n预期错误: {e}")

    # 常见的 crontab 表达式示例
    examples = {
        "每分钟执行": "* * * * *",
        "每天午夜执行": "0 0 * * *",
        "每小时执行": "0 * * * *",
        "每周一上午 9 点执行": "0 9 * * 1",
        "每月 1 号执行": "0 0 1 * *",
        "每秒执行": "* * * * * *",
    }

    print("\n常见的 crontab 表达式示例:")
    for desc, expr in examples.items():
        try:
            trigger = my_CronTrigger.my_from_crontab(expr)
            print(f"{desc}: {expr} -> {trigger}")
        except Exception as e:
            print(f"{desc}: {expr} -> 错误: {e}")
