"""
@Time   : 2018/9/5
@author : lijc210@163.com
@Desc:  : 函数异常，发送通知
"""

import sys
import time
import traceback
from typing import Any, Callable, List, TypeVar

from utils.mail import Mail
from utils.work_weixin_send import Weixin

T = TypeVar("T")


def try_except(fun: Callable[..., T]) -> Callable[..., T]:
    def notice(*args: Any, **kwargs: Any) -> T:
        try:
            res: T = fun(*args, **kwargs)
        except Exception:
            res = None  # type: ignore
            traceback.print_exc()

            fun_name: str = fun.__name__
            error_content: str = traceback.format_exc()
            datetime: str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            subject: str = fun_name + str(datetime) + "出错"
            content: str = error_content
            # 邮件通知
            mail_to: List[str] = [
                "lijicong1@qeeka.com",
                "henry.xiao@qeeka.com",
                "lingkangfu@qeeka.com",
            ]
            mail_cc: List[str] = [
                "lijicong1@qeeka.com",
                "henry.xiao@qeeka.com",
                "lingkangfu@qeeka.com",
            ]
            mail: Mail = Mail(mail_to, mail_cc)
            mail.send(subject, content)
            # 微信通知
            weixin: Weixin = Weixin()
            weixin.send(agentid=1000012, text=subject)
            sys.exit(1)
        return res

    return notice


if __name__ == "__main__":

    @try_except
    def func() -> None:
        print("aaaa")
        raise ValueError("aaaa")

    func()
