
from . import *

pages = []


def automatically_placed_in():
    """
    自动放入
    :param positions:
    :return:
    """
    control.activate()
    random_click(1300, 983)
    time.sleep(0.3)
    return True


automatically_placed_in_page = Page(
    name="批量融合",
    targetTexts=[
        TextMatch(
            name="批量融合",
            text="批量融合",
        ),
    ],
    action=automatically_placed_in,
)

pages.append(automatically_placed_in_page)


def end_echoes():
    """
    结束
    :param positions:
    :return:
    """
    for i in range(3):
        control.esc()
        time.sleep(1)
    return True


end_echoes_page = Page(
    name="合成结束",
    targetTexts=[
        TextMatch(
            name="请至少",
            text="请至少",
        ),
    ],
    action=end_echoes,
)

pages.append(end_echoes_page)


def all():
    control.activate()
    random_click(550, 990)
    random_click(1510, 990)
    return True


all_page = Page(
    name="全选",
    targetTexts=[
        TextMatch(
            name="全选",
            text="全选",
        ),
    ],
    action=all,
)

pages.append(all_page)


def tips():
    """
    提示
    :param positions:
    :return:
    """
    control.activate()
    time.sleep(0.3)
    random_click(850, 598)
    random_click(1285, 680)
    time.sleep(0.3)
    return True


tips_page = Page(
    name="提示",
    targetTexts=[
        TextMatch(
            name="登录",
            text="登录",
        ),
    ],
    action=tips,
)

pages.append(tips_page)


def get_echoes():
    """
    获取回音
    :param positions:
    :return:
    """
    control.activate()
    time.sleep(1)
    echo_synthesis()
    time.sleep(1)
    return True


get_echoes_page = Page(
    name="获得声骸",
    targetTexts=[
        TextMatch(
            name="获得声骸",
            text="获得声骸",
        ),
    ],
    action=get_echoes,
)

pages.append(get_echoes_page)