from src.jcutils.utils.config_loader import ConfigLoader

app_config = ConfigLoader.load_config()

print("aaa")
print(app_config.APP_NAME)
print("bbb")
