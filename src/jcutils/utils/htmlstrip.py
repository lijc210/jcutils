"""
Created on 2017/2/17
@author: lijc210@163.com
Desc: HTML标签去除和文本分句工具
"""

import re
from typing import List

from pyquery import PyQuery as pq


class HTMLStrip:
    """
    HTML标签去除和文本处理工具类

    提供去除HTML标签和文本分句的功能
    """

    @staticmethod
    def strip(snippet: str) -> str:
        """
        去除HTML标签，提取纯文本

        :param snippet: 包含HTML标签的字符串
        :return: 去除HTML标签后的纯文本
        """
        doc: pq = pq(snippet)
        return doc.text()

    @staticmethod
    def fenju(text: str) -> List[str]:
        """
        文本分句，根据标点符号将文本分割成句子列表

        支持的标点符号包括：
        - 中文标点：；。！？
        - 英文标点：? . , ; : !
        - 其他标点：，

        :param text: 要分句的文本
        :return: 句子列表
        """
        content: str = HTMLStrip.strip(text)
        # 中文标点
        pattern2 = re.compile(r"\；|\。|\！|\？")
        # 英文和其他标点
        pattern3 = re.compile(r"\?|\.|\,|\;|\:|\!|\，")

        # 合并所有分隔符模式
        sentenselist: List[str] = re.split(f"{pattern2.pattern}|{pattern3.pattern}", content)

        # 过滤空字符串
        sentenselist = [s.strip() for s in sentenselist if s.strip()]

        return sentenselist


if __name__ == "__main__":
    # 测试HTML去除
    content: str = """首先，首先，我大中华有靠谱的不忽悠人的良心装修企业吗？<br>这不是一个人的问题，这整个行业都厚颜无耻。这也不是一个行业的问题，在目前体制下，有良心的企业很难活得久。"""
    content_new: str = HTMLStrip.strip(content)
    print("HTML去除结果:")
    print(content_new)
    print()

    # 测试分句功能
    ls: List[str] = HTMLStrip.fenju(
        "家里装修，地面材料的种类很多，木地板、瓷砖、地毯等，要怎么进行选购也是个大人值得深思的大问题。我们可以从功能、审美需求、脚感、生活习惯等四个方面来进行选购的啊。1按功能区选:起居室的沙发区最好选择柔软、易清洁更换的材料，比如一块小地毯。这样可以满足大人赤足放松看电视、儿童席地玩耍的需要。厨房的地面易附着水和污物，可选择毛孔小、吸水率低的瓷砖，清理起来比较省力。卫生间地面比较潮湿，一般不宜使用木地板，选择瓷砖也要注意防滑性。2按审美需求选:近年来，木地板产品在颜色上有了不少突破，市面上已经有彩色木地板供应，但相对而言，地毯、瓷砖组成的图案和色彩变化更丰富一些，也更容易体现个性。3按脚感选:木地板富有弹性，并有温暖感，喜欢赤足的业主应该首选木地板。随着制作工艺水平的提高，瓷砖的冰凉脚感得到了改善，布艺纹、皮革纹、木纹质感的瓷砖都已面世，脚感接近木地板，并且清洁起来更容易，加上地热采暖逐渐步入家庭，选瓷砖的人也逐渐增多。4按生活习惯选:如果你工作繁忙，无暇打理家居，应当选择易于清洁的瓷砖。如果有充分的时间，并且喜好打理家居，可以选择木地板和地毯。木地板比较难打理，因为木地板怕水，要保持一定的干燥度。瓷砖比较好打理，做起卫生来非常方便，但是脚感却不好。地毯脚感好，但却容易滋生细菌，要用吸尘器做卫生，比较麻烦。根据自己家的实际情况来选购吧！"
    )
    print("分句结果:")
    for i, sentence in enumerate(ls, 1):
        print(f"{i}. {sentence}")
    print(f"\n总共 {len(ls)} 句")
