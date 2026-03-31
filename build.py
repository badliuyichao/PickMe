# -*- coding: utf-8 -*-
"""
打包脚本 - 将程序打包为Windows可执行文件
运行此脚本前请先安装 pyinstaller:
    pip install pyinstaller
"""
import os
import sys
import subprocess


def build_exe():
    """打包程序"""
    print("开始打包 PickMe 抽奖系统...")

    # PyInstaller 参数
    cmd = [
        "pyinstaller",
        "--onefile",              # 打包为单个文件
        "--windowed",             # 不显示控制台窗口
        "--name=PickMe",          # 输出文件名
        "--add-data=data;data",   # 包含data目录
        "--icon=assets/icon.ico", # 图标（如果有）
        "main.py"
    ]

    # 如果图标不存在，移除图标参数
    if not os.path.exists("assets/icon.ico"):
        cmd.remove("--icon=assets/icon.ico")

    print(f"执行命令: {' '.join(cmd)}")

    # 执行打包
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("\n✅ 打包成功！")
        print(f"可执行文件位置: dist/PickMe.exe")
        print("\n使用说明:")
        print("1. 将 dist/PickMe.exe 复制到任意位置")
        print("2. 确保 data 目录与 exe 文件在同一目录")
        print("3. 双击 PickMe.exe 即可运行")
    else:
        print("\n❌ 打包失败！")
        print(f"错误信息: {result.stderr}")
        return False

    return True


if __name__ == "__main__":
    try:
        build_exe()
    except Exception as e:
        print(f"打包过程中出现错误: {e}")
        sys.exit(1)