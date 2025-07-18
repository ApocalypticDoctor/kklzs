import math
import time

from ocr import ocr
from constant import width_ratio, height_ratio
from status import logger, info
from control import control
from config import config
from utils import wait_home, forward, random_click, screenshot, jinru, find_text, release_skills, lock_4c, tempy, \
    find_pic, template_pic

def challenge1():
    if config.TargetChallenge == "迅刀":
        num = 0
    elif config.TargetChallenge == "音感仪":
        num = 1
    elif config.TargetChallenge == "长刃":
        num = 2
    elif config.TargetChallenge == "拳套":
        num = 3
    else:
        num = 4
    random_click(1700, 305 + 155 * num)  # 前往n号位
    time.sleep(1)
    random_click(1600, 1000)  # 快速旅行
    logger("等待传送完成", flag=False)
    time.sleep(2)
    wait_home()
    logger("传送完成", flag=False)
    forward(0.5)
    jinru(False)
    for i in range(3):
        if num in [1, 4]:
            forward(3)
        else:
            forward(4)
        control.tap("f")
        control.tap("f")
        # 战斗
        time.sleep(3)
        info.fighttype = "每日"
        info.overflag = False
        info.ruleIndex = 0
        release_skills()
        time.sleep(1.5)
        control.mouse_middle()
        control.tap("1")
        gain(i)
        wait_home()


def challenge2():
    tz_dict = {
        "愿戴/奔狼": "哀",
        "流云/幽夜": "贝奥海域",
        "此间/无惧": "黎乔利群岛",
        "凌冽/此间": "生半岛",
        "幽夜/高天": "悲叹墓岛",
        "风套/冰套": "荒石高地",
        "冰套/雷套": "虎口山脉",
        "光套/不绝": "怨鸟泽",
        "雷套/火套": "归墟港市",  # 荒石高地2
        "暗套/轻云": "无光之森"
    }
    y = 200
    while y < 940:
        y = y + 270
        if y > 940:
            y = 940
        find = find_text(830, 220, 1100, 950, tz_dict.get(config.TargetChallenge))
        if find:
            break
        random_x = int(1880) * width_ratio
        random_y = int(y) * height_ratio
        control.fight_click(random_x, random_y)
        if config.TargetChallenge == "雷套/火套":
            y += 155
        random_click(1880, y)
        time.sleep(0.1)
    random_click(1700, 220 + find.position.y2)
    time.sleep(0.8)
    random_click(1750, 1000)  # 快速旅行
    logger("等待传送完成", flag=False)
    time.sleep(2)
    wait_home()
    logger("传送完成", flag=False)
    for i in range(3):
        if i == 0:
            if config.TargetChallenge in ["暗套/轻云", "雷套/火套", "风套/冰套"]:
                forward(1.3)
            elif config.TargetChallenge == "幽夜/高天":
                control.key_press("a")
                time.sleep(0.5)
                control.key_press("w")
                time.sleep(5)
                control.key_release("a")
                control.key_release("w")
                control.mouse_middle()
                forward(4)
            elif config.TargetChallenge == "凌冽/此间":
                control.key_press("w")
                time.sleep(1)
                control.key_press("d")
                time.sleep(5)
                control.key_release("d")
                control.key_release("w")
                control.mouse_middle()
                forward(5)
            elif config.TargetChallenge == "此间/无惧":
                control.key_press("w")
                time.sleep(2)
                control.key_press("a")
                time.sleep(5)
                control.key_release("a")
                control.key_release("w")
                control.mouse_middle()
                forward(3)
            elif config.TargetChallenge == "流云/幽夜":
                forward(10)
            elif config.TargetChallenge == "愿戴/奔狼":
                forward(10)
        else:
            time.sleep(2)
            if config.TargetChallenge in ["风套/冰套", "冰套/雷套", "光套/不绝", "雷套/火套", "暗套/轻云"]:
                time.sleep(3)
            else:
                control.mouse_middle()
                forward(2.5)
        control.tap("f")
        control.tap("f")
        # 战斗
        if config.TargetChallenge in ["风套/冰套", "冰套/雷套", "光套/不绝", "雷套/火套", "暗套/轻云"]:
            time.sleep(4)
        time.sleep(1)
        info.fighttype = "每日"
        info.overflag = False
        info.ruleIndex = 0
        release_skills()
        time.sleep(3)
        control.mouse_middle()
        control.tap("1")
        gain(i)


def challenge3(sum):
    random_click(685, 885) # 下拖动
    random_click(685, 885) # 下拖动
    random_click(430, 870) # 肉鸽
    random_click(1720, 420) # 前往
    time.sleep(0.5)
    random_click(1750, 1000)  # 快速旅行
    logger("等待传送完成", flag=False)
    time.sleep(2)
    wait_home()
    logger("传送完成", flag=False)
    for i in range((sum + 60) // 120):
        control.tap("f")
        control.tap("f")
        time.sleep(2)
        random_click(1720, 980)
        time.sleep(1)
        random_click(1650, 990)
        random_click(1650, 990)
        time.sleep(0.5)
        wait_home()

        # 肉鸽1
        control.mouse_middle()
        forward(2.5)
        info.fighttype = "每日"
        info.overflag = False
        info.ruleIndex = 0
        release_skills()
        turn()
        gain(4)
        door()

        # 肉鸽2
        img = screenshot()
        if (img[int(63 * height_ratio), int(1244 * width_ratio)] > [250, 250, 250]).any():  # 精英小怪
            forward(6.5)
            info.fighttype = "每日"
            info.overflag = False
            info.ruleIndex = 0
            release_skills()
            turn()
            gain(4)
            door()
        else:
            if template_pic("task")[0] > int(960 * width_ratio):  # 悬崖
                control.key_press("w")
                time.sleep(0.5)
                control.shift()
                control.space()
                time.sleep(0.3)
                control.shift()
                for _ in range(5):
                    control.tap("t")
                    time.sleep(0.1)
                control.key_release("w")
                control.mouse_middle()
                forward(2.5)
                info.fighttype = "悬崖"
                release_skills()
                turn()
                control.key_press("w")
                while not find_pic(1460, 935, 1525, 1000, "t.png", 0.5):
                    pass
                control.tap("t")
                time.sleep(3)
                control.key_release("w")
                if find_pic(1460, 935, 1525, 1000, "t.png", 0.5):
                    control.key_press("w")
                    control.tap("t")
                    time.sleep(3)
                    control.key_release("w")
                gain(5)
                info.fighttype = "每日"
                info.overflag = False
                info.ruleIndex = 0
                release_skills()
                turn()
                gain(4)
                door()
            else:
                forward(2.5)
                control.tap("f")
                control.tap("f")
                time.sleep(0.5)
                info.fighttype = "每日"
                info.overflag = False
                info.ruleIndex = 0
                release_skills()
                turn()
                control.key_press("w")
                for _ in range(10):
                    control.mouse_middle()
                    time.sleep(0.3)
                    control.space()
                    time.sleep(0.3)
                    control.shift()
                control.key_release("w")
                info.fighttype = "每日"
                info.overflag = False
                info.ruleIndex = 0
                release_skills()
                turn()
                gain(4)
                door()

        # 肉鸽3
        control.mouse_middle()
        forward(3)
        info.fighttype = "每日"
        info.overflag = False
        info.ruleIndex = 0
        release_skills()
        turn()
        gain(4)
        door()

        # 肉鸽4
        control.key_press("w")
        for _ in range(2):
            time.sleep(0.5)
            control.shift()
        control.key_release("w")
        control.tap("f")
        time.sleep(0.5)
        random_click(420, 555)
        random_click(420, 555)
        random_click(1600, 1030)
        time.sleep(0.5)
        control.key_press("w")
        time.sleep(0.5)
        forward(2, "a")
        control.key_release("w")
        control.tap("f")
        time.sleep(0.5)
        for _ in range(5):
            control.click(int(1600 * width_ratio), int(1030 * height_ratio))
        control.esc()
        time.sleep(0.3)
        control.key_press("w")
        forward(0.5, "a")
        time.sleep(1.7)
        control.key_release("w")
        control.tap("f")
        control.tap("f")
        wait_home()

        # 肉鸽5
        forward(3)
        info.fighttype = "每日"
        info.overflag = False
        info.ruleIndex = 0
        release_skills()
        turn()
        gain(4)
        gain(3, i)

def gain(i, count=0):
    flag = True
    while True:
        if i >= 4:
            x, y = template_pic("task")
        else:
            try:
                x, y = template_pic("gain")
            except:
                if i < 2:
                    random_click(1280, 675)  # 确认
                    random_click(1280, 675)  # 确认
                    time.sleep(0.5)
                    random_click(1210, 920)  # 重新挑战
                    random_click(1210, 920)  # 重新挑战
                elif i == 2:
                    random_click(1280, 675)  # 确认
                    random_click(1280, 675)  # 确认
                    time.sleep(0.5)
                    random_click(700, 920)  # 退出
                    random_click(700, 920)  # 退出
                elif i == 3:
                    if count == 0:
                        random_click(650, 675)  # 单倍
                        random_click(650, 675)  # 单倍
                    else:
                        random_click(1300, 675)  # 双倍
                        random_click(1300, 675)  # 双倍
                    time.sleep(0.3)
                    random_click(960, 900)
                    control.esc()
                    random_click(650, 675)  # 退出
                    random_click(650, 675)  # 退出
                    time.sleep(0.3)
                    random_click(960, 920)  # 退出
                    random_click(960, 920)  # 退出
                    wait_home()
                return
        if flag:
            if x > int((960 + 75) * width_ratio):
                key = "d"
            elif x < int((960 - 75) * width_ratio):
                key = "a" 
            else:
                flag = False
                continue
            control.key_press(key)
            while True:
                if i >= 3:
                    try:
                        x, y = template_pic("task")
                    except:
                        pass
                else:
                    try:
                        x, y = template_pic("gain")
                    except:
                        control.tap("f")
                        control.tap("f")
                        time.sleep(0.5)
                        random_click(1280, 675)  # 确认
                        random_click(1280, 675)  # 确认
                        time.sleep(0.5)
                        if i < 2:
                            random_click(1210, 920)  # 重新挑战
                            random_click(1210, 920)  # 重新挑战
                            return
                        else:
                            random_click(700, 920)  # 退出
                            random_click(700, 920)  # 退出
                            return
                if int((960 - 75) * width_ratio) < x < int((960 + 75) * width_ratio):
                    control.key_release(key)
                    flag = False
                    break
            if i == 5:
                forward(0.5, "a")
        else:
            if y < int(540 * height_ratio):
                control.key_press("w")
            else:
                control.key_press("s")
            while True:
                img = screenshot()
                img = img[int(420 * height_ratio):int(630 * height_ratio), int(1335 * width_ratio):int(1470 * width_ratio)]
                if ocr(img):
                    control.key_release("w")
                    control.key_release("s")
                    control.tap("f")
                    control.tap("f")
                    time.sleep(0.5)
                    if i < 2:
                        random_click(1280, 675)  # 确认
                        random_click(1280, 675)  # 确认
                        time.sleep(0.5)
                        random_click(1210, 920)  # 重新挑战
                        random_click(1210, 920)  # 重新挑战
                    elif i == 2:
                        random_click(1280, 675)  # 确认
                        random_click(1280, 675)  # 确认
                        time.sleep(0.5)
                        random_click(700, 920)  # 退出
                        random_click(700, 920)  # 退出
                    elif i == 3:
                        if count == 0:
                            random_click(650, 675) # 单倍
                            random_click(650, 675) # 单倍
                        else:
                            random_click(1300, 675) # 双倍
                            random_click(1300, 675) # 双倍
                        time.sleep(0.3)
                        random_click(960, 900)
                        control.esc()
                        random_click(650, 675)  # 退出
                        random_click(650, 675)  # 退出
                        time.sleep(0.3)
                        random_click(960, 920)  # 退出
                        random_click(960, 920)  # 退出
                        wait_home()
                    elif i == 4:
                        random_click(420, 555)
                        random_click(420, 555)
                        random_click(1600, 1030)
                        time.sleep(0.5)
                        forward(1)
                    return

def turn():
    time.sleep(1.5)
    control.mouse_middle()
    control.tap("1")
    while True:
        try:
            x, y = template_pic("task")
        except:
            return
        if int((960 - 150) * width_ratio) <= x <= int((960 + 150) * width_ratio):
            break
        if int((540 - 40) * height_ratio) <= y <= int((540 + 40) * height_ratio):
            break
        # 计算角度（弧度），然后转换为度数
        angle = math.degrees(math.atan2((y - int(540 * width_ratio)), (x - int(960 * height_ratio)))) % 360
        # 判断区域
        sector = int(angle // 45) + 1  # 每45度一个区域，共8个区域
        key_dict = {
            1: ("d", "s"),
            2: ("s", "d"),
            3: ("s", "a"),
            4: ("a", "s"),
            5: ("a", "w"),
            8: ("d", "w")
        }
        if sector not in [6, 7]:
            key = key_dict.get(sector)
            control.key_press(key[0])
            forward(0.1, key[1])
            control.key_release(key[0])
            time.sleep(0.5)
            control.mouse_middle()
            time.sleep(0.5)
        else:
            break

def door():
    while True:
        img = screenshot()
        img = img[int(0 * height_ratio):int(540 * height_ratio), int(885 * width_ratio):int(1035 * width_ratio)]
        res = ocr(img)
        if res:
            while True:
                forward(0.7)
                img = screenshot()
                img = img[int(420 * height_ratio):int(630 * height_ratio), int(1335 * width_ratio):int(1470 * width_ratio)]
                if ocr(img):
                    control.tap("f")
                    control.tap("f")
                    time.sleep(3)
                    return
        else:
            control.tap("a")
            control.tap("a")
            control.tap("w")
            control.mouse_middle()
            time.sleep(0.5)