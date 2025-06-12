import ctypes

import win32gui
import sys
from ctypes import windll
import os

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

hwnd = win32gui.FindWindow("UnrealWindow", "鸣潮  ")
if hwnd == 0:
    print("先启动游戏 再启动脚本啊 屌毛!红")
    sys.exit(0)
if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    print("管理员启动程序啊 屌毛!红")
    sys.exit(0)
left, top, right, bot = win32gui.GetClientRect(hwnd)
w = right - left
h = bot - top
scale_factor = windll.shcore.GetScaleFactorForDevice(0) / 100  # 返回百分比形式的缩放因子
width_ratio = w / 1920 * scale_factor
height_ratio = h / 1080 * scale_factor
real_w = int(w * scale_factor)
real_h = int(h * scale_factor)
windll.shcore.SetProcessDpiAwareness(1)  # 设置dpi感知
