"""
@Time   : 2018/9/5
@author : lijc210@163.com
@Desc:  : 函数异常，发送通知
"""

import logging
import sys
import time
import traceback
from typing import Any, Callable, List, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


def try_except(fun: Callable[..., T]) -> Callable[..., T]:
    def notice(*args: Any, **kwargs: Any) -> T:
        try:
            res: T = fun(*args, **kwargs)
        except Exception:
            res = None  # type: ignore
            fun_name: str = getattr(fun, "__name__", type(fun).__name__)
            logger.error("函数 %s 执行失败", fun_name, exc_info=True)

            error_content: str = traceback.format_exc()
            datetime: str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            subject: str = fun_name + str(datetime) + "出错"
            content: str = error_content
            # 邮件、微信通知依赖外部模块，未安装时跳过
            try:
                from utils.mail import Mail  # ty: ignore[import-not-found]
                from utils.work_weixin_send import Weixin  # ty: ignore[import-not-found]
            except ImportError:
                logger.warning("邮件/微信通知模块不可用，跳过通知")
            else:
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
                Mail(mail_to, mail_cc).send(subject, content)
                # 微信通知
                Weixin().send(agentid=1000012, text=subject)
            sys.exit(1)
        return res

    return notice


if __name__ == "__main__":

    @try_except
    def func() -> None:
        print("aaaa")
        raise ValueError("aaaa")

    func()
