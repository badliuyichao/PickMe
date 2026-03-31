# -*- coding: utf-8 -*-
"""
奖项设置面板
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.utils.data_manager import DataManager


class PrizePanel(ctk.CTkFrame):
    """奖项设置面板"""

    def __init__(self, master, data_manager: "DataManager"):
        super().__init__(master)
        self.data_manager = data_manager
        self._create_ui()
        self._load_prizes()

    def _create_ui(self):
        """创建UI"""
        # 左侧：奖项列表
        left_frame = ctk.CTkFrame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            left_frame,
            text="奖项列表",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10)

        # 列表
        self.prizes_frame = ctk.CTkScrollableFrame(left_frame)
        self.prizes_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 右侧：操作区
        right_frame = ctk.CTkFrame(self, width=300)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)
        right_frame.pack_propagate(False)

        # 添加奖项
        add_frame = ctk.CTkFrame(right_frame)
        add_frame.pack(fill="x", padx=10, pady=10)

        add_label = ctk.CTkLabel(add_frame, text="添加奖项", font=ctk.CTkFont(size=16, weight="bold"))
        add_label.pack(pady=10)

        self.name_entry = ctk.CTkEntry(add_frame, placeholder_text="奖项名称")
        self.name_entry.pack(padx=10, pady=5, fill="x")

        self.count_entry = ctk.CTkEntry(add_frame, placeholder_text="中奖人数")
        self.count_entry.pack(padx=10, pady=5, fill="x")

        # 颜色选择
        color_frame = ctk.CTkFrame(add_frame)
        color_frame.pack(padx=10, pady=5, fill="x")

        color_label = ctk.CTkLabel(color_frame, text="奖项颜色:")
        color_label.pack(side="left", padx=5)

        self.color_var = ctk.StringVar(value="#FFD700")
        colors = ["#FFD700", "#C0C0C0", "#CD7F32", "#FF6B6B", "#4ECDC4", "#95E1D3"]
        self.color_menu = ctk.CTkOptionMenu(color_frame, variable=self.color_var, values=colors)
        self.color_menu.pack(side="right", padx=5, fill="x", expand=True)

        add_btn = ctk.CTkButton(add_frame, text="添加奖项", command=self._add_prize)
        add_btn.pack(padx=10, pady=10, fill="x")

        # 说明
        info_frame = ctk.CTkFrame(right_frame)
        info_frame.pack(fill="x", padx=10, pady=10)

        info_text = "说明:\n- 奖项将按顺序抽取\n- 可设置多个奖项\n- 金色=特等奖\n- 银色=一等奖\n- 铜色=二等奖"
        info_label = ctk.CTkLabel(info_frame, text=info_text, justify="left", wraplength=250)
        info_label.pack(padx=10, pady=10)

    def _load_prizes(self):
        """加载奖项列表"""
        # 清空当前列表
        for widget in self.prizes_frame.winfo_children():
            widget.destroy()

        # 获取数据
        prizes = self.data_manager.get_prizes()

        # 显示列表
        for p in prizes:
            frame = ctk.CTkFrame(self.prizes_frame)
            frame.pack(fill="x", padx=5, pady=5)

            # 左侧颜色指示器
            color_label = ctk.CTkLabel(
                frame,
                text="  ",
                fg_color=p.get("color", "#FFD700"),
                width=10
            )
            color_label.pack(side="left", padx=5, pady=10)

            # 中间信息
            info_frame = ctk.CTkFrame(frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10)

            name_label = ctk.CTkLabel(
                info_frame,
                text=p['name'],
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            name_label.pack(anchor="w")

            progress_text = f"进度: {p.get('drawn', 0)}/{p['count']}"
            progress_label = ctk.CTkLabel(info_frame, text=progress_text, anchor="w")
            progress_label.pack(anchor="w")

            # 右侧按钮
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=5)

            # 编辑按钮
            edit_btn = ctk.CTkButton(
                btn_frame,
                text="编辑",
                width=60,
                command=lambda prize=p: self._edit_prize_dialog(prize)
            )
            edit_btn.pack(side="left", padx=2)

            # 删除按钮
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="删除",
                width=60,
                fg_color="red",
                command=lambda pid=p['id']: self._delete_prize(pid)
            )
            delete_btn.pack(side="left", padx=2)

    def _add_prize(self):
        """添加奖项"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("警告", "请输入奖项名称")
            return

        count_str = self.count_entry.get().strip()
        if not count_str:
            messagebox.showwarning("警告", "请输入中奖人数")
            return

        try:
            count = int(count_str)
            if count <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("警告", "中奖人数必须是大于0的整数")
            return

        color = self.color_var.get()
        self.data_manager.add_prize(name, count, color)

        # 清空输入
        self.name_entry.delete(0, "end")
        self.count_entry.delete(0, "end")

        # 刷新列表
        self._load_prizes()
        messagebox.showinfo("成功", f"已添加奖项: {name}")

    def _edit_prize_dialog(self, prize: dict):
        """编辑奖项对话框"""
        dialog = ctk.CTkInputDialog(
            title="编辑奖项",
            text=f"编辑 {prize['name']} - 中奖人数:",
            entry_text=str(prize['count'])
        )

        new_count_str = dialog.get_input()
        if new_count_str:
            try:
                new_count = int(new_count_str)
                if new_count <= 0:
                    raise ValueError()
                self.data_manager.update_prize(prize['id'], count=new_count)
                self._load_prizes()
                messagebox.showinfo("成功", "奖项已更新")
            except ValueError:
                messagebox.showwarning("警告", "中奖人数必须是大于0的整数")

    def _delete_prize(self, prize_id: int):
        """删除奖项"""
        if messagebox.askyesno("确认", "确定要删除该奖项吗？"):
            self.data_manager.delete_prize(prize_id)
            self._load_prizes()