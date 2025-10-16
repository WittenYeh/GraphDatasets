#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一个从命令行读取文件名和行数 k，并打印文件前 k 行内容的脚本。
"""

import argparse
import sys

def read_first_k_lines(filename, k):
    """
    读取并打印指定文件的前 k 行。

    参数:
    filename (str): 要读取的文件的路径。
    k (int): 要读取的行数。
    """
    # 检查 k 是否为正整数
    if k <= 0:
        print(f"错误: 行数 k 必须是一个正整数，您提供的是: {k}", file=sys.stderr)
        return

    try:
        # 使用 'with open' 确保文件在使用后被正确关闭
        # 指定 encoding='utf-8' 以更好地处理各种文本文件
        with open(filename, 'r', encoding='utf-8') as f:
            # 逐行读取文件
            for i, line in enumerate(f):
                # 当我们读到第 k 行时就停止 (因为 enumerate 从 0 开始)
                if i >= k:
                    break
                # 打印行内容。line 本身包含换行符，所以用 end='' 避免额外空行
                print(line, end='')

    except FileNotFoundError:
        # 处理文件不存在的错误
        print(f"错误: 文件 '{filename}' 未找到。", file=sys.stderr)
    except Exception as e:
        # 处理其他可能的错误，例如读取权限问题
        print(f"读取文件时发生错误: {e}", file=sys.stderr)


if __name__ == "__main__":
    # 1. 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(
        description="读取并打印一个文件的前 k 行内容。",
        epilog="示例: python read_lines.py my_log.txt 10"
    )

    # 2. 添加命令行参数
    # 'filename' 是一个位置参数
    parser.add_argument("filename", help="要读取的文件的路径")
    
    # 'k' 是另一个位置参数，我们指定其类型为 int
    parser.add_argument("k", type=int, help="要从文件头部读取的行数")

    # 3. 解析参数
    # 如果命令行参数不符合要求，argparse 会自动打印帮助信息并退出
    args = parser.parse_args()

    # 4. 调用主函数并传入解析后的参数
    read_first_k_lines(args.filename, args.k)