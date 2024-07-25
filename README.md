# pyutils

python 公用工具包

## rye 部署方式

``` shell
curl -sSf https://rye-up.com/get | bash
rye self update
rye pin 3.11.1
rye sync
rye run serve #启动
rye sync --no-lock
```

## rye 使用

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
# 添加本地包
rye add pyutils --path /Users/lijicong/workspace/python/pyutils/dist/pyutils-0.1.0-py3-none-any.whl
```

## 推送到锅圈仓库

git remote set-url --add origin https://e.coding.net/lijc210/work_guoquan/guoquan-apocalypse-cron.git
