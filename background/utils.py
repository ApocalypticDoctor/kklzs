import concurrent.futures
import glob
import re
import threading
import time
import cv2
import psutil
import win32gui
import win32process
import win32ui
import os
import win32con
import numpy as np

from PIL import Image
from ctypes import windll
from status import info, logger
from typing import List
from constant import root_path, hwnd, real_w, real_h, width_ratio, height_ratio
from ocr import ocr, everyday_ocr
from schema import match_template, OcrResult
from control import control
from config import config
from datetime import datetime


index = 0  # 实际索引
keyflag = False  # 梦魇复刷往前跑
active = "dev"
mutex = threading.Lock()
die = []
x, y = (0, 45)
pool = concurrent.futures.ThreadPoolExecutor(max_workers=8)
fightDict = {
    "a": control.fight_click,
    "s": control.space,
    "l": control.shift,
}

def get_file_count(folder_path):
    file_list = glob.glob(folder_path + "/*")
    return len(file_list)


def release_skills():
    global index, keyflag
    control.activate()
    if keyflag and info.bossName in ["梦魇无冠者", "梦魇燎照之骑"]:
        control.mouse_middle()
        control.key_press("w")
        time.sleep(0.2)
        control.mouse_middle()
        control.shift()
        control.mouse_middle()
        time.sleep(0.2)
        control.mouse_middle()
        control.shift()
        control.mouse_middle()
        time.sleep(0.2)
        control.mouse_middle()
        control.key_release("w")
    keyflag = True
    if info.waitBoss:
        boss_wait()
    while True:
        index = config.RoleIndex[info.ruleIndex]
        tactics = config.FightTactics[info.ruleIndex].split(",")
        info.ruleIndex += 1
        if info.ruleIndex == len(config.RoleIndex):
            info.ruleIndex = 0
        if index in die:
            continue
        if fight(tactics, True):
            return


def release_skills_after_ult():
    try:
        tacticsUlt = config.FightTacticsUlt[info.ruleIndex - 1].split(",")
        fight(tacticsUlt, False)
    except:
        pass


def fight(tactics, flag):
    while True:
        img = screenshot()
        if info.overflag:
            return True  # 提前结束
        if info.fighttype == "boss" and (img[int(46 * height_ratio), int(1726 * width_ratio)] > [254, 254, 254]).all():  # 没开大招
            break
        if info.fighttype == "每日" and (img[int(54 * height_ratio), int(40 * width_ratio)] > [254, 254, 254]).all():  # 没开大招
            break
    for tactic in tactics:  # 遍历对应角色的战斗策略
        if info.overflag:
            return True  # 提前结束
        #  判断 flag 状态，若为真，则执行一些操作
        if index in die:
            return False
        control.tap(index)
        control.mouse_middle()
        pool.submit(over_fight)
        try:
            wait_time = float(tactic)
            time.sleep(wait_time)
        except:
            if tactic in ["e", "t", "q"]:
                if info.overflag:
                    return True  # 提前结束
                control.tap(tactic)
            elif tactic == "r" and flag:  # 大招处理
                if info.overflag:
                    return True  # 提前结束
                control.tap(tactic)
                time.sleep(0.1)
                img = screenshot()
                if (img[int(46 * height_ratio), int(1726 * width_ratio)] < [255, 255, 255]).all():  # 等待大招时间
                    while True:
                        img = screenshot()
                        if (img[int(46 * height_ratio), int(1726 * width_ratio)] > [254, 254, 254]).all():  # 等待大招时间
                            pool.submit(over_fight)
                            release_skills_after_ult()
                            break
            elif tactic in fightDict:
                if info.overflag:
                    return True  # 提前结束
                fightDict.get(tactic)()
            elif tactic == "z":
                if info.overflag:
                    return True  # 提前结束
                control.zhongji()
            else:
                continuous_tap_time = float(tactic[tactic.find("(") + 1:tactic.find(")")])
                tap_start_time = time.time()
                while time.time() - tap_start_time <= continuous_tap_time:
                    if info.overflag:
                        return True
                    if tactic[0] == "a":
                        control.fight_click()
                    else:
                        control.tap(tactic[0])
    return False  # 所有策略执行完后返回


def forward(cxk: float, f: str = "w"):
    control.key_press(f)
    time.sleep(cxk)
    control.key_release(f)


bossDict = {
    "鸣钟之龟": 3,
    "朔雷之鳞": 0,
    "燎照之骑": 2,
    "无常凶鹭": 3,
    "辉萤军势": 2,
    "飞廉之猩": 4,
    "哀声鸷": 4,
    "无冠者": 3,
    "聚械机偶": 6,
    "云闪之鳞": 2,
    "无归的谬误": 5,
    "罗蕾莱": 4,
    "异构武装": 3,
    "叹息古龙": 4,
    "梦魇飞廉之猩": 0,
    "梦魇无常凶鹭": 4,
    "梦魇云闪之鳞": 2,
    "梦魇朔雷之鳞": 2,
    "梦魇无冠者": 2,
    "梦魇燎照之骑": 3,
    "梦魇哀声鸷": 4,
    "梦魇辉萤军势": 1,
    "梦魇凯尔匹": 4,
    "荣耀狮像": 3,
    "梦魇赫卡忒": 0
}

bossPoint = {
    "鸣钟之龟": 829,   # **** · ****
    "无妄者": 877,    # ***
    "角": 838,    # * · ****
    "赫卡忒": 812,    # *** · ****
    "芙露德莉斯": 851,    # *****
    "朔雷之鳞": 829,
    "燎照之骑": 829,
    "无常凶鹭": 829,
    "辉萤军势": 829,
    "飞廉之猩": 829,
    "哀声鸷": 812,
    "无冠者": 829,    # *** · *****
    "聚械机偶": 864,    # ****
    "云闪之鳞": 829,
    "无归的谬误": 877,    # ***** · *****
    "罗蕾莱": 812,
    "异构武装": 829,
    "叹息古龙": 829,
    "梦魇飞廉之猩": 891,    # ** · **** · ****
    "梦魇无常凶鹭": 891,
    "梦魇云闪之鳞": 891,
    "梦魇朔雷之鳞": 891,
    "梦魇无冠者": 904,    # ** · *** · ****
    "梦魇燎照之骑": 891,
    "梦魇哀声鸷": 904,
    "梦魇辉萤军势": 891,
    "梦魇凯尔匹": 904,
    "荣耀狮像": 829,
    "芬莱克": 829,
    "梦魇赫卡忒": 904
}

def transfer_to_boss():
    random_click(77, 577 + tempy)  # 残像探寻
    random_click(77, 577 + tempy)  # 残像探寻
    findBoss = None
    y = 200
    while y < 610:
        y = y + 30
        findBoss = find_text(280, 135, 600, 900, info.bossName)
        if findBoss:
            break
        random_click(855, y)
        time.sleep(0.1)
    if not findBoss:
        control.esc()
        logger("未找到目标boss", "红")
        info.bossName = ""
        info.bossIndex = -1
        time.sleep(1)
        return False
    x = (findBoss.position.x1 + findBoss.position.x2) // 2
    y = (findBoss.position.y1 + findBoss.position.y2) // 2
    control.click(x + int(300 * width_ratio), y + int(135 * height_ratio))
    time.sleep(0.1)
    random_click(1700, 990)  # 探测
    time.sleep(1)
    random_click(1750, 1000)  # 快速旅行
    random_click(1750, 1000)  # 快速旅行
    time.sleep(2)
    wait_home()
    logger("传送完成", flag=False)
    if info.bossName in ["无妄者", "角", "赫卡忒"]:
        forward(0.8)
        jinru()
    elif info.bossName in ["芙露德莉斯"]:
        jinru()
    elif info.bossName == "梦魇赫卡忒":
        forward(0.5, "a")
        control.tap("f")
        control.tap("f")
        time.sleep(1)
        wait_home()
    else:
        move_boss()
    info.lastFightTime = datetime.now()  # 重置最近检测到战斗时间


def move_boss(flag=True):
    if info.bossName not in ["梦魇辉萤军势", "梦魇云闪之鳞"]:
        control.mouse_middle()
    if info.bossName == "罗蕾莱":
        time.sleep(0.5)
        if find_text(20, 265, 320, 310, "击败") and flag:
            control.esc()
            time.sleep(0.8)
            random_click(1370, 1035)
            time.sleep(0.5)
            random_click(370, 145)
            random_click(1765, 550)
            random_click(1765, 550)
            random_click(960, 1000)
            time.sleep(5)
            for i in range(2):
                control.esc()
                time.sleep(1)
    num = bossDict.get(info.bossName)
    if num:
        control.key_press("w")
        for i in range(num):
            control.shift()
            time.sleep(0.8)
            if info.bossName == "聚械机偶" and i == 4:
                control.space()
                time.sleep(1)
                control.space()
            if info.bossName == "飞廉之猩" and i == 3:
                forward(1, "a")
        control.key_release("w")
        if info.bossName == "梦魇朔雷之鳞":
            forward(0.8)
        else:
            forward(2)
    if info.bossName == "无冠者":
        control.tap("f")
        time.sleep(1)


def transfer_to_dreamless():
    random_click(77, 315 + tempy)  # 周期挑战
    random_click(77, 315 + tempy)  # 周期挑战
    time.sleep(0.3)
    random_click(400, 620)  # 战歌重奏
    time.sleep(0.3)
    random_click(1720, 320)  # 新周本
    time.sleep(0.3)
    if find_text(1230, 640, 1370, 700, "确认"):
        random_click(1300, 680)
        time.sleep(0.5)
        return True
    time.sleep(1)
    random_click(1600, 1000)  # 快速旅行
    random_click(1600, 1000)  # 快速旅行
    time.sleep(2)
    wait_home()
    logger("传送完成", flag=False)
    forward(0.8)
    jinru()
    return True


recovery = True
tempy = 0


def recover():
    time.sleep(0.2)
    logger("恢复线程启动", "绿")
    while True:
        if info.waveplate < 240:
            time.sleep(60 * 6)
            info.waveplate += 1
        else:
            time.sleep(10)


def new_everyday():
    logger("每日线程启动", "绿")
    while True:
        time.sleep(int(86400 - (time.time() - datetime(2025, 3, 3, 4, 0, 0).timestamp()) % 86400))
        if config.TargetChallenge != "关闭":
            info.waveplates = 0
        if find_text(760, 930, 1160, 1000, "点击领取今日月相观测卡奖励"):
            for i in range(3):
                random_click(600, 600)
                time.sleep(1)

t = None
def over_fight():
    global keyflag, t, die
    try:
        mutex.acquire()
        if not t:
            t = time.time()
        mutex.release()
        img = screenshot(1)
        if len(die) == 3:
            info.fighttype = ""
            info.overflag = True
            die = []
            if info.bossName in ["无妄者", "角", "赫卡忒", "芙露德莉斯"]:
                control.altPress()
                random_click(1210, 920)
                random_click(1210, 920)
                control.altRepress()
                time.sleep(1.5)
                wait_home()
            else:
                keyflag = False
                control.altPress()
                random_click(960, 960)
                random_click(960, 960)
                control.altRepress()
                time.sleep(1.5)
                wait_home()
                move_boss()
        if info.fighttype == "boss":
            if (img[int(46 * height_ratio), int(1726 * width_ratio)] > [254, 254, 254]).all(): #  角色图标
                if (img[int(y * height_ratio), int(x * width_ratio)] < [255, 255, 255]).all(): # boss没有血条
                    info.fighttype = ""
                    info.overflag = True
                    t = None
                if (img[int(289 * height_ratio), int(1755 * width_ratio)] < [150, 150, 150]).all() and "1" not in die: # 1号位死
                    die.append("1")
                    logger("1号位死了", "红")
                elif (img[int(421 * height_ratio), int(1755 * width_ratio)] < [150, 150, 150]).all() and "2" not in die: # 2号位死
                    die.append("2")
                    logger("2号位死了", "红")
                elif (img[int(553 * height_ratio), int(1755 * width_ratio)] < [150, 150, 150]).all() and "3" not in die: # 3号位死
                    die.append("3")
                    logger("3号位死了", "红")
            if info.bossName == "赫卡忒" and ((img[int(46 * height_ratio), int(1726 * width_ratio)] < [5, 5, 5]).all() and (img[int(61 * height_ratio), int(678 * width_ratio)] < [5, 5, 5]).all()):
                time.sleep(1)
        if "梦魇" in info.bossName and t and time.time() - t > 5 and info.bossName != "梦魇赫卡忒":
            if (img[int(46 * height_ratio), int(1726 * width_ratio)] > [254, 254, 254]).all():
                if (img[int(63 * height_ratio), int(1244 * width_ratio)] > [250, 250, 250]).any():
                    logger("超出场地", "红")
                    info.fighttype = ""
                    info.overflag = True
                    t = None
                    control.tap("1")
                    repeat_boss()
                else:
                    t = None

        if info.bossName in ["异构武装", "辉萤军势", "梦魇辉萤军势", "梦魇凯尔匹"]:
            img2 = img[int(240 * height_ratio):int(320 * height_ratio), int(830 * width_ratio):int(1075 * width_ratio)]
            res2 = ocr(img2)
            if res2 and res2[0].text == "交替点击进行挣脱":
                b = time.time()
                while time.time() - b < 3:
                    control.tap("a")
                    control.tap("d")
        if info.fighttype == "每日":
            img3 = img[int(240 * height_ratio):int(320 * height_ratio), int(830 * width_ratio):int(1075 * width_ratio)]  # 挑战成功
            res3 = ocr(img3)
            if (res3 and res3[0].text in ["挑战成功", "挑战达成"]):
                info.fighttype = ""
                info.overflag = True
        if info.fighttype == "悬崖" and template_pic("task"):
            info.fighttype = ""
            info.overflag = True


    except Exception as e:
        logger(str(e) + " over_fight")
        pass


def repeat_boss():
    control.tap("m")
    time.sleep(1)
    cx, cy = (0, 0)
    img = screenshot()
    img = img[int(490 * height_ratio):int(590 * height_ratio), int(910 * width_ratio):int(1010 * width_ratio)]

    for a in range(100):
        for b in range(100):
            if (img[b, a] == [255, 255, 255]).all():
                cx, cy = (910 + a, 490 + b)
                break
        if cx:
            break
    random_click(cx, cy)
    time.sleep(0.3)
    random_click(1750, 1000)  # 快速旅行
    random_click(1750, 1000)  # 快速旅行
    time.sleep(2)
    wait_home()
    logger("传送完成", flag=False)
    move_boss(False)
    if "梦魇" not in info.bossName:
        if info.bossName in ["罗蕾莱", "异构武装"]:
            forward(1, "a")
        elif info.bossName in ["叹息古龙", "无归的谬误"]:
            forward(1, "d")
        while True:
            forward(0.7)
            img = screenshot()
            img1 = img[int(420 * height_ratio):int(630 * height_ratio), int(1335 * width_ratio):int(1470 * width_ratio)]
            result = ocr(img1)
            if result:
                if len(result) == 3:
                    control.tap("2")
                    if result[0].text != "吸收":
                        control.scroll(1)
                    control.tap("f")
                    time.sleep(1)
                    control.tap("1")
                    if result[0].text == "吸收":
                        control.scroll(1)
                    info.absorptionCount += 1
                    info.echoNum += 1
                    logger("吸收声骸", "绿")
                elif len(result) == 2:
                    control.scroll(1)
                elif len(result) == 1:
                    control.tap("f")
                    continue
                control.tap("f")
                time.sleep(1)
                break
        time.sleep(1)
        if info.bossName == "罗蕾莱":
            time.sleep(0.5)
            if not find_text(20, 265, 320, 310, "击败"):
                control.esc()
                time.sleep(0.8)
                random_click(1370, 1035)
                time.sleep(0.5)
                random_click(370, 145)
                random_click(1765, 550)
                random_click(1765, 550)
                random_click(960, 1000)
                time.sleep(5)
                for i in range(2):
                    control.esc()
                    time.sleep(1)


def transfer():
    global recovery, tempy, keyflag, x
    keyflag = False
    control.activate()
    time.sleep(0.1)
    control.activate()
    a = int(86400 - (time.time() - datetime(2025, 3, 3, 4, 0, 0).timestamp()) % 86400)
    if a < 20:
        time.sleep(a + 5)
    if info.echoNum >= 3000:
        control.esc()
        time.sleep(0.5)
        random_click(1425, 484)
        time.sleep(0.5)
        random_click(70, 595)
        return True

    if info.waveplate == -1:  # 获取体力
        control.tap("m")
        time.sleep(1)
        random_click(1810, 620)
        img = screenshot()
        img = img[int(10 * height_ratio):int(100 * height_ratio), int(1460 * width_ratio):int(1700 * width_ratio)]
        res = everyday_ocr(img)
        if type(res) == int:
            info.waveplate = res
            logger("获取当前体力成功 当前体力为" + str(info.waveplate), "蓝")
        else:
            logger("获取当前体力失败！", "红")
        control.tap("m")
        time.sleep(1)
    if info.echoNum == 0:  # 获取声骸个数
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
        control.tap("b")
        time.sleep(0.5)
    if recovery:  # 体力恢复 and 每日刷新
        threading.Thread(target=new_everyday).start()
        threading.Thread(target=recover).start()
        recovery = False

    if config.IsWei:
        control.tap("1")
        time.sleep(0.2)
        control.tap("e")
        time.sleep(0.1)
        control.space()
        for i in range(config.TwoWei):
            control.click()

    if info.bossName == config.TargetBoss[info.bossIndex % len(config.TargetBoss)] and info.bossName not in ["无妄者", "角", "赫卡忒", "芙露德莉斯"] and (info.waveplates == 240 or info.waveplate < 60):
        info.waitBoss = True
        logger(f"当前目标boss: {info.bossName}")
        repeat_boss()
        info.lastFightTime = datetime.now()  # 重置最近检测到战斗时间
        return

    control.tap(win32con.VK_F2)
    time.sleep(0.8)
    if info.bossIndex == -1 and not find_pic(46, 411, 110, 475, "强者之路.png", 0.6):
        tempy = 140

    if config.TargetChallenge != "关闭":
        if find_pic(55, 45, 95, 96, "每日.png", 0.6):
            if info.waveplate >= 180:
                logger("进行第一次自动清体力", "蓝")
                everyday()
                info.waveplates = 180
        else:
            info.waveplate = 180
        if info.waveplate + int(86400 - (time.time() - datetime(2025, 3, 3, 4, 0, 0).timestamp()) % 86400) // 360 >= 240:
            if info.waveplate >= 60:
                from challenge import challenge3
                logger("进行第二次自动清体力", "蓝")
                challenge3(60)
            info.waveplates = 240
    else:
        info.waveplates = 240

    info.waitBoss = True
    info.bossIndex += 1
    info.bossName = config.TargetBoss[info.bossIndex % len(config.TargetBoss)]
    x = bossPoint.get(info.bossName)
    logger(f"当前目标boss: {info.bossName}")
    if info.bossName == "":
        return transfer_to_dreamless()
    else:
        return transfer_to_boss()


def jinru(flag=True):
    # 进入
    control.tap("f")
    control.tap("f")
    if flag:
        if info.bossName == "芙露德莉斯":
            time.sleep(5)
        time.sleep(2)
        y = ((config.DungeonWeeklyBossLevel - 40) / 10) * 85 + 197
        random_click(311, y)  # 推荐等级
        random_click(311, y)
    else:
        time.sleep(7)
    random_click(1720, 980)  # 单人挑战
    time.sleep(0.2)
    if info.waveplate < 60:
        time.sleep(0.3)
        random_click(1250, 680)  # 结晶波片不足
    time.sleep(1.3)
    random_click(1650, 990)  # 开启挑战
    random_click(1650, 990)  # 开启挑战
    time.sleep(1.3)
    wait_home()
    info.lastFightTime = datetime.now()


def screenshot(flag=0) -> np.ndarray | None:
    mutex.acquire()
    hwndDC = win32gui.GetWindowDC(hwnd)  # 获取窗口设备上下文（DC）
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 创建MFC DC从hwndDC
    saveDC = mfcDC.CreateCompatibleDC()  # 创建与mfcDC兼容的DC
    saveBitMap = win32ui.CreateBitmap()  # 创建一个位图对象
    saveBitMap.CreateCompatibleBitmap(mfcDC, real_w, real_h)  # 创建与mfcDC兼容的位图
    saveDC.SelectObject(saveBitMap)  # 选择saveDC的位图对象，准备绘图
    if windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3) != 1:
        logger("截取屏幕失败,游戏不要最小化!!!", "红")
        # 释放所有资源
        try:
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            del hwndDC, mfcDC, saveDC, saveBitMap
        except Exception as e:
            logger(f"1清理截图资源失败: {e}")
        mutex.release()
        time.sleep(3)
        return screenshot()  # 如果截取失败，则重试
    bmp_info = saveBitMap.GetInfo()  # 获取位图信息
    bmp_str = saveBitMap.GetBitmapBits(True)  # 获取位图数据
    im = np.frombuffer(bmp_str, dtype="uint8")  # 将位图数据转换为numpy数组
    im.shape = (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)  # 设置数组形状
    # 调整通道顺序 并 去除alpha通道
    im = im[:, :, [2, 1, 0, 3]][:, :, :3]
    if flag == 1:
        im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    # 清理资源
    try:
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        del hwndDC, mfcDC, saveDC, saveBitMap
    except Exception as e:
        info.fighttype = ""
        logger(f"2清理截图资源失败: {e}")
    mutex.release()
    return im  # 返回截取到的图像


def search_text(results: List[OcrResult], target: str) -> OcrResult | None:
    for result in results:
        if re.search(target, result.text):  # 使用正则匹配
            return result
    return None


def find_text(x1: int, y1: int, x2: int, y2: int, targets: str | list[str]) -> OcrResult | None:
    if "梦魇" in targets:
        targets = "·" + targets[2:]
    if "鸷" in targets:
        targets = targets[:-1]
    img = screenshot()
    img = img[int(y1 * height_ratio):int(y2 * height_ratio), int(x1 * width_ratio):int(x2 * width_ratio)]
    result = ocr(img)
    if text_info := search_text(result, targets):
        return text_info
    return None


def wait_home():
    a = time.time()
    while True:
        b = time.time()
        if int(b - a) > 15:
            logger("疑似卡死强制重启", "红")
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            psutil.Process(pid).terminate()
            time.sleep(999)
        img = screenshot(1)
        img = img[int(1050 * height_ratio):int(1080 * height_ratio), int(1695 * width_ratio):int(1920 * width_ratio)]
        if ocr(img):
            return
        control.click()
        time.sleep(0.2)

def absorption_action():
    global die
    t = time.time()
    a = int(86400 - (time.time() - datetime(2025, 3, 3, 4, 0, 0).timestamp()) % 86400)
    if a < 20:
        time.sleep(a + 5)
    control.tap("1")
    control.mouse_middle()
    if absorption_and_receive_rewards():
        if die:
            revive()
        return
    control.shift()
    time.sleep(1)
    if absorption_and_receive_rewards():
        if die:
            revive()
        return
    if info.bossName in ["梦魇哀声鸷"]:
        count = 3
    else:
        count = 5
    for _ in range(count):
        forward(0.7)
        if absorption_and_receive_rewards():
            if die:
                revive()
            time.sleep(t + 11 - time.time())
            return
    logger("未掉落声骸", "红")
    if die:
        revive()
    else:
        time.sleep(t + 9 - time.time())



def absorption_and_receive_rewards() -> bool:
    img = screenshot()
    img = img[int(420 * height_ratio):int(630 * height_ratio), int(1335 * width_ratio):int(1470 * width_ratio)]
    result = ocr(img)
    if result:
        time.sleep(0.1)
        img = screenshot(1)
        img = img[int(420 * height_ratio):int(630 * height_ratio), int(1335 * width_ratio):int(1470 * width_ratio)]
        result = ocr(img)
        if result:
            if info.bossName in ["无妄者", "角", "赫卡忒", "芙露德莉斯"]:
                if len(result) == 2 and result[0].text != "吸收":
                    control.scroll(1)
                elif result[0].text != "吸收":
                    return False
            else:
                if len(result) == 2 and result[0].text != "吸收":
                    logger("未掉落声骸", "红")
                    control.scroll(1)
                    control.tap("f")
                    time.sleep(1)
                    return True
                if len(result) == 3:
                    control.tap("2")
                    if result[0].text != "吸收":
                        control.scroll(1)
                    control.tap("f")
                    time.sleep(1)
                    control.tap("1")
                    if result[0].text == "吸收":
                        control.scroll(1)
                if "米" in result[0].text:
                    return False
            control.tap("f")
            time.sleep(1)
            info.absorptionCount += 1
            info.echoNum += 1
            logger("吸收声骸", "绿")
            return True
    else:
        return False


def revive():
    global die
    die = []
    info.bossName = ""
    control.tap(win32con.VK_F2)
    time.sleep(0.5)
    random_click(77, 315 + tempy)  # 周期挑战
    random_click(77, 315 + tempy)  # 周期挑战
    time.sleep(0.3)
    random_click(1810, 451)
    random_click(1700, 275)  # 复活
    time.sleep(0.8)
    random_click(815, 690)
    random_click(1750, 1000)  # 快速旅行
    time.sleep(2)
    wait_home()
    logger("复活完成")
    config.MaxIdleTime = 0

def random_click(x, y):
    random_x = int(x) * width_ratio
    random_y = int(y) * height_ratio
    control.click(random_x, random_y)


def boss_wait():
    if info.bossName == "鸣钟之龟":
        logger("龟龟需要等待15秒开始战斗!", flag=False)
        time.sleep(15)
    elif info.bossName == "聚械机偶":
        logger("机器人需要等待12秒开始战斗!", flag=False)
        time.sleep(11.5)
    elif info.bossName == "无归的谬误":
        logger("谬误需要等待6秒开始战斗!", flag=False)
        time.sleep(5.5)
    elif info.bossName == "无妄者":
        logger("无妄者需要等待2.2秒开始战斗!", flag=False)
        time.sleep(2.2)
    elif "哀声鸷" in info.bossName:
        time.sleep(0.5)
    elif info.bossName == "异构武装":
        time.sleep(1.5)
    elif info.bossName == "角":
        forward(2.5)
    elif info.bossName in ["赫卡忒", "芙露德莉斯"]:
        forward(4)
    info.waitBoss = False


def find_pic(x1: int, y1: int, x2: int, y2: int, template_name: str = None, threshold: float = 0.8,
             img: np.ndarray = None):
    if img is None:
        img = screenshot()
    img = img[int(y1 * height_ratio):int(y2 * height_ratio), int(x1 * width_ratio):int(x2 * width_ratio)]
    template = Image.open(os.path.join(root_path, "template", template_name))
    template = np.array(template)
    result = match_template(img, template, threshold)
    return result

def everyday():
    from challenge import challenge1, challenge2, challenge3
    random_click(77, 315 + tempy)  # 周期挑战
    if config.TargetChallenge in ["迅刀", "音感仪", "长刃", "拳套", "枪"]:
        img = screenshot()
        img = img[int(130 * height_ratio):int(180 * height_ratio), int(700 * width_ratio):int(1100 * width_ratio)]
        res = everyday_ocr(img)
        if type(res) == int:
            challenge1()
            control.tap(win32con.VK_F2)
            time.sleep(0.5)
            random_click(77, 315 + tempy)  # 周期挑战
            challenge3(60)
        else:
            challenge3(180)
    elif config.TargetChallenge != "无":
        random_click(400, 500)  # 无音清剿
        img = screenshot()
        img = img[int(130 * height_ratio):int(180 * height_ratio), int(700 * width_ratio):int(1100 * width_ratio)]
        res = everyday_ocr(img)
        if type(res) == int:
            challenge2()
        else:
            challenge3(180)
    else:
        challenge3(180)
    control.tap(win32con.VK_F2)
    time.sleep(0.8)
    img = screenshot()
    img = img[int(140 * height_ratio):int(830 * height_ratio), int(350 * width_ratio):int(1810 * width_ratio)]
    res = everyday_ocr(img)
    count = 0
    num = 0
    for i in range(len(res)):
        if res[i] == "领取":
            count += res[i + 1]
            num += 1
        if count >= 100:
            for a in range(num):
                random_click(1670, 195)
            random_click(1720, 920)
            time.sleep(0.3)
            random_click(960, 540)
            time.sleep(0.4)
            control.esc()
            info.echoNum += 1
            logger("每日任务已经做完", "绿")
            time.sleep(2)
            return

def template_pic(target):
    img = screenshot(1)
    temp = temp = cv2.imdecode(np.fromfile(root_path + "\\template\\" + target + ".png", dtype=np.uint8), 1)
    temp = cv2.resize(temp, (int(temp.shape[1] * width_ratio), int(temp.shape[0] * height_ratio)), interpolation=cv2.INTER_AREA)
    h, w = temp.shape[:2]
    res = cv2.matchTemplate(img, temp, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.6)
    for pt in zip(*loc[::-1]):
        if int(pt[0] + 0.5 * w) > 100 * width_ratio:
            return int(pt[0] + 0.5 * w), int(pt[1] + 0.5 * h)
    return None
