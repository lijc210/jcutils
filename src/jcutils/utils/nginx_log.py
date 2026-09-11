"""
@File    :   nginx_log.py
@Time    :   2021/01/23 18:41:53
@Author  :   lijc210@163.com
@Desc    :   Nginx 日志分析工具
             用于分析 Nginx 访问日志，筛选出响应时间超过阈值的请求记录
"""

import argparse
import sys
from typing import Iterator, List, Optional, TextIO


def parse_nginx_log_line(line: str) -> Optional[float]:
    """
    解析单行 Nginx 日志，提取响应时间

    :param line: Nginx 日志行
    :return: 响应时间（毫秒），解析失败返回 None
    """
    try:
        line_list: List[str] = line.strip().split(" ")
        # 假设响应时间是最后一列（常见的 Nginx 日志格式）
        response_time_str: str = line_list[-1]
        return float(response_time_str)
    except (ValueError, IndexError, AttributeError):
        return None


def filter_slow_requests(
    file: TextIO,
    threshold_ms: float = 1000.0,
    output_file: Optional[TextIO] = None,
) -> Iterator[str]:
    """
    从 Nginx 日志文件中筛选出响应时间超过阈值的请求

    :param file: 日志文件对象
    :param threshold_ms: 响应时间阈值（毫秒），默认 1000ms（1秒）
    :param output_file: 输出文件对象，如果为 None 则打印到控制台
    :yield: 慢请求日志行
    """
    for line in file:
        response_time: Optional[float] = parse_nginx_log_line(line)
        if response_time is not None and response_time >= threshold_ms:
            if output_file:
                output_file.write(line.strip() + "\n")
            else:
                yield line.strip()


def analyze_nginx_log(
    log_file_path: str,
    threshold_ms: float = 1000.0,
    output_file_path: Optional[str] = None,
) -> int:
    """
    分析 Nginx 日志文件，统计并输出慢请求数量

    :param log_file_path: Nginx 日志文件路径
    :param threshold_ms: 响应时间阈值（毫秒），默认 1000ms
    :param output_file_path: 慢请求输出文件路径，如果为 None 则打印到控制台
    :return: 慢请求的数量
    """
    slow_count: int = 0

    with open(log_file_path, "r", encoding="utf-8", errors="ignore") as log_file:
        output_file: Optional[TextIO] = None

        if output_file_path:
            output_file = open(output_file_path, "w", encoding="utf-8")
        else:
            print(f"正在分析日志文件: {log_file_path}")
            print(f"响应时间阈值: {threshold_ms}ms")
            print("-" * 80)

        try:
            for line in filter_slow_requests(log_file, threshold_ms, output_file):
                slow_count += 1
                if output_file is None:
                    print(f"[{slow_count}] {line}")
        finally:
            if output_file:
                output_file.close()
                print(f"慢请求已保存到: {output_file_path}")

    return slow_count


def analyze_nginx_log_from_stdin(threshold_ms: float = 1000.0) -> int:
    """
    从标准输入读取 Nginx 日志并分析慢请求

    :param threshold_ms: 响应时间阈值（毫秒），默认 1000ms
    :return: 慢请求的数量
    """
    slow_count: int = 0

    print("正在从标准输入读取日志...")
    print(f"响应时间阈值: {threshold_ms}ms")
    print("-" * 80)

    for line in filter_slow_requests(sys.stdin, threshold_ms):
        slow_count += 1
        print(f"[{slow_count}] {line}")

    return slow_count


def main() -> None:
    """
    主函数，提供命令行接口
    """
    parser = argparse.ArgumentParser(description="Nginx 日志慢请求分析工具")
    parser.add_argument("log_file", nargs="?", help="Nginx 日志文件路径，如果不指定则从标准输入读取")
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=1000.0,
        help="响应时间阈值（毫秒），默认 1000ms",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="输出文件路径，如果不指定则打印到控制台",
    )

    args = parser.parse_args()

    try:
        if args.log_file:
            slow_count: int = analyze_nginx_log(args.log_file, args.threshold, args.output)
        else:
            slow_count = analyze_nginx_log_from_stdin(args.threshold)

        print("-" * 80)
        print(f"分析完成！共找到 {slow_count} 个慢请求（响应时间 >= {args.threshold}ms）")

    except FileNotFoundError:
        print(f"错误: 文件 '{args.log_file}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 示例 1: 分析日志文件
    # python nginx_log.py access.log -t 2000 -o slow_requests.log

    # 示例 2: 从标准输入读取
    # cat access.log | python nginx_log.py -t 1000

    # 示例 3: 默认参数运行
    # python nginx_log.py 13.log

    # 直接运行主程序
    main()

    # 或者使用原始方式（向后兼容）
    # with open("13.log") as f:
    #     for line in f.readlines():
    #         line_list = line.strip().split(" ")
    #         try:
    #             ms = float(line_list[-1])
    #             if ms >= 1:
    #                 print(line.strip())
    #         except Exception:
    #             pass
    #             # print line.strip()
