"""
@author: lijc210@163.com
@file: html.py
@time: 2020/07/14
@desc: HTML标签处理工具
"""

import re
from typing import Optional


def remove_html_label(htmlstr: str) -> str:
    """
    去除HTML标签，纯文本提取

    :param htmlstr: 包含HTML标签的字符串
    :return: 去除HTML标签后的纯文本字符串
    """
    # hive里面会把\n和\r替换为<CR>和<LF>，先恢复
    htmlstr = htmlstr.replace("<CR>", "").replace("<LF>", "")

    # 先过滤CDATA
    re_cdata = re.compile(r"//<!\[CDATA\[[^>]*//\]\]>", re.I)  # 匹配CDATA
    re_script = re.compile(r"<\s*script[^>]*>[^<]*<\s*/\s*script\s*>", re.I)  # Script
    re_style = re.compile(r"<\s*style[^>]*>[^<]*<\s*/\s*style\s*>", re.I)  # style
    re_br = re.compile(r"<br\s*?/?>")  # 处理换行
    re_h = re.compile(r"</?\w+[^>]*>")  # HTML标签
    re_comment = re.compile(r"<!--[^>]*-->")  # HTML注释

    s: str = re_cdata.sub("", htmlstr)  # 去掉CDATA
    s = re_script.sub("", s)  # 去掉SCRIPT
    s = re_style.sub("", s)  # 去掉style
    s = re_br.sub("\n", s)  # 将br转换为换行
    s = re_h.sub("", s)  # 去掉HTML标签
    s = re_comment.sub("", s)  # 去掉HTML注释

    # 去掉多余的空行
    blank_line = re.compile(r"\n+")
    s = blank_line.sub("\n", s)

    # 遇到2个数字中间一个逗号的不分割（逗号在数字中间表示千位分隔符）
    while True:
        mm: Optional[re.Match[str]] = re.search(r"\d+,+\d+", s)
        if mm:
            matched_text: str = mm.group()
            s = s.replace(matched_text, matched_text.replace(",", ""))
        else:
            break

    return s
