# -*- coding: utf-8 -*-
"""
PickMe 抽奖系统主程序入口
"""
from src.ui.main_window import MainWindow


def main():
    """主函数"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()