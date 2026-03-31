# -*- coding: utf-8 -*-
"""
PickMe 抽奖系统配置文件
"""

# 窗口配置
WINDOW_TITLE = "PickMe 抽奖系统"
WINDOW_SIZE = (1200, 800)
WINDOW_MIN_SIZE = (1000, 700)

# 颜色配置 - 酷炫科技风
COLORS = {
    "bg_dark": "#0f0f1a",           # 背景色
    "bg_medium": "#1a1a2e",         # 中等背景色
    "accent_blue": "#00fff5",       # 霓虹蓝
    "accent_purple": "#ff00ff",     # 霓虹紫
    "accent_red": "#ff0055",        # 霓虹红
    "text_white": "#ffffff",        # 文字白色
    "text_gray": "#888888",         # 灰色文字
    "gold": "#FFD700",              # 金色
    "silver": "#C0C0C0",            # 银色
    "bronze": "#CD7F32",            # 铜色
}

# 字体配置
FONTS = {
    "title": ("微软雅黑", 24, "bold"),
    "name_display": ("微软雅黑", 48, "bold"),
    "subtitle": ("微软雅黑", 18, "bold"),
    "normal": ("微软雅黑", 14),
    "small": ("微软雅黑", 12),
}

# 动画配置
ANIMATION = {
    "roll_speed": 0.05,             # 姓名滚动速度（秒）
    "roll_deceleration": 0.002,     # 减速系数
    "particle_count": 100,          # 粒子数量
    "firework_particles": 50,       # 烟花粒子数量
}

# 数据文件路径
DATA_FILES = {
    "participants": "data/participants.json",
    "prizes": "data/prizes.json",
    "results": "data/results.json",
}

# 默认奖项配置
DEFAULT_PRIZES = [
    {"id": 1, "name": "特等奖", "count": 1, "drawn": 0, "color": COLORS["gold"]},
    {"id": 2, "name": "一等奖", "count": 3, "drawn": 0, "color": COLORS["silver"]},
    {"id": 3, "name": "二等奖", "count": 5, "drawn": 0, "color": COLORS["bronze"]},
]