import os
import time
from datetime import datetime
from multiprocessing import Queue

from pydantic import BaseModel, Field

from constant import root_path
from config import config


class StatusInfo(BaseModel):
    ruleIndex: int = Field(0, title="角色索引")
    bossIndex: int = Field(-1, title="boss索引")
    fightCount: int = Field(0, title="战斗次数")
    absorptionCount: int = Field(0, title="吸收次数")
    lastFightTime: datetime = Field(datetime.now(), title="最近检测到战斗时间")
    startTime: datetime = Field(datetime.now(), title="开始时间")
    bossName: str = Field("", title="当前BOSS名称")
    waitBoss: bool = Field(True, title="是否等待Boss")
    waveplate: int = Field(-1, title="体力")
    waveplates: int = Field(0, title="消耗体力")
    echoNum: int = Field(0, title="声骸数量")
    echoLockNum: int = Field(0, title="锁定声骸数量")
    taoNums: dict = Field({}, title="各套个数")
    everyday: bool = Field(False, title="每日")
    fighttype: str = Field("", title="战斗类型")
    overflag: bool = Field(False, title="结束标志")
    q: Queue = Field(None)


info = StatusInfo()
lastMsg = ""
tao = list(config.EchoLockConfig.keys())
for t in tao:
    info.taoNums[t] = 0


def logger(msg: str, color: str = '', flag=True):
    global lastMsg
    if "当前声骸为" in msg:
        content = f"{datetime.now().strftime('%m-%d %H:%M:%S')} "
    else:
        content = (
            f"{datetime.now().strftime('%m-%d %H:%M:%S')} "
            f"战斗次数: {info.fightCount} "
            f"吸收次数: {info.absorptionCount} "
        )

    if info.echoLockNum != 0:
        content += f"锁定个数: {info.echoLockNum} "
    content += f"{msg}"
    start = "\n" if lastMsg != msg else "\r"
    content1 = start + content
    content2 = content + color
    if info.q:
        info.q.put(content2)
        time.sleep(0.1)
    else:
        print(content2)
    lastMsg = msg
    if flag:
        with open(os.path.join(root_path, "mc_log.txt"), "a", encoding="utf-8") as log_file:
            log_file.write(content1)
