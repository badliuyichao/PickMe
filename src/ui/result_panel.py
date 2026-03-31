# -*- coding: utf-8 -*-
"""
结果管理面板
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.utils.data_manager import DataManager


class ResultPanel(ctk.CTkFrame):
    """结果管理面板"""

    def __init__(self, master, data_manager: "DataManager"):
        super().__init__(master)
        self.data_manager = data_manager
        self._create_ui()
        self._load_results()

    def _create_ui(self):
        """创建UI"""
        # 顶部操作栏
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            top_frame,
            text="中奖名单",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=10)

        # 按钮
        export_btn = ctk.CTkButton(top_frame, text="导出名单", command=self._export_results)
        export_btn.pack(side="right", padx=10)

        clear_btn = ctk.CTkButton(
            top_frame,
            text="清空结果",
            fg_color="red",
            command=self._clear_results
        )
        clear_btn.pack(side="right", padx=10)

        refresh_btn = ctk.CTkButton(top_frame, text="刷新", command=self._load_results)
        refresh_btn.pack(side="right", padx=10)

        # 中奖统计
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=20, pady=10)

        total_label = ctk.CTkLabel(stats_frame, text="总中奖人数: 0")
        total_label.pack(pady=10)
        self.total_label = total_label

        # 中奖名单列表
        self.results_frame = ctk.CTkScrollableFrame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def _load_results(self):
        """加载中奖结果"""
        # 清空当前列表
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # 获取数据
        results = self.data_manager.get_results()
        self.total_label.configure(text=f"总中奖人数: {len(results)}")

        # 按奖项分组显示
        prizes = self.data_manager.get_prizes()

        for prize in prizes:
            # 奖项标题
            prize_results = [r for r in results if r['prize_id'] == prize['id']]

            if prize_results:
                # 奖项框
                prize_frame = ctk.CTkFrame(self.results_frame)
                prize_frame.pack(fill="x", padx=5, pady=10)

                # 奖项标题栏
                title_frame = ctk.CTkFrame(prize_frame)
                title_frame.pack(fill="x", padx=10, pady=5)

                # 颜色指示器
                color_label = ctk.CTkLabel(
                    title_frame,
                    text="  ",
                    fg_color=prize.get("color", "#FFD700"),
                    width=10
                )
                color_label.pack(side="left", padx=5)

                prize_name_label = ctk.CTkLabel(
                    title_frame,
                    text=f"{prize['name']} ({len(prize_results)}/{prize['count']}名)",
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                prize_name_label.pack(side="left", padx=10)

                # 中奖者列表
                for i, result in enumerate(prize_results):
                    winner_frame = ctk.CTkFrame(prize_frame, fg_color="transparent")
                    winner_frame.pack(fill="x", padx=20, pady=2)

                    # 序号
                    index_label = ctk.CTkLabel(
                        winner_frame,
                        text=f"{i+1}.",
                        width=30
                    )
                    index_label.pack(side="left")

                    # 姓名
                    name_label = ctk.CTkLabel(
                        winner_frame,
                        text=result['winner_name'],
                        font=ctk.CTkFont(size=14),
                        anchor="w"
                    )
                    name_label.pack(side="left", padx=10, fill="x", expand=True)

                    # 时间
                    time_label = ctk.CTkLabel(
                        winner_frame,
                        text=result['timestamp'],
                        text_color="gray"
                    )
                    time_label.pack(side="right", padx=10)

        if not results:
            no_data_label = ctk.CTkLabel(
                self.results_frame,
                text="暂无中奖记录",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.pack(pady=20)

    def _export_results(self):
        """导出中奖结果"""
        results = self.data_manager.get_results()
        if not results:
            messagebox.showwarning("提示", "暂无中奖结果可导出")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if not file_path:
            return

        if self.data_manager.export_results_to_txt(file_path):
            messagebox.showinfo("成功", f"中奖名单已导出到: {file_path}")
        else:
            messagebox.showerror("错误", "导出失败")

    def _clear_results(self):
        """清空所有结果"""
        if messagebox.askyesno("确认", "确定要清空所有中奖结果吗？此操作不可恢复！"):
            self.data_manager.clear_results()
            self._load_results()
            messagebox.showinfo("成功", "中奖结果已清空")