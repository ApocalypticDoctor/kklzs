from schema import ConditionalAction
from . import *

conditional_actions = []
echo_lock4c_task_page = []


# 超过最大空闲时间
def judgment_idle_action() -> bool:
    config.MaxIdleTime = 3
    info.overflag = False
    return transfer()


def judgment_idle() -> bool:
    return (datetime.now() - info.lastFightTime).seconds > config.MaxIdleTime


judgment_idle_conditional_action = ConditionalAction(
    name="前往boss",
    condition=judgment_idle,
    action=judgment_idle_action,
)
conditional_actions.append(judgment_idle_conditional_action)


def lock_action():
    echo_lock4c()
    control.esc()
    time.sleep(1)
    return True


action_page = ConditionalAction(
    name="4C锁定",
    condition=judgment_idle,
    action=lock_action
)
echo_lock4c_task_page.append(action_page)
