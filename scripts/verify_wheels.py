#!/usr/bin/env python3
"""校验 wheel 是完整、无尾随数据的 ZIP，供 CI 在发布前做快速检查。"""

from __future__ import annotations

import hashlib
import io
import sys
import zipfile
from pathlib import Path

# End of Central Directory 记录，固定 22 字节 + 可变长度的注释
EOCD = b"PK\x05\x06"


def check(data: bytes) -> str | None:
    """校验 wheel 的 ZIP 结构，返回错误信息；None 表示通过。"""
    pos = data.rfind(EOCD)
    if pos < 0:
        return "找不到 ZIP 结尾记录（EOCD）"

    comment_len = int.from_bytes(data[pos + 20 : pos + 22], "little")
    trailing = len(data) - (pos + 22 + comment_len)
    if trailing:
        return f"末尾有多余数据 {trailing} 字节"

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            broken = zf.testzip()
    except zipfile.BadZipFile as exc:
        return f"ZIP 结构损坏: {exc}"

    if broken is not None:
        return f"压缩成员校验失败: {broken}"
    return None


def main(argv: list[str]) -> int:
    if not argv:
        print("用法: verify_wheels.py <wheel 文件或目录> ...", file=sys.stderr)
        return 1

    paths: list[Path] = []
    for arg in argv:
        target = Path(arg)
        paths.extend(sorted(target.glob("*.whl")) if target.is_dir() else [target])

    if not paths:
        print("未找到任何 wheel 文件", file=sys.stderr)
        return 1

    failures = 0
    for path in paths:
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        error = check(data)
        if error is None:
            print(f"OK   {path}  size={len(data)}  sha256={digest}")
        else:
            failures += 1
            print(f"FAIL {path}: {error}")
            # 打印末尾字节，便于判断多出来的是换行符、填充字节还是别的内容
            print(f"     size={len(data)}  sha256={digest}  tail={data[-32:].hex()}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
