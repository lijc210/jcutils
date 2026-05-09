# 安装说明

## pip切换源

``` shel
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config unset global.index-url

pip install -i https://pypi.org/simple/ uv
```

## 安装uv

``` shell
# 官方源
curl -LsSf https://astral.sh/uv/install.sh | sh
# 使用gitee源
curl -LsSf https://gitee.com/wangnov/uv-custom/releases/download/latest/uv-installer-custom.sh | sh
# 升级
uv self update
```

## 安装环境

``` shell
uv python pin 3.11.1
uv sync
```
