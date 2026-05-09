import time

from src.jcutils.utils.config_holder import config_holder

print(config_holder.TEST)


while True:
    time.sleep(5)
    print(config_holder.TEST)
