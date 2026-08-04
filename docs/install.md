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
uv python pin 3.13
uv sync
```

## 安装依赖

```
uv sync --all-extras
```

## Free-threaded Python (No-GIL) 支持

jcutils 支持 Python Free-threaded（无 GIL）环境（Python 3.13t+）。

### 安装 free-threaded Python

``` shell
# 使用 uv 安装 free-threaded Python
uv python install 3.13t
uv python pin 3.13t

# 或使用 pyenv
pyenv install 3.13t
```

### 在 free-threaded 环境中安装 jcutils

``` shell
# pip 安装
pip install jcutils

# uv 安装
uv sync
```

### 验证 free-threaded 支持

``` python
import sys
print("GIL enabled:", sys._is_gil_enabled())  # 应输出 False

import jcutils
print(jcutils.hello_from_bin())
```

> **注意**: Free-threaded 构建使用版本特定的 wheel（如 cp313t），
> 而非 abi3 wheel。CI 会自动为 Linux/macOS/Windows 构建并发布 free-threaded wheel。
