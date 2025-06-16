import time

from . import *

pages = []


# 击败 战斗状态
def fight_action(positions: dict[str, Position]) -> bool:
    info.fightCount += 1
    info.ruleIndex = 0
    info.overflag = False
    info.fighttype = "boss"
    release_skills()
    if info.bossName not in ["无妄者", "角", "赫卡忒", "芙露德莉斯"]:
        absorption_action()
    info.lastFightTime = datetime.now()
    return True


fight_page = Page(
    name="战斗",
    targetTexts=[
        TextMatch(
            name="击败",
            text=template(r"(击败|对战|泰缇斯系统|梦|叹息古龙)"),  # 使用正则表达式匹配 支持击败和对战
        ),
    ],
    action=fight_action,
)
pages.append(fight_page)  # 战斗

# 离开
def leave_action(positions: dict[str, Position]) -> bool:
    absorption_action()
    time.sleep(0.3)
    control.esc()
    time.sleep(0.5)
    control.activate()
    # 下个boss和现在一样 并且背包没满
    a = info.bossName == config.TargetBoss[info.bossIndex % len(config.TargetBoss)] and info.echoNum < 3000
    # 请体力 且 清日常体力小于240
    b = config.TargetChallenge == "无音区" and info.waveplates < 240 and info.waveplate >= 60
    c = config.TargetChallenge in ["角色", "武器", "贝币", "迅刀", "音感仪", "长刃", "拳套", "枪"] and info.waveplates < 240 and info.waveplate >= 40
    d = int(86400 - (time.time() - datetime(2025, 3, 3, 4, 0, 0).timestamp()) % 86400)
    if d < 10:
        time.sleep(d + 5)
    if info.everyday and a and not b and not c:
        random_click(1300, 680)
        random_click(1300, 680)
        time.sleep(1)

        info.bossIndex += 1
        info.overflag = False
        info.waitBoss = True
        logger(f"当前目标boss: {info.bossName}")
        wait_home()
        info.lastFightTime = datetime.now()  # 重置最近检测到战斗时间
    else:
        random_click(620, 680)
        random_click(620, 680)
        time.sleep(2)
        wait_home()
    return True


leave_page = Page(
    name="离开",
    targetTexts=[
        TextMatch(
            name="离开",
            text=template(r"(离开|领取奖励)"),
        ),
    ],
    excludeTexts=[
        TextMatch(
            name="确认",
            text="确认",
        ),
    ],
    action=leave_action,
)
pages.append(leave_page)  # 离开


def login_action(positions: dict[str, Position]) -> bool:
    def find_all_indices(s, target):
        return [j for j, char in enumerate(s) if char == target]
    control.activate()
    config.MaxIdleTime = 19
    for i in range(3):
        random_click(960, 1010)
        time.sleep(0.4)
    if os.path.exists(os.path.join(root_path, "mc_log.txt")):
        with open(os.path.join(root_path, "mc_log.txt"), "r", encoding="utf-8") as file:
            lines = file.readlines()
            i = -3
            while i > -15:
                i -= 1
                last_line = lines[i]
                if int(last_line[last_line.index("战斗次数") + 5:last_line.index("吸收次数") - 1]) != 0:
                    if info.fightCount == 0:
                        indexs = find_all_indices(last_line, " ")
                        info.fightCount = int(last_line[indexs[2] + 1:indexs[3]])
                        if "锁定个数" in last_line:
                            info.echoLockNum = int(last_line[indexs[6] + 1:indexs[7]])
                        info.absorptionCount = int(last_line[indexs[4] + 1:indexs[5]])
                    if "当前" in last_line:
                        if "当前目标boss" in last_line:
                            info.bossName = lines[i][lines[i].index("当前目标boss") + 10:len(lines[i]) - 1]
                        elif "战斗画面" in last_line:
                            info.bossName = lines[i - 1][lines[i - 1].index("当前目标boss") + 10:len(lines[i - 1]) - 1]
                        info.lastFightTime = datetime.now()  # 重置最近检测到战斗时间
                        return True
login_page = Page(
    name="登录",
    targetTexts=[
        TextMatch(
            name="点击连接",
            text="点击连接",
        ),
    ],
    action=login_action,
)
pages.append(login_page)  # 登录


def hot_action(positions: dict[str, Position]) -> bool:
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    psutil.Process(pid).terminate()
    return True
hot_page = Page(
    name="热更",
    targetTexts=[
        TextMatch(
            name="退出",
            text=template(r"(退出|公告)"),
        ),
    ],
    action=hot_action,
)
pages.append(hot_page)  # 热更

def update_action(positions: dict[str, Position]) -> bool:
    while "" in find_text(100, 950, 330, 1000, "着色器"):
        pass
    return True
update_page = Page(
    name="着色器",
    targetTexts=[
        TextMatch(
            name="更新",
            text="着色器",
        ),
    ],
    action=update_action,
)
pages.append(update_page)  # 热更