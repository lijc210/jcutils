"""
钉钉机器人使用示例

使用前需要设置环境变量：
- DINGTALK_ACCESS_TOKEN: 机器人 access_token
- DINGTALK_SECRET: 机器人签名密钥（可选）
"""

import os

from jcutils.client.dingtalk import DingTalkBot


def main():
    # 获取环境变量
    access_token = os.getenv("DINGTALK_ACCESS_TOKEN")
    secret = os.getenv("DINGTALK_SECRET")

    if not access_token:
        print("请设置环境变量 DINGTALK_ACCESS_TOKEN")
        return

    # 创建机器人实例
    bot = DingTalkBot(access_token=access_token, secret=secret)

    # 1. 发送文本消息
    print("1. 发送文本消息")
    result = bot.send_text("你好，这是一条测试消息", ["@all"])
    print(f"结果: {result}")

    # 2. 发送 Markdown 消息
    print("\n2. 发送 Markdown 消息")
    markdown_content = """
    实时新增用户反馈<font color="warning">132例</font>，请相关同事注意。
    >类型:<font color="comment">用户反馈</font>
    >普通用户反馈:<font color="comment">117例</font>
    >VIP用户反馈:<font color="comment">15例</font>
    """
    result = bot.send_markdown(markdown_content, title="用户反馈", mentioned_list=["@all"])
    print(f"结果: {result}")

    # 3. 发送图片
    print("\n3. 发送图片")
    # 注意：需要提供实际的图片文件路径
    # file_path = "path/to/your/image.png"
    # if os.path.exists(file_path):
    #     base64_data, md5 = DingTalkBot.encode_image(file_path)
    #     result = bot.send_image(base64_data, md5)
    #     print(f"结果: {result}")

    # 4. 发送 ActionCard 消息
    print("\n4. 发送 ActionCard 消息")
    result = bot.send_action_card(
        title="ACTIONCARD",
        text="### 乔布斯\n 你小时候就该认真玩iPhone了\n\n![img](http://www.wailian.link/images/2016/02/05/icon.png)\n\n"
        "[选择按钮](http://www.taobao.com)",
        btns=[{"title": "选择1", "actionURL": "https://www.dingtalk.com"}],
    )
    print(f"结果: {result}")

    # 5. 发送 FeedCard 消息
    print("\n5. 发送 FeedCard 消息")
    result = bot.send_feed_card(
        title="FEEDCARD",
        links=[
            {
                "title": "时代峰峻--TFBOYS",
                "messageURL": "https://www.dingtalk.com",
                "picURL": "http://www.wailian.link/images/2016/02/05/tfboys.jpg",
            }
        ],
    )
    print(f"结果: {result}")

    # 6. 文件上传和发送
    print("\n6. 文件上传和发送")
    # 注意：需要提供实际的文件路径
    # file_path = "path/to/your/file.pdf"
    # if os.path.exists(file_path):
    #     with open(file_path, "rb") as f:
    #         file_data = f.read()
    #     file_name = os.path.basename(file_path)
    #     upload_result = bot.upload_media(file_name, file_data)
    #     if upload_result.get("errcode") == 0:
    #         media_id = upload_result.get("media_id")
    #         result = bot.send_file(media_id)
    #         print(f"文件发送结果: {result}")


if __name__ == "__main__":
    main()
