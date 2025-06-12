from pydantic import BaseModel, Field
import yaml
import os
from typing import Dict, List


class Config(BaseModel):
    MaxIdleTime: int = Field(2, title="最大空闲时间")
    TargetBoss: list[str] = Field([], title="目标Boss")
    TargetChallenge: str = Field("", title="目标副本")
    FightTactics: list[str] = Field([], title="战斗策略")
    RoleIndex: str = Field("123", title="角色索引")
    IsWei: bool = Field(True, title="是否维")
    TwoWei: int = Field(1, title="是否二命维")
    FightTacticsUlt: list[str] = Field([], title="大招释放成功时的技能释放顺序")
    DungeonWeeklyBossLevel: int = Field(80, title="无妄者等级")
    EchoLockConfig: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict, title="锁定声骸配置")
    AppPath: str = Field("", title="游戏路径")
    Automatic: bool = Field(True, title="自动启动")


# 判断是否存在配置文件
if os.path.exists("config.yaml"):
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = Config(**yaml.safe_load(f))
else:
    config = Config()
# 加载声骸锁定配置文件
if os.path.exists("echo_config.yaml"):
    with open("echo_config.yaml", "r", encoding="utf-8") as f:
        config.EchoLockConfig = yaml.safe_load(f)
