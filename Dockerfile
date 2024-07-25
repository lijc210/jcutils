FROM python:3.11-slim

RUN sed -i s/deb.debian.org/mirrors.aliyun.com/g /etc/apt/sources.list && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' >/etc/timezone && apt update && \
    apt install --no-install-recommends  gcc libpq-dev libkrb5-dev git -y && rm -rf /var/lib/apt/lists/*

WORKDIR /data/guoquan-apocalypse-cron
# 代码放在镜像外
# VOLUME ["/data/guoquan-apocalypse-cron"]
COPY . /data/guoquan-apocalypse-cron
RUN git config --global --add safe.directory /data/guoquan-apocalypse-cron && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    /usr/local/bin/python -m pip install --upgrade pip && \
    pip install --no-cache-dir  -r requirements.txt

CMD [ "python", "-u", "main.py" ]
