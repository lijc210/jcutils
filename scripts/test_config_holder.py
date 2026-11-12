import time

from jcutils.utils.config_holder import config_holder

print(getattr(config_holder, "TEST", None))


while True:
    time.sleep(5)
    print(getattr(config_holder, "TEST", None))
