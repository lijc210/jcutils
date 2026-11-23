from src.jcutils.utils.config_loader import ConfigLoader

app_config = ConfigLoader.load_config()

if __name__ == "__main__":
    print("aaa")
    print(app_config.APP_ID)
    print("bbb")
