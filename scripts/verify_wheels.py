#!/usr/bin/env python3
"""校验 wheel 是完整、无尾随数据的 ZIP，供 CI 在发布前做快速检查。"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

# End of Central Directory 记录，固定 22 字节 + 可变长度的注释
EOCD = b"PK\x05\x06"


def check(path: Path) -> str | None:
    """校验单个 wheel，返回错误信息；None 表示通过。"""
    data = path.read_bytes()

    pos = data.rfind(EOCD)
    if pos < 0:
        return "找不到 ZIP 结尾记录（EOCD）"

    comment_len = int.from_bytes(data[pos + 20 : pos + 22], "little")
    trailing = len(data) - (pos + 22 + comment_len)
    if trailing:
        return f"末尾有多余数据 {trailing} 字节"

    try:
        with zipfile.ZipFile(path) as zf:
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
        error = check(path)
        if error is None:
            print(f"OK   {path}")
        else:
            failures += 1
            print(f"FAIL {path}: {error}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
