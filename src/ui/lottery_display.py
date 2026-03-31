# -*- coding: utf-8 -*-
"""
抽奖展示面板 - 包含动画效果
"""
import customtkinter as ctk
import random
import math
from tkinter import messagebox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.utils.data_manager import DataManager
    from src.core.lottery_engine import LotteryEngine
import config


class LotteryDisplay(ctk.CTkFrame):
    """抽奖展示面板"""

    def __init__(self, master, data_manager: "DataManager", lottery_engine: "LotteryEngine"):
        super().__init__(master)
        self.data_manager = data_manager
        self.lottery_engine = lottery_engine

        # 动画状态
        self.is_rolling = False
        self.roll_job = None
        self.current_name = ""

        # 粒子系统
        self.particles = []
        self.particle_job = None

        self._create_ui()
        self._update_stats()

    def _create_ui(self):
        """创建UI"""
        # 顶部信息栏
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=20, pady=20)

        # 当前奖项选择
        prize_label = ctk.CTkLabel(top_frame, text="选择奖项:", font=ctk.CTkFont(size=14))
        prize_label.pack(side="left", padx=10)

        self.prize_var = ctk.StringVar(value="请选择奖项")
        self.prize_menu = ctk.CTkOptionMenu(top_frame, variable=self.prize_var, command=self._on_prize_selected)
        self.prize_menu.pack(side="left", padx=10, fill="x", expand=True)

        self.refresh_btn = ctk.CTkButton(top_frame, text="刷新", width=80, command=self._refresh_prizes)
        self.refresh_btn.pack(side="right", padx=10)

        # 中间展示区 - Canvas用于绘制粒子特效
        self.canvas = ctk.CTkCanvas(
            self,
            bg=config.COLORS["bg_dark"],
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=20, pady=10)

        # 姓名显示标签（覆盖在Canvas上）
        self.name_label = ctk.CTkLabel(
            self.canvas,
            text="准备抽奖",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=config.COLORS["accent_blue"]
        )
        self.name_label.place(relx=0.5, rely=0.5, anchor="center")

        # 状态信息
        self.status_label = ctk.CTkLabel(
            self,
            text="请先选择奖项，然后点击开始抽奖",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=5)

        # 底部控制区
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=20, pady=20)

        # 开始/停止按钮
        self.start_btn = ctk.CTkButton(
            bottom_frame,
            text="🎰 开始抽奖",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=50,
            command=self._toggle_lottery
        )
        self.start_btn.pack(side="left", padx=20, fill="x", expand=True)

        # 统计信息
        stats_frame = ctk.CTkFrame(bottom_frame)
        stats_frame.pack(side="right", padx=20)

        self.participants_count_label = ctk.CTkLabel(stats_frame, text="参与人数: 0")
        self.participants_count_label.pack(pady=5)

        self.remaining_count_label = ctk.CTkLabel(stats_frame, text="剩余人数: 0")
        self.remaining_count_label.pack(pady=5)

        self.winner_count_label = ctk.CTkLabel(stats_frame, text="已中奖: 0")
        self.winner_count_label.pack(pady=5)

        # 初始化奖项列表
        self._refresh_prizes()

    def _refresh_prizes(self):
        """刷新奖项列表"""
        prizes = self.data_manager.get_prizes()
        prize_options = []

        for p in prizes:
            remaining = p['count'] - p.get('drawn', 0)
            if remaining > 0:
                prize_options.append(f"{p['name']} (剩余{remaining}名)")
            else:
                prize_options.append(f"{p['name']} (已完成)")

        if prize_options:
            self.prize_menu.configure(values=prize_options)
            if not self.prize_var.get() or self.prize_var.get() == "请选择奖项":
                self.prize_var.set(prize_options[0])
                self._on_prize_selected(prize_options[0])
        else:
            self.prize_menu.configure(values=["暂无奖项"])
            self.prize_var.set("暂无奖项")

        self._update_stats()

    def _on_prize_selected(self, selected: str):
        """奖项选择回调"""
        if selected == "暂无奖项" or selected == "请选择奖项":
            return

        # 提取奖项名称
        prize_name = selected.split(" (")[0]
        prizes = self.data_manager.get_prizes()

        for p in prizes:
            if p['name'] == prize_name:
                result = self.lottery_engine.set_current_prize(p['id'])
                if result['success']:
                    remaining = p['count'] - p.get('drawn', 0)
                    self.status_label.configure(text=f"已选择: {p['name']}，还可抽取 {remaining} 名")
                else:
                    self.status_label.configure(text=result['message'])
                break

        self._update_stats()

    def _update_stats(self):
        """更新统计信息"""
        all_count = len(self.data_manager.get_participants())
        remaining_count = self.lottery_engine.get_remaining_count()
        winner_count = len(self.data_manager.get_results())

        self.participants_count_label.configure(text=f"参与人数: {all_count}")
        self.remaining_count_label.configure(text=f"剩余人数: {remaining_count}")
        self.winner_count_label.configure(text=f"已中奖: {winner_count}")

    def _toggle_lottery(self):
        """切换抽奖状态"""
        if not self.is_rolling:
            # 开始抽奖
            can_draw, message = self.lottery_engine.can_draw()
            if not can_draw:
                messagebox.showwarning("提示", message)
                return

            self.is_rolling = True
            self.start_btn.configure(text="⏹ 停止抽奖", fg_color=config.COLORS["accent_red"])
            self._start_roll_animation()
            self._start_particle_animation()
        else:
            # 停止抽奖，正式抽取
            self.is_rolling = False
            self.start_btn.configure(text="🎰 开始抽奖", fg_color=None)
            self._stop_and_draw()

    def _start_roll_animation(self):
        """开始姓名滚动动画"""
        if not self.is_rolling:
            return

        # 获取随机姓名用于展示
        names = self.lottery_engine.get_random_names_for_animation(1)
        if names:
            self.current_name = names[0]
            # 随机选择颜色
            colors = [config.COLORS["accent_blue"], config.COLORS["accent_purple"], config.COLORS["gold"]]
            color = random.choice(colors)
            self.name_label.configure(text=self.current_name, text_color=color)

        # 继续动画
        self.roll_job = self.after(50, self._start_roll_animation)

    def _stop_and_draw(self):
        """停止滚动并执行真实抽奖"""
        # 停止滚动动画
        if self.roll_job:
            self.after_cancel(self.roll_job)
            self.roll_job = None

        # 执行真实抽奖
        result = self.lottery_engine.draw()

        if result:
            winner = result['winner']
            prize = result['prize']

            # 显示中奖者
            self.name_label.configure(
                text=f"🎉 {winner['name']} 🎉",
                text_color=config.COLORS["gold"]
            )

            # 触发烟花效果
            self._firework_effect()

            # 更新状态
            self.status_label.configure(text=f"恭喜 {winner['name']} 获得 {prize['name']}！")
            messagebox.showinfo("恭喜", f"中奖者: {winner['name']}\n奖项: {prize['name']}")
        else:
            self.name_label.configure(text="抽奖失败", text_color=config.COLORS["accent_red"])
            self.status_label.configure(text="无法抽奖，请检查设置")

        # 更新统计
        self._update_stats()
        self._refresh_prizes()

    def _start_particle_animation(self):
        """启动粒子动画"""
        # 创建粒子
        self._create_particles()

        # 开始动画循环
        self._animate_particles()

    def _create_particles(self):
        """创建粒子"""
        self.particles = []
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        for _ in range(50):
            particle = {
                'x': random.randint(0, canvas_width),
                'y': random.randint(0, canvas_height),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'size': random.randint(2, 5),
                'color': random.choice([config.COLORS["accent_blue"], config.COLORS["accent_purple"], config.COLORS["gold"]])
            }
            self.particles.append(particle)

    def _animate_particles(self):
        """粒子动画"""
        if not self.is_rolling:
            self._clear_particles()
            return

        # 清除画布
        self.canvas.delete("particle")

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 更新粒子位置
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']

            # 边界反弹
            if p['x'] < 0 or p['x'] > canvas_width:
                p['vx'] *= -1
            if p['y'] < 0 or p['y'] > canvas_height:
                p['vy'] *= -1

            # 绘制粒子
            self.canvas.create_oval(
                p['x'] - p['size'],
                p['y'] - p['size'],
                p['x'] + p['size'],
                p['y'] + p['size'],
                fill=p['color'],
                outline='',
                tags="particle"
            )

        # 继续动画
        self.particle_job = self.after(30, self._animate_particles)

    def _clear_particles(self):
        """清除粒子"""
        if self.particle_job:
            self.after_cancel(self.particle_job)
            self.particle_job = None
        self.canvas.delete("particle")
        self.particles = []

    def _firework_effect(self):
        """烟花效果"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 在中心位置创建烟花
        center_x = canvas_width // 2
        center_y = canvas_height // 2

        # 创建多个爆炸粒子
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            particle = {
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(3, 8),
                'color': random.choice([config.COLORS["gold"], config.COLORS["accent_purple"], config.COLORS["accent_blue"], config.COLORS["accent_red"]]),
                'life': 30  # 生命周期
            }
            self.particles.append(particle)

        # 开始烟花动画
        self._animate_firework()

    def _animate_firework(self):
        """烟花动画"""
        if not self.particles:
            self.canvas.delete("firework")
            return

        # 清除之前的烟花
        self.canvas.delete("firework")

        # 更新和绘制粒子
        new_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.5  # 重力
            p['life'] -= 1

            if p['life'] > 0:
                # 绘制粒子
                self.canvas.create_oval(
                    p['x'] - p['size'],
                    p['y'] - p['size'],
                    p['x'] + p['size'],
                    p['y'] + p['size'],
                    fill=p['color'],
                    outline='',
                    tags="firework"
                )
                new_particles.append(p)

        self.particles = new_particles

        # 继续动画
        if self.particles:
            self.after(30, self._animate_firework)
        else:
            self.canvas.delete("firework")