import re


def phone_mask(text):
    # 使用正则表达式查找手机号
    def replace_phone(match):
        phone_number = match.group(1)
        masked_phone_number = phone_number[:3] + "*" * 4 + phone_number[7:]
        return f"{masked_phone_number}"

    # 对手机号进行部分替换
    masked_text = re.sub(r"\D(1[3456789]\d{9})", replace_phone, text)

    return masked_text


text = """回复时间要求： 门店编码及名称：锅圈食汇江苏省苏州市姑苏区城北西路店327548 问题描述：商家进线，顾客美团#3号单，在脆骨鱼棒 115g里面发现有头发，门店要求给出处理方案，目前顾客未表态。 涉及订单事宜提供订单号：415279371365023744478538（三方单号：2500899354267010427） 图片：在附件 商家手机号：18913747311"""

result = phone_mask(text)
print(result)
