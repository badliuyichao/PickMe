#!/bin/bash
# PickMe 快速启动脚本

echo "========================================="
echo "  PickMe 抽奖系统 - 快速启动"
echo "========================================="
echo ""

# 检查Python
if ! command -v python &> /dev/null
then
    echo "错误: 未检测到 Python，请先安装 Python 3.8+"
    exit 1
fi

echo "Python 版本:"
python --version
echo ""

# 检查依赖
echo "检查依赖..."
pip list | grep -E "customtkinter|Pillow|openpyxl|reportlab|pygame" || {
    echo "依赖未安装，正在安装..."
    pip install -r requirements.txt
}

echo ""
echo "启动程序..."
echo ""

# 运行程序
python main.py

echo ""
echo "程序已退出"
echo "========================================="