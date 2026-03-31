# -*- coding: utf-8 -*-
"""
参与者管理面板
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.utils.data_manager import DataManager


class ParticipantPanel(ctk.CTkFrame):
    """参与者管理面板"""

    def __init__(self, master, data_manager: "DataManager"):
        super().__init__(master)
        self.data_manager = data_manager
        self._create_ui()
        self._load_participants()

    def _create_ui(self):
        """创建UI"""
        # 左侧：参与者列表
        left_frame = ctk.CTkFrame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            left_frame,
            text="参与者列表",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10)

        # 统计信息
        self.stats_label = ctk.CTkLabel(left_frame, text="总人数: 0")
        self.stats_label.pack(pady=5)

        # 列表框
        self.participants_listbox = ctk.CTkScrollableFrame(left_frame)
        self.participants_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # 右侧：操作区
        right_frame = ctk.CTkFrame(self, width=300)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)
        right_frame.pack_propagate(False)

        # 添加参与者
        add_frame = ctk.CTkFrame(right_frame)
        add_frame.pack(fill="x", padx=10, pady=10)

        add_label = ctk.CTkLabel(add_frame, text="添加参与者", font=ctk.CTkFont(size=16, weight="bold"))
        add_label.pack(pady=10)

        self.name_entry = ctk.CTkEntry(add_frame, placeholder_text="姓名")
        self.name_entry.pack(padx=10, pady=5, fill="x")

        self.dept_entry = ctk.CTkEntry(add_frame, placeholder_text="部门（可选）")
        self.dept_entry.pack(padx=10, pady=5, fill="x")

        add_btn = ctk.CTkButton(add_frame, text="添加", command=self._add_participant)
        add_btn.pack(padx=10, pady=10, fill="x")

        # 批量操作
        batch_frame = ctk.CTkFrame(right_frame)
        batch_frame.pack(fill="x", padx=10, pady=10)

        batch_label = ctk.CTkLabel(batch_frame, text="批量操作", font=ctk.CTkFont(size=16, weight="bold"))
        batch_label.pack(pady=10)

        import_btn = ctk.CTkButton(batch_frame, text="从文件导入", command=self._import_from_file)
        import_btn.pack(padx=10, pady=5, fill="x")

        clear_btn = ctk.CTkButton(batch_frame, text="清空所有", fg_color="red", command=self._clear_all)
        clear_btn.pack(padx=10, pady=5, fill="x")

        export_btn = ctk.CTkButton(batch_frame, text="导出名单", command=self._export_participants)
        export_btn.pack(padx=10, pady=5, fill="x")

    def _load_participants(self):
        """加载参与者列表"""
        # 清空当前列表
        for widget in self.participants_listbox.winfo_children():
            widget.destroy()

        # 获取数据
        participants = self.data_manager.get_participants()
        self.stats_label.configure(text=f"总人数: {len(participants)}")

        # 显示列表
        for i, p in enumerate(participants):
            frame = ctk.CTkFrame(self.participants_listbox)
            frame.pack(fill="x", padx=5, pady=2)

            text = f"{i+1}. {p['name']}"
            if p.get('department'):
                text += f" ({p['department']})"

            label = ctk.CTkLabel(frame, text=text, anchor="w")
            label.pack(side="left", padx=10, pady=5, fill="x", expand=True)

            delete_btn = ctk.CTkButton(
                frame,
                text="删除",
                width=60,
                fg_color="red",
                command=lambda pid=p['id']: self._delete_participant(pid)
            )
            delete_btn.pack(side="right", padx=5, pady=5)

    def _add_participant(self):
        """添加参与者"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("警告", "请输入姓名")
            return

        department = self.dept_entry.get().strip()
        self.data_manager.add_participant(name, department)

        # 清空输入
        self.name_entry.delete(0, "end")
        self.dept_entry.delete(0, "end")

        # 刷新列表
        self._load_participants()
        messagebox.showinfo("成功", f"已添加: {name}")

    def _delete_participant(self, participant_id: int):
        """删除参与者"""
        if messagebox.askyesno("确认", "确定要删除该参与者吗？"):
            self.data_manager.delete_participant(participant_id)
            self._load_participants()

    def _import_from_file(self):
        """从文件导入"""
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f if line.strip()]

            count = self.data_manager.add_participants_batch(names)
            self._load_participants()
            messagebox.showinfo("成功", f"成功导入 {count} 名参与者")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")

    def _clear_all(self):
        """清空所有参与者"""
        if messagebox.askyesno("确认", "确定要清空所有参与者吗？此操作不可恢复！"):
            self.data_manager.clear_participants()
            self._load_participants()

    def _export_participants(self):
        """导出参与者名单"""
        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")]
        )
        if not file_path:
            return

        if self.data_manager.export_to_txt(file_path):
            messagebox.showinfo("成功", f"已导出到: {file_path}")
        else:
            messagebox.showerror("错误", "导出失败")