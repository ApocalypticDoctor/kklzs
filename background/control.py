import time
import win32gui
import win32con
import win32api
from constant import hwnd


class Control:
    def __init__(self, hwnd: int):
        self.hwnd = hwnd

    def fight_click(self, x: int | float = 0, y: int | float = 0):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        long_position = win32api.MAKELONG(x, y)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
        time.sleep(0.05)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)

    def click(self, x: int | float = 0, y: int | float = 0):
        self.fight_click(x, y)
        time.sleep(0.2)

    def mouse_middle(self, x: int = 0, y: int = 0):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        self.activate()
        long_position = win32api.MAKELONG(x, y)  # 生成坐标
        win32gui.PostMessage(self.hwnd, win32con.WM_MBUTTONDOWN, win32con.MK_MBUTTON, long_position)  # 鼠标中键按下
        win32gui.PostMessage(self.hwnd, win32con.WM_MBUTTONUP, win32con.MK_MBUTTON, long_position)  # 鼠标中键抬起

    def mouse_press(self, x: int | float = 0, y: int | float = 0):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        long_position = win32api.MAKELONG(x, y)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)

    def mouse_release(self, x: int | float = 0, y: int | float = 0):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        long_position = win32api.MAKELONG(x, y)
        win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)

    def scroll(self, count: int, x: int | float = 0, y: int | float = 0):
        count = count if isinstance(count, int) else int(count)
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        lParam = win32api.MAKELONG(x, y)
        wParam = win32api.MAKELONG(0, win32con.WHEEL_DELTA * count)
        win32gui.SendMessage(self.hwnd, win32con.WM_MOUSEWHEEL, wParam, lParam)
        time.sleep(0.3)

    def tap(self, key: str | int):
        if isinstance(key, str):
            key = ord(key.upper())
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)
        time.sleep(0.04)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, key, 0)

    def esc(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)

    def key_press(self, key: int | str):
        if isinstance(key, str):
            key = ord(key.upper())
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)

    def key_release(self, key: int | str):
        if isinstance(key, str):
            key = ord(key.upper())
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, key, 0)

    def activate(self, flag=True):
        win32gui.PostMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        if flag:
            time.sleep(0.2)

    def inactivate(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_INACTIVE, 0)

    def space(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)

    def shift(self):
        long_position = win32api.MAKELONG(0, 0)
        win32gui.PostMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, long_position)
        time.sleep(0.1)
        win32gui.PostMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, long_position)
        time.sleep(0.2)

    def zhongji(self):
        self.mouse_press()
        time.sleep(0.5)
        self.mouse_release()

    def altPress(self):
        win32gui.PostMessage(hwnd, win32con.WM_SYSKEYDOWN, win32con.VK_MENU, 0)

    def altRepress(self):
        win32gui.PostMessage(hwnd, win32con.WM_SYSKEYUP, win32con.VK_MENU, 0)
control = Control(hwnd)