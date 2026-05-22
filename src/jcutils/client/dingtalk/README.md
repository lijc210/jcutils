# 钉钉机器人 Webhook 客户端

钉钉机器人 Webhook 客户端，用于向钉钉群发送消息。

## 功能特性

- 支持文本消息发送
- 支持 Markdown 消息发送
- 支持图片消息发送
- 支持文件消息发送（需先上传媒体）
- 支持 ActionCard 消息发送
- 支持 FeedCard 消息发送
- 支持 @提醒功能
- 自动处理接口调用限制错误
- 支持签名验证（HMAC-SHA256）

## 安装

确保已安装依赖：

```bash
pip install requests retry
```

## 使用方法

### 初始化机器人

```python
from jcutils.client.dingtalk import DingTalkBot

# 创建机器人实例
bot = DingTalkBot(
    access_token="your_access_token",
    secret="your_secret"  # 可选，签名密钥
)
```

### 发送文本消息

```python
# 发送简单文本
result = bot.send_text("你好，这是一条测试消息")

# 发送文本并@所有人
result = bot.send_text("紧急通知！", ["@all"])

# 发送文本并@指定用户
result = bot.send_text("请查看", ["13800138000", "13900139000"])
```

### 发送 Markdown 消息

```python
markdown_content = """
### 标题
这是一条 **Markdown** 消息

> 引用文本

- 列表项1
- 列表项2
"""

result = bot.send_markdown(
    content=markdown_content,
    title="消息标题",
    mentioned_list=["@all"]
)
```

### 发送图片消息

```python
# 方法1：使用 encode_image 静态方法
base64_data, md5 = DingTalkBot.encode_image("path/to/image.png")
result = bot.send_image(base64_data, md5)

# 方法2：手动编码
import base64
import hashlib

with open("path/to/image.png", "rb") as f:
    data = f.read()
    base64_data = base64.b64encode(data).decode("utf-8")
    md5 = hashlib.md5(data).hexdigest()

result = bot.send_image(base64_data, md5)
```

### 发送文件消息

```python
# 1. 先上传文件
with open("path/to/file.pdf", "rb") as f:
    file_data = f.read()

upload_result = bot.upload_media("file.pdf", file_data)
media_id = upload_result.get("media_id")

# 2. 发送文件
result = bot.send_file(media_id)
```

### 发送 ActionCard 消息

```python
result = bot.send_action_card(
    title="ACTIONCARD",
    text="### 乔布斯\n 你小时候就该认真玩iPhone了\n\n![img](http://example.com/image.png)\n\n"
    "[选择按钮](http://www.taobao.com)",
    btns=[
        {"title": "选择1", "actionURL": "https://www.dingtalk.com"},
        {"title": "选择2", "actionURL": "https://www.taobao.com"}
    ],
    btn_orientation="0"  # 0-竖排，1-横排
)
```

### 发送 FeedCard 消息

```python
result = bot.send_feed_card(
    title="FEEDCARD",
    links=[
        {
            "title": "时代峰峻--TFBOYS",
            "messageURL": "https://www.dingtalk.com",
            "picURL": "http://example.com/image.jpg"
        },
        {
            "title": "另一个链接",
            "messageURL": "https://www.taobao.com",
            "picURL": "http://example.com/image2.jpg"
        }
    ]
)
```

## 环境变量

可以通过环境变量配置机器人：

- `DINGTALK_ACCESS_TOKEN`: 机器人 access_token（必需）
- `DINGTALK_SECRET`: 机器人签名密钥（可选）

## 错误处理

机器人会自动处理以下错误：

- **接口调用超过限制 (45009)**: 抛出 `ValueError` 异常
- **其他错误**: 自动发送错误信息作为文本消息到群

## 重试机制

以下方法支持自动重试（最多重试2次，间隔60秒）：

- `send_text()`
- `send_image()`
- `upload_media()`
- `send_file()`

## 示例

完整的使用示例请参考 `examples/dingtalk_example.py`。

## API 参考

### DingTalkBot 类

#### 初始化参数

- `access_token` (str): 机器人 access_token
- `secret` (str, optional): 机器人签名密钥

#### 方法

- `send_text(content, mentioned_list=None)`: 发送文本消息
- `send_markdown(content, title="", mentioned_list=None)`: 发送 Markdown 消息
- `send_image(base64_data, md5)`: 发送图片消息
- `upload_media(file_name, data)`: 上传临时素材
- `send_file(media_id)`: 发送文件消息
- `send_action_card(title, text, btn_orientation="0", btns=None)`: 发送 ActionCard 消息
- `send_feed_card(title, links)`: 发送 FeedCard 消息
- `encode_image(file_path)`: 静态方法，将图片文件编码为 Base64 和 MD5