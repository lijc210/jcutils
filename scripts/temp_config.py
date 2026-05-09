import os

from dotenv import load_dotenv

load_dotenv()  # 默认读取当前工作目录下的 .env

config_path = os.getenv("CONFIG_PATH")

print(config_path)
