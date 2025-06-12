from schema import Task
from .pages.general import pages as general_pages
from .conditional_actions.boss import conditional_actions, echo_lock4c_task_page
from .pages.synthesis import pages as synthesis_pages

# 合并所有页面
boss_task = Task()
boss_task.pages = general_pages  # 合并通用页面和boss页面
boss_task.conditionalActions = conditional_actions  # 添加boss专属条件动作

synthesis_task = Task()
synthesis_task.pages = synthesis_pages  # 合成页面

echo_lock4c_task = Task()
echo_lock4c_task.conditionalActions = echo_lock4c_task_page  # 4C锁定
