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
from everyday import everyday


index = 0  # 实际索引
keyflag = False  # 梦魇复刷往前跑
mutex = threading.Lock()
die = []
pool = concurrent.futures.ThreadPoolExecutor(max_workers=8)
fightDict = {
    "a": control.fight_click,
    "s": control.space,
    "l": control.shift,
}

def get_file_count(folder_path):
    file_list = glob.glob(folder_path + '/*')
    return len(file_list)


def release_skills():
    global index, keyflag
    control.activate()
    if keyflag and info.bossName in ["梦魇无冠者", "梦魇燎照之骑"]:
        control.key_press("w")
        time.sleep(0.2)
        control.shift()
        time.sleep(0.2)
        control.shift()
        time.sleep(0.2)
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
    # while True:
    #     img = screenshot()
    #     if (img[int(43 * height_ratio), int(1740 * width_ratio)] > [254, 254, 254]).all():  # 没开大招
    #         break
    for tactic in tactics:  # 遍历对应角色的战斗策略
        if info.overflag:
            return True  # 提前结束
        #  判断 flag 状态，若为真，则执行一些操作
        control.activate(False)
        control.tap(index)
        control.mouse_middle()
        try:
            wait_time = float(tactic)
            time.sleep(wait_time)
        except:
            if tactic in ["e", "t", "q"]:
                if info.overflag:
                    return True  # 提前结束
                if tactic in die:
                    return False
                control.tap(tactic)
                pool.submit(over_fight)
            elif tactic == "r" and flag:  # 大招处理
                if info.overflag:
                    return True  # 提前结束
                control.tap(tactic)
                time.sleep(0.1)
                img = screenshot()
                if (img[int(43 * height_ratio), int(1740 * width_ratio)] < [255, 255, 255]).all():  # 等待大招时间
                    logger("检测到大招释放，等待大招动画", flag=False)
                    while True:
                        img = screenshot()
                        if (img[int(43 * height_ratio), int(1740 * width_ratio)] > [254, 254, 254]).all():  # 等待大招时间
                            pool.submit(over_fight)
                            release_skills_after_ult()
                            break
            elif tactic in fightDict:
                if info.overflag:
                    return True  # 提前结束
                fightDict.get(tactic)()
                pool.submit(over_fight)
            elif tactic == "z":
                if info.overflag:
                    return True  # 提前结束
                control.zhongji()
                pool.submit(over_fight)
            else:
                continuous_tap_time = float(tactic[tactic.find('(') + 1:tactic.find(')')])
                tap_start_time = time.time()
                while time.time() - tap_start_time <= continuous_tap_time:
                    if info.overflag:
                        return True
                    if tactic[0] == "a":
                        control.fight_click()
                    else:
                        control.tap(tactic[0])
                    pool.submit(over_fight)
    return False  # 所有策略执行完后返回


def forward(cxk: float, f: str = "w"):
    control.key_press(f)
    time.sleep(cxk)
    control.key_release(f)


bossDict = {
    "鸣钟之龟": 4,
    "朔雷之鳞": 1,
    "燎照之骑": 3,
    "无常凶鹭": 4,
    "辉萤军势": 3,
    "飞廉之猩": 5,
    "哀声鸷": 5,
    "无冠者": 4,
    "聚械机偶": 7,
    "云闪之鳞": 3,
    "无归的谬误": 6,
    "罗蕾莱": 5,
    "异构武装": 4,
    "叹息古龙": 5,
    "梦魇飞廉之猩": 0,
    "梦魇无常凶鹭": 5,
    "梦魇云闪之鳞": 3,
    "梦魇朔雷之鳞": 3,
    "梦魇无冠者": 3,
    "梦魇燎照之骑": 4,
    "梦魇哀声鸷": 5,
    "梦魇辉萤军势": 2,
    "梦魇凯尔匹": 6,
    "荣耀狮像": 4
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
    if not findBoss:
        control.esc()
        logger("未找到目标boss", "红")
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
    move_boss()
    info.lastFightTime = datetime.now()  # 重置最近检测到战斗时间


def move_boss(flag=True):
    if info.bossName != "梦魇辉萤军势":
        control.mouse_middle()
    if info.bossName == "罗蕾莱" and not find_text(20, 265, 320, 310, "击败") and flag:
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
            time.sleep(0.5)
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
            forward(1.3)
    if info.bossName == "无冠者":
        control.tap("f")
        time.sleep(1)


def transfer_to_dreamless():
    random_click(77, 315 + tempy)  # 周期挑战
    random_click(77, 315 + tempy)  # 周期挑战
    time.sleep(0.3)
    random_click(400, 620)  # 战歌重奏
    time.sleep(0.3)
    if info.bossName == "无妄者":
        random_click(1720, 470)  # 无妄者
    elif info.bossName == "角":
        random_click(1720, 630)  # 角
    elif info.bossName == "赫卡忒":
        random_click(1720, 780)  # 赫卡忒
    elif info.bossName == "芙露德莉斯":
        random_click(1720, 930)  # 芙露德莉斯
        # time.sleep(0.3)
        # if find_text(1230, 640, 1370, 700, "确认"):
        #     random_click(1300, 680)
        #     time.sleep(0.5)
        #     return True
    time.sleep(1)
    random_click(1600, 1000)  # 快速旅行
    random_click(1600, 1000)  # 快速旅行
    time.sleep(2)
    wait_home()
    logger("传送完成", flag=False)
    if info.bossName != "芙露德莉斯":
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
        if config.TargetChallenge:
            info.everyday = False
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
        img = screenshot()
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
            if (img[int(43 * height_ratio), int(1740 * width_ratio)] > [254, 254, 254]).all(): #  角色图标
                if (img[int(63 * height_ratio), int(679 * width_ratio)] < [255, 255, 255]).all(): # boss没有血条
                    info.fighttype = ""
                    info.overflag = True
                    t = None
                if (img[int(289 * height_ratio), int(1758 * width_ratio)] < [150, 150, 150]).all() and "1" not in die: # 1号位死
                    die.append("1")
                    logger("1号位死了", "红")
                elif (img[int(421 * height_ratio), int(1758 * width_ratio)] < [150, 150, 150]).all() and "2" not in die: # 2号位死
                    die.append("2")
                    logger("2号位死了", "红")
                elif (img[int(553 * height_ratio), int(1758 * width_ratio)] < [150, 150, 150]).all() and "3" not in die: # 3号位死
                    die.append("3")
                    logger("3号位死了", "红")
            if info.bossName == "赫卡忒" and ((img[int(43 * height_ratio), int(1740 * width_ratio)] < [5, 5, 5]).all() and (img[int(61 * height_ratio), int(678 * width_ratio)] < [5, 5, 5]).all()):
                time.sleep(1)
        if "梦魇" in info.bossName and t:
            if time.time() - t > 5 and (img[int(43 * height_ratio), int(1740 * width_ratio)] > [254, 254, 254]).all() and (img[int(63 * height_ratio), int(1244 * width_ratio)] > [200, 200, 200]).any():
                logger("超出场地", "红")
                info.fighttype = ""
                info.overflag = True
                t = None
                control.tap("1")
                repeat_boss()
            else:
                t = None

        if "辉萤军势" in info.bossName or info.bossName in ["异构武装"]:
            img2 = img[int(240 * height_ratio):int(320 * height_ratio), int(830 * width_ratio):int(1075 * width_ratio)]
            res2 = ocr(img2)
            if res2 and res2[0].text == "交替点击进行挣脱":
                b = time.time()
                while time.time() - b < 2:
                    control.tap("a")
                    control.tap("d")
        if info.fighttype == "每日":
            img3 = img[int(240 * height_ratio):int(320 * height_ratio), int(830 * width_ratio):int(1075 * width_ratio)]  # 挑战成功
            res3 = ocr(img3)
            if res3 and res3[0].text in ["挑战成功", "挑战达成"]:
                info.fighttype = ""
                info.overflag = True

    except Exception as e:
        logger(str(e) + " over_fight")
        pass
    finally:
        mutex.release()


def repeat_boss():
    control.tap("m")
    time.sleep(1)
    random_click(960, 540)  # 中心
    random_click(1750, 1000)  # 快速旅行
    random_click(1750, 1000)  # 快速旅行
    time.sleep(2)
    wait_home()
    logger("传送完成", flag=False)
    cv2.imwrite(f"../temp/{info.fightCount}.png", screenshot(1))
    move_boss(False)
    if "梦魇" not in info.bossName:
        if info.bossName in ["罗蕾莱", "异构武装"]:
            forward(1, "a")
        elif info.bossName in ["叹息古龙", "无归的谬误"]:
            forward(1, "d")
        while True:
            forward(0.7)
            img = screenshot()
            img = img[int(420 * height_ratio):int(630 * height_ratio), int(1335 * width_ratio):int(1470 * width_ratio)]
            result = ocr(img)
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
                elif len(result) == 1:
                    control.tap("f")
                    continue
                control.scroll(1)
                control.tap("f")
                time.sleep(1)
                break
        time.sleep(1)
        if info.bossName == "罗蕾莱":
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
    global recovery, tempy, keyflag
    keyflag = False
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

    if info.bossName == config.TargetBoss[info.bossIndex % len(config.TargetBoss)] and "梦魇" not in info.bossName and info.bossName not in ["无妄者", "角", "赫卡忒", "芙露德莉斯"]:
        info.waitBoss = True
        logger(f"当前目标boss: {info.bossName}")
        repeat_boss()
        info.lastFightTime = datetime.now()  # 重置最近检测到战斗时间
        return

    control.tap(win32con.VK_F2)
    time.sleep(0.5)
    if info.bossIndex == -1:
        if not find_pic(46, 411, 110, 475, "强者之路.png", 0.6):
            tempy = 140
    if config.TargetChallenge:
        a = 0
        if find_pic(55, 45, 95, 96, "每日.png", 0.6):
            if config.TargetChallenge == "无音区" and info.waveplate >= 180:
                a = 180
            elif config.TargetChallenge in ["角色", "武器", "贝币", "迅刀", "音感仪", "长刃", "拳套", "枪"] and info.waveplate >= 200:
                a = 200
            if a:
                from challenge import challenge, reset
                logger("体力到达额定上限 进行第一次自动清体力", "蓝")
                challenge(a, tempy)
                reset()
                logger("尝试进行自动每日任务", "蓝")
                everyday()
        else:
            info.everyday = True
            if config.TargetChallenge == "无音区":
                info.waveplates = 180
                a = 60
            else:
                info.waveplates = 200
                a = 40
            if info.waveplate + int(86400 - (time.time() - datetime(2025, 3, 3, 4, 0, 0).timestamp()) % 86400) // 360 >= 240:
                if info.waveplate >= a:
                    from challenge import challenge, reset
                    logger("进行第二次自动清体力", "蓝")
                    challenge(a, tempy)
                    reset()
            else:
                info.waveplates = 240
    else:
        info.everyday = True

    info.waitBoss = True
    info.bossIndex += 1
    info.bossName = config.TargetBoss[info.bossIndex % len(config.TargetBoss)]
    logger(f"当前目标boss: {info.bossName}")
    if info.bossName in ["无妄者", "角", "赫卡忒", "芙露德莉斯"]:
        return transfer_to_dreamless()
    else:
        return transfer_to_boss()


def jinru(flag=True, num=0):
    # 进入
    control.tap("f")
    control.tap("f")
    if flag:
        if info.bossName == "芙露德莉斯":
            time.sleep(5)
        # 推荐等级
        time.sleep(1.7)
        y = ((config.DungeonWeeklyBossLevel - 40) / 10) * 85 + 197
        random_click(311, y)  # 推荐等级
        random_click(311, y)
    else:
        time.sleep(2.3)
        if num < 5:
            y = 190 + 110 * num
            time.sleep(0.5)
            control.click()
            time.sleep(1)
            control.tap("f")
            time.sleep(3)
            random_click(970, 960)
            time.sleep(1.5)
            random_click(300, y)
            time.sleep(0.3)
        else:
            time.sleep(5)
    random_click(1720, 980)  # 单人挑战
    if info.waveplate < 60:
        time.sleep(0.5)
        random_click(1250, 680)  # 结晶波片不足
    time.sleep(1)
    random_click(1650, 990)  # 开启挑战
    time.sleep(1)
    wait_home()


def screenshot(flag=0) -> np.ndarray | None:
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


def turn_forward(f):
    control.key_press(f)
    forward(0.02, "w")
    control.key_release(f)
    control.mouse_middle()
    time.sleep(0.4)

def absorption_action():
    global die
    a = int(86400 - (time.time() - datetime(2025, 3, 3, 4, 0, 0).timestamp()) % 86400)
    if a < 20:
        time.sleep(a + 5)
    while True:
        img = screenshot()
        if (img[int(43 * height_ratio), int(1740 * width_ratio)] > [254, 254, 254]).all():  # 角色图标
            break
    control.tap("1")
    control.mouse_middle()
    if absorption_and_receive_rewards():
        if die:
            revive()
        return
    if config.IsWei:
        control.tap("e")
    control.shift()
    time.sleep(1)
    if absorption_and_receive_rewards():
        if die:
            revive()
        return
    if info.bossName in ["梦魇哀声鸷"]:
        count = 3
    else:
        count = 7
    for _ in range(count):
        forward(0.7)
        if absorption_and_receive_rewards():
            if die:
                revive()
            return
    logger("未掉落声骸", "红")
    if die:
        revive()


def absorption_and_receive_rewards() -> bool:
    img = screenshot()
    img = img[int(420 * height_ratio):int(630 * height_ratio), int(1335 * width_ratio):int(1470 * width_ratio)]
    result = ocr(img)
    if result:
        time.sleep(0.1)
        img = screenshot()
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


def is_echo_main_status_valid(this_echo_set, this_echo_cost, this_echo_main_status, echo_lock_config):
    if this_echo_set in echo_lock_config:
        if this_echo_cost in echo_lock_config[this_echo_set]:
            return this_echo_main_status in echo_lock_config[this_echo_set][this_echo_cost]
    return False


def check_echo_cost(image, x1, y1, x2, y2):
    image = image[int(y1 * height_ratio):int(y2 * height_ratio), int(x1 * width_ratio):int(x2 * width_ratio)]
    res = ocr(image)[0].text
    if "56" in res:
        return "1"
    elif res == "20":
        return "3"
    elif res == "30":
        return "4"
    else:
        return "??"


def check_echo_main_status(image, x1, y1, x2, y2):
    try:
        image = image[int(y1 * height_ratio):int(y2 * height_ratio), int(x1 * width_ratio):int(x2 * width_ratio)]
        res = ocr(image)[0].text
        if res:
            if "灭" in res:
                res = "湮灭伤害加成"
            elif "冷" in res:
                res = "冷凝伤害加成"
            return res
        else:
            return "??"
    except Exception as e:
        logger("识别主属性失败" + str(e), "红")
        return "??"

def check_echo_set(image, x1, y1, x2, y2):
    try:
        image = image[int(y1 * height_ratio):int(y2 * height_ratio), int(x1 * width_ratio):int(x2 * width_ratio)]
        res = ocr(image)
        for i in range(len(res)):
            if res[i].text == "合鸣效果":
                if "幽夜" in res[i + 1].text:
                    return "幽夜隐匿之帷"
                if "之" in res[i + 1].text:
                    return res[i + 1].text[:6]
                else:
                    return res[i + 1].text[:4]
        return "??"
    except Exception as e:
        logger("识别套装失败" + str(e), "红")
        return "??"

def check_echo_set2(image, flag, tz):
    try:
        image = cv2.resize(image, (1920, 1080), interpolation=cv2.INTER_LINEAR)
        if flag == 1:
            image = image[315:360, 830:870]
        else:
            image = image[310:345, 1430:1470]
        for i in tz:
            temp = cv2.imdecode(np.fromfile(f"{root_path}/template/{i}/1.png", dtype=np.uint8), 1)
            res = cv2.matchTemplate(image, temp, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.6)
            for pt in zip(*loc[::-1]):
                return i
    except Exception as e:
        logger("识别套装失败" + str(e), "红")
        return "??"

def check_echo_name(image, x1, y1, x2, y2):
    try:
        image = image[int(y1 * height_ratio):int(y2 * height_ratio), int(x1 * width_ratio):int(x2 * width_ratio)]
        res = ocr(image)
        if "灭" in res[0].text:
            return "湮灭棱镜"
        if "阿" in res[0].text:
            return "阿嗞嗞"
        if "咔" in res[0].text and "咔咔" not in res[0].text:
            return "咔嚓嚓"
        if "撤" in res[0].text:
            return "赦罪节使"
        if "碎" in res[0].text:
            return "碎獠猪"
        return res[0].text
    except Exception as e:
        logger("识别声骸名出错" + str(e), "红")
        return "??"


def lock_echo_synthesis(echo_cost, echo_main_status, echo_set):
    echo_cost = echo_cost + "COST"
    if is_echo_main_status_valid(echo_set, echo_cost, echo_main_status, config.EchoLockConfig):
        info.echoLockNum += 1
        control.tap("c")
        return True
    return False


temptao = None
def is_lock():
    global temptao
    image = screenshot()
    this_echo_name = check_echo_name(image, 705, 130, 940, 180)  # 识别声骸名
    if "梦" in this_echo_name:
        this_echo_name = "梦魇" + this_echo_name[2:]
    if this_echo_name == "梦魇·燎照之骑":
        this_echo_set = "熔山裂谷"
        this_echo_cost = "4"
    elif this_echo_name == "无常凶鹭":
        this_echo_set = "轻云出月"
        this_echo_cost = "4"
    elif this_echo_name == "角鳄":
        this_echo_set = check_echo_set2(image, 1, ["愿戴荣光之旅", "奔狼燎原之焰"])
        this_echo_cost = "3"
    elif this_echo_name in ["梦魇·凯尔匹", "共鸣回响·芙露德莉斯"]:
        this_echo_set = check_echo_set2(image, 1, ["流云逝尽之空", "愿戴荣光之旅"])
        this_echo_cost = "4"
    else:
        this_echo_set = check_echo_set(image, 705, 650, 900, 860)  # 识别套装属性
        this_echo_cost = check_echo_cost(image, 1165, 484, 1235, 520)  # 识别声骸COST1/3/4
    this_echo_main_status = check_echo_main_status(image, 780, 435, 1030, 475)  # 识别主词条
    log = "当前声骸为:" + this_echo_set + "套 " + this_echo_cost + "C " + this_echo_main_status + " " + this_echo_name
    if config.EchoLockConfig[this_echo_set]["PASS"] and this_echo_name in config.EchoLockConfig[this_echo_set]["PASS"]:
        logger(log + " 忽略", "红", flag=False)
    elif lock_echo_synthesis(this_echo_cost, this_echo_main_status, this_echo_set):  # 锁定声骸
        info.taoNums[this_echo_set] += 1
        logger(log + " 锁定", "绿", flag=False)
    else:
        logger(log + " 不锁定", "红", flag=False)
    temptao = this_echo_set
    control.esc()
    time.sleep(0.2)


def add_echo_list(img):
    def shibie(tz):
        tzlist = []
        # temp = cv2.imdecode(np.fromfile(f"{root_path}/template/{tz}/0.png", dtype=np.uint8), 1)
        # res = cv2.matchTemplate(img, temp, cv2.TM_CCOEFF_NORMED)
        # loc = np.where(res >= 0.7)
        # for pt in zip(*loc[::-1]):
        #     if not tzlist:
        #         tzlist.append((pt[0], pt[1] + 24))
        #         cv2.rectangle(img, pt, (pt[0] + 24, pt[1] + 24), (255, 255, 0), 1)
        #     else:
        #         for j in tzlist:
        #             if abs(j[0] - pt[0]) < 10 and abs(j[1] - pt[1] - 24) < 10:
        #                 break
        #             if j == tzlist[-1]:
        #                 tzlist.append((pt[0], pt[1] + 24))
        #                 cv2.rectangle(img, pt, (pt[0] + 24, pt[1] + 24), (255, 255, 0), 1)
        #
        # if not tzlist:
        #     return
        for j in range(2):
            # if len(config.EchoLockConfig[tz][f"{j * 2 + 1}COST"]) == 0:
            #     continue
            path = f"{root_path}/template/{tz}/{j * 2 + 1}C"
            size = get_file_count(path)
            for k in range(size):
                temp = cv2.imdecode(np.fromfile(f"{path}/{k}.png", dtype=np.uint8), 1)
                res = cv2.matchTemplate(img, temp, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= 0.8)
                for pt in zip(*loc[::-1]):
                    if not click_list:
                        for i in tzlist:
                            if abs(pt[0] - i[0] + 70) < 30 and abs(pt[1] - i[1]) < 30:
                                # echo_mutex.acquire()
                                click_list.append((pt[0] + 30, pt[1] + 30))
                                tzlist.remove(i)
                                # cv2.rectangle(img, pt, (pt[0] + 70, pt[1] + 70), (0, 255, 0), 1)
                                # echo_mutex.release()
                                if not tzlist:
                                    return
                        if not tzlist:
                            # echo_mutex.acquire()
                            click_list.append((pt[0] + 30, pt[1] + 30))
                            # cv2.rectangle(img, pt, (pt[0] + 70, pt[1] + 70), (0, 255, 0), 1)
                            # echo_mutex.release()
                    else:
                        for j in click_list:
                            if abs(j[0] - (pt[0] + 30)) < 30 and abs(j[1] - (pt[1] + 30)) < 30:
                                break
                            if j == click_list[-1]:
                                for i in tzlist:
                                    if abs(pt[0] - i[0] + 70) < 30 and abs(pt[1] - i[1]) < 30:
                                        # echo_mutex.acquire()
                                        click_list.append((pt[0] + 30, pt[1] + 30))
                                        tzlist.remove(i)
                                        # cv2.rectangle(img, pt, (pt[0] + 70, pt[1] + 70), (0, 255, 0), 1)
                                        # echo_mutex.release()
                                        if not tzlist:
                                            return
                                if not tzlist:
                                    # echo_mutex.acquire()
                                    click_list.append((pt[0] + 30, pt[1] + 30))
                                    # cv2.rectangle(img, pt, (pt[0] + 70, pt[1] + 70), (0, 255, 0), 1)
                                    # echo_mutex.release()

    logger("正在识别声骸...", "蓝", False)
    click_list = []
    # threads = []
    # echo_mutex = threading.Lock()
    tao = list(config.EchoLockConfig.keys())
    for i in tao:
        # if len(config.EchoLockConfig[i]["1COST"]) + len(config.EchoLockConfig[i]["3COST"]) == 0:
        #     continue
        shibie(i)
    #     thread = threading.Thread(target=shibie, args=(i,))
    #     thread.start()
    #     threads.append(thread)
    # for thread in threads:
    #     thread.join()

    click_list = sorted(click_list, key=lambda point: (point[1], point[0]))
    for i in range(len(click_list)):
        if i != 0 and abs(click_list[i][1] - click_list[i - 1][1] < 50):
            click_list[i] = (click_list[i][0], click_list[i - 1][1])
    click_list = sorted(click_list, key=lambda point: (point[1], point[0]))
    logger(f"识别结束 共{len(click_list)}个", "蓝", False)
    # cv2.namedWindow('Image', cv2.WINDOW_AUTOSIZE)
    # cv2.imshow("Image", img)
    # cv2.waitKey(0)
    return click_list


def echo_synthesis():
    control.activate()
    img = screenshot(1)
    img = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_LINEAR)
    res = ocr(img)
    if len(res) > 1 and "额外获得" in res[1].text:
        img = img[0:res[1].position.y1:, 0:1920]
        freegain = True
    else:
        freegain = False
    click_list = add_echo_list(img)
    for i in range(len(click_list)):
        click_x, click_y = click_list[i]
        random_click(click_x, click_y)  # 点开声骸
        is_lock()

    if freegain:
        random_click(res[1].position.x1, res[1].position.y1)
        random_click(res[1].position.x1, res[1].position.y1)
        for i in range(3):
            control.scroll(-15, int(res[1].position.x1 * width_ratio), int(res[1].position.y1 * height_ratio))
        time.sleep(1)

        img = screenshot(1)
        img = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_LINEAR)
        res = ocr(img)
        y = 0
        for i in res:
            if i.text == "额外获得":
                y = i.position.y2
                img = img[y:1080, 0:1920]
                break
        click_list = add_echo_list(img)
        for i in range(len(click_list)):
            click_x, click_y = click_list[i]
            random_click(click_x, click_y + y)  # 点开声骸
            is_lock()
    time.sleep(0.2)
    control.esc()

addy = 0
def echo_lock4c():
    global addy
    def switch(image):
        global addy
        while (image[111 + addy, 1219] > [150, 150, 150]).all():
            addy += 1
        addy -= 1

    control.activate()
    control.tap("b")
    time.sleep(1)
    random_click(75, 330)  # 声骸
    random_click(230, 988)  # 筛选
    random_click(1180, 900)  # 重置
    random_click(1180, 900)  # 重置
    random_click(1600, 760)  # 4C
    random_click(1560, 905)  # 确定
    time.sleep(0.5)
    random_click(370, 985)  # 排序
    random_click(385, 780)  # 获得时间
    random_click(730, 935)  # 空白
    y = 110
    img = screenshot(1)
    img1 = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)
    if (img1[993, 649] < [140, 140, 140]).any():
        random_click(640, 985)  # 反转
    thread = threading.Thread(target=switch, args=(img1,))
    while y <= 935:
        y += addy
        if y > 935:
            y = 935
        random_click(1219, y)
        random_click(1219, y)
        if y == 110:
            thread.start()
        lock_4c(False)
        thread.join()
        if y == 110:
            y += addy
    addy = 0

def lock_4c(flag):
    if flag and len(config.EchoLockConfig["沉日劫明"]["1COST"]) and len(config.EchoLockConfig["沉日劫明"]["3COST"]) and len(config.EchoLockConfig["轻云出月"]["1COST"]) and len(config.EchoLockConfig["轻云出月"]["3COST"])== 0:
        return
    for a in range(4):
        for b in range(6):
            random_click(275 + 165 * b, 210 + 200 * a)
            random_click(275 + 165 * b, 210 + 200 * a)
            img = screenshot(1)
            img1 = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)
            if (img1[328, 1811] < [150, 150, 150]).all():  # 没锁
                this_echo_name = check_echo_name(img, 1300, 120, 1600, 170)
                if "哀声" in this_echo_name:
                    this_echo_name = this_echo_name[:-1] + "鸷"
                if "梦" in this_echo_name:
                    this_echo_name = "梦魇" + this_echo_name[2:]
                if this_echo_name == "梦魇·燎照之骑":
                    this_echo_set = "熔山裂谷"
                elif this_echo_name == "无常凶鹭":
                    this_echo_set = "轻云出月"
                elif this_echo_name == "异构武装":
                    this_echo_set = "凌冽决断之心"
                elif this_echo_name in ["梦魇·凯尔匹", "共鸣回响·芙露德莉斯"]:
                    this_echo_set = check_echo_set2(img, 2, ["流云逝尽之空", "愿戴荣光之旅"])
                else:
                    this_echo_set = check_echo_set(img, 1300, 675, 1850, 865)  # 识别套装属性
                    if not this_echo_set:
                        logger("不是0级忽略", "红", False)
                        continue
                if not flag and len(config.EchoLockConfig[this_echo_set]["4COST"]) == 0:
                        logger(f"{this_echo_set}套不锁定忽略", "红", False)
                        continue
                this_echo_cost = check_echo_cost(img, 1750, 460, 1850, 510)  # 识别声骸COST1/3/4
                if this_echo_cost == "??":
                    logger(f"{this_echo_set}套不是0级忽略", "红", False)
                    continue
                if flag and this_echo_cost == "4":
                    return
                this_echo_main_status = check_echo_main_status(img, 1360, 410, 1600, 465)  # 识别主词条
                if lock_echo_synthesis(this_echo_cost, this_echo_main_status, this_echo_set):
                    logger(f"{this_echo_set}套 {this_echo_main_status} 锁定", "绿", False)
                else:
                    logger(f"{this_echo_set}套 {this_echo_main_status} 不锁定", "红", False)
            else:
                return


# def template_pic(target: str):
#     img = screenshot()
#     temp = cv2.imdecode(np.fromfile(root_path + "\\template\\" + target + ".png", dtype=np.uint8), 1)
#     temp = cv2.resize(temp, (int(temp.shape[1] * height_ratio), int(temp.shape[0] * width_ratio)), interpolation=cv2.INTER_AREA)
#     h, w = temp.shape[:2]
#     res = cv2.matchTemplate(img, temp, cv2.TM_CCOEFF)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#     return int(max_loc[0] + 0.5 * w), int(max_loc[1] + 0.5 * h)