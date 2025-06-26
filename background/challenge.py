import time

import cv2
import win32con

#from yolo import search_echoes
from ocr import everyday_ocr
from constant import width_ratio, height_ratio
from status import logger, info
from control import control
from config import config
from utils import wait_home, forward, random_click, screenshot, turn_forward, jinru, find_text, release_skills, lock_4c

addy = 0
count = 0
xiaohao = 0


def reset():
    global addy, count, xiaohao
    addy = 0
    count = 0
    xiaohao = 0


def challenge(sum, tempy):
    global xiaohao, addy
    name = config.TargetChallenge
    info.bossName = ""
    logger("当前副本为:" + name + "本", "蓝")
    while xiaohao < sum:
        control.activate()
        if not xiaohao:
            if name == "无音区":
                challenge3(tempy)
            else:
                if name in ["角色", "武器", "贝币"]:
                    challenge1(name, tempy)
                else:
                    challenge2(name, tempy)
                wait_home()
                logger("进入副本", "绿")
                time.sleep(0.3)
                control.mouse_middle()
                time.sleep(0.4)
                if name in ["角色", "武器", "贝币"]:
                    forward(2.2)
                else:
                    forward(3)
        else:
            if name != "无音区":
                random_click(1220, 920)  # 再次挑战
                time.sleep(2)
                wait_home()
                logger("进入副本", "绿")
                time.sleep(0.3)
                control.mouse_middle()
                time.sleep(0.4)
                if name in ["角色", "武器", "贝币"]:
                    forward(2.2)
                else:
                    forward(3)
            else:
                random_click(960, 920 + addy)  # 退出
                random_click(960, 920 + addy)  # 退出
                time.sleep(1.5)
        control.activate()
        control.mouse_middle()
        control.tap("f")
        logger("开启挑战", "绿")
        info.fighttype = "每日"
        info.bossName = ""
        info.overflag = False
        if name in ["角色", "武器", "贝币", "迅刀", "音感仪", "长刃", "拳套", "枪"]:
            time.sleep(3)
        else:
            time.sleep(5)
        release_skills()
        control.mouse_middle()
        time.sleep(0.4)
        logger("战斗结束", "绿")

        control.tap("1")
        time.sleep(0.5)
        control.tap("e")
        time.sleep(0.1)
        control.space()
        control.click()
        time.sleep(0.3)

        if name in ["角色", "武器", "贝币", "迅刀", "音感仪", "长刃", "拳套", "枪"]:
            pass
            # for i in range(4):
            #     img = screenshot()
            #     x = search_echoes(img)
            #     if x is not None:
            #         break
            #     control.tap("a")
            #     time.sleep(0.3)
            #     control.mouse_middle()
            #     time.sleep(0.4)
            # while True:
            #     if gain(name):
            #         break
            #     img = screenshot()
            #     x = search_echoes(img)  # 领取奖励在屏幕上的x
            #     if x is None or x < 910 * width_ratio:
            #         turn_forward("a")
            #     elif x > 1010 * width_ratio:
            #         turn_forward("d")
            #     else:
            #         break
        else:
            time.sleep(3)
        a = time.time()
        while True:
            if name == "无音区" and time.time() - a > 15:
                logger("领取超时", "红")
                time.sleep(90)
                challenge(sum, tempy)
                return
            if gain(name):
                break
            forward(0.6)
            time.sleep(0.2)

    logger("体力已经清理完毕", "绿")
    if name == "无音区":
        random_click(960, 920)  # 退出
        random_click(960, 920)  # 退出
        time.sleep(1)
        control.tap("b")
        time.sleep(1)
        random_click(75, 330)
        img = screenshot()
        img = img[int(45 * height_ratio):int(90 * height_ratio), int(160 * width_ratio):int(330 * width_ratio)]
        res = everyday_ocr(img)
        if type(res) == int:
            info.echoNum = res
            logger("获取声骸个数成功 当前个数为" + str(info.echoNum), "蓝")
        else:
            logger("获取声骸个数失败!", "红")

        random_click(230, 988)  # 筛选
        random_click(1180, 900)  # 重置
        random_click(1180, 900)  # 重置
        random_click(1560, 905)  # 确定
        time.sleep(0.5)
        random_click(370, 985)  # 排序
        random_click(385, 780)  # 获得时间
        random_click(730, 935)  # 空白
        img = screenshot(1)
        img1 = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)
        if (img1[993, 649] < [140, 140, 140]).any():
            random_click(640, 985)  # 反转
        lock_4c(True)
        control.tap("b")
        time.sleep(0.5)
    else:
        random_click(700, 920)  # 退出副本
        random_click(700, 920)  # 退出副本
        time.sleep(2)
        wait_home()
        logger("传送完成")
    control.tap(win32con.VK_F2)
    time.sleep(1)


def challenge1(name, tempy):
    global addy, count
    if name == "角色":
        num = 0
    elif name == "武器":
        num = 1
    else:
        num = 2
    random_click(77, 315 + tempy)  # 周期挑战
    time.sleep(0.3)
    random_click(400, 300)  # 模拟领域
    time.sleep(0.3)
    img = screenshot()
    img = img[int(130 * height_ratio):int(180 * height_ratio), int(700 * width_ratio):int(1100 * width_ratio)]
    res = everyday_ocr(img)
    if type(res) == int:
        count = res
        addy = 48
    random_click(1700, 270)  # 前往1号位
    time.sleep(1.5)
    random_click(1600, 1000)  # 快速旅行
    logger("等待传送完成")
    time.sleep(2)
    wait_home()  # 等待回到主界面
    logger("传送完成")
    forward(1)
    jinru(False, num)


def challenge2(name, tempy):
    global addy, count
    if name == "迅刀":
        num = 0
    elif name == "音感仪":
        num = 1
    elif name == "长刃":
        num = 2
    elif name == "拳套":
        num = 3
    else:
        num = 4
    y = 265 + 155 * num
    random_click(77, 315 + tempy)  # 周期挑战
    time.sleep(0.3)
    img = screenshot()
    img = img[int(130 * height_ratio):int(180 * height_ratio), int(700 * width_ratio):int(1100 * width_ratio)]
    res = everyday_ocr(img)
    if type(res) == int:
        count = res
        addy = 48
    random_click(1700, y)  # 前往n号位
    time.sleep(1)
    random_click(1600, 1000)  # 快速旅行
    logger("等待传送完成")
    time.sleep(2)
    wait_home()
    logger("传送完成")
    forward(1)
    jinru(False, 5)


def challenge3(tempy):
    global addy, count
    random_click(77, 315 + tempy)  # 周期挑战
    time.sleep(0.3)
    random_click(400, 500)  # 无音清剿
    time.sleep(0.3)
    img = screenshot()
    img = img[int(130 * height_ratio):int(180 * height_ratio), int(700 * width_ratio):int(1100 * width_ratio)]
    res = everyday_ocr(img)
    if type(res) == int:
        count = res
        addy = 48
    random_click(1880, 940)  # 往下拖动
    time.sleep(0.3)
    random_click(1700, 870)  # 前往无光之森
    time.sleep(0.8)
    random_click(1750, 1000)  # 快速旅行
    logger("等待传送完成")
    time.sleep(2)
    wait_home()
    logger("传送完成")
    forward(1.3)


def gain(name):
    global addy, count, xiaohao
    addy = 40
    if count == 0:
        addy = 0
    if find_text(1330, 530, 1450, 580, "领取奖励"):
        a = 40
        if name == "无音区":
            a = 60
        if count > 0 or not info.waveplates:
            a *= 2
        control.tap("f")
        time.sleep(1)
        if a == 80 or a == 120:
            random_click(1300, 670 + addy)  # 确认
            random_click(1300, 670 + addy)  # 确认
        else:
            random_click(620, 670 + addy)  # 确认
            random_click(620, 670 + addy)  # 确认
        logger("领取奖励成功", "绿")
        if count > 0:
            a //= 2
        xiaohao += a
        info.waveplate -= a
        info.waveplates += a
        info.ruleIndex = 0
        count -= 1
        time.sleep(2)
        return True
    return False
