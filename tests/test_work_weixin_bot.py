from src.api.config import CONFIG
from src.pyutils.utils.work_weixin_bot import send_text

key = CONFIG.WECHAT_DATA_TEST  # 测试
send_text(
    key,
    "test",
    ["@all"],
)
