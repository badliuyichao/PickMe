# -*- coding: utf-8 -*-
"""
主窗口模块
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.utils.data_manager import DataManager
from src.core.lottery_engine import LotteryEngine
from src.ui.participant_panel import ParticipantPanel
from src.ui.prize_panel import PrizePanel
from src.ui.lottery_display import LotteryDisplay
from src.ui.result_panel import ResultPanel
import config


class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        # 设置外观
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # 窗口设置
        self.title(config.WINDOW_TITLE)
        self.geometry(f"{config.WINDOW_SIZE[0]}x{config.WINDOW_SIZE[1]}")
        self.minsize(*config.WINDOW_MIN_SIZE)

        # 初始化数据管理器
        self.data_manager = DataManager(
            config.DATA_FILES["participants"],
            config.DATA_FILES["prizes"],
            config.DATA_FILES["results"]
        )

        # 初始化抽奖引擎
        self.lottery_engine = LotteryEngine(self.data_manager)

        # 创建UI
        self._create_ui()

    def _create_ui(self):
        """创建UI界面"""
        # 创建选项卡
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加选项卡
        self.tab_participants = self.tabview.add("参与者管理")
        self.tab_prizes = self.tabview.add("奖项设置")
        self.tab_lottery = self.tabview.add("抽奖")
        self.tab_results = self.tabview.add("中奖名单")

        # 创建各个面板
        self.participant_panel = ParticipantPanel(
            self.tab_participants,
            self.data_manager
        )
        self.participant_panel.pack(fill="both", expand=True)

        self.prize_panel = PrizePanel(
            self.tab_prizes,
            self.data_manager
        )
        self.prize_panel.pack(fill="both", expand=True)

        self.lottery_display = LotteryDisplay(
            self.tab_lottery,
            self.data_manager,
            self.lottery_engine
        )
        self.lottery_display.pack(fill="both", expand=True)

        self.result_panel = ResultPanel(
            self.tab_results,
            self.data_manager
        )
        self.result_panel.pack(fill="both", expand=True)

    def run(self):
        """运行应用"""
        self.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()