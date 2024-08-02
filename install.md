# 安装说明

## 安装环境

``` shell
curl -sSf https://rye-up.com/get | bash
rye self update
rye pin 3.11.1
rye sync
rye run serve #启动
rye sync --no-lock
```

## rye使用

```shell
# 安装依赖
rye sync
# 代码检查
rye lint
rye lint --fix
# 格式化代码
rye fmt
# 启动
python main.py
# rye启动
rye run main
# 执行脚本
source .env
python ...
# 后台运行
nohup rye run main >> /data/appdata/guoquan-apocalypse-cron/logs/app.log 2>&1 &
```

## docker方式部署命令参考

```shell
# 尽量在linux下 build，避免架构不一致

docker build -f Dockerfile -t guoquan-apocalypse-cron .
docker run -d -p 15603:15603 -e ENV=dev --name guoquan-apocalypse-cron guoquan-apocalypse-cron
docker run -d -p 15603:15603 -e ENV=test --name guoquan-apocalypse-cron guoquan-apocalypse-cron
docker run -d -p 15603:15603 -e ENV=prod --name guoquan-apocalypse-cron guoquan-apocalypse-cron
```


