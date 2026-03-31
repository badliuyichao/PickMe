@echo off
REM PickMe 快速启动脚本 (Windows)

echo =========================================
echo   PickMe 抽奖系统 - 快速启动
echo =========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo Python 版本:
python --version
echo.

REM 检查依赖
echo 检查依赖...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo 依赖未安装，正在安装...
    pip install -r requirements.txt
)

echo.
echo 启动程序...
echo.

REM 运行程序
python main.py

echo.
echo 程序已退出
echo =========================================
pause