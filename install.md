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
# 打包(加-c 清除打包)
rye build
# 发布
rye publish
# 添加本地包
rye add jcutils --path jcutils-0.1.0-py3-none-any.whl
```

## docker方式部署命令参考

```shell
docker build -f Dockerfile -t guoquan-apocalypse-app .
docker run -d -p 15603:15603 -e ENV=dev --name guoquan-apocalypse-app guoquan-apocalypse-app
docker run -d -p 15603:15603 -e ENV=test --name guoquan-apocalypse-app guoquan-apocalypse-app
docker run -d -p 15603:15603 -e ENV=prod --name guoquan-apocalypse-app guoquan-apocalypse-app
```


## 推送到 github

git remote set-url --add origin https://github.com/lijc210/jcutils

