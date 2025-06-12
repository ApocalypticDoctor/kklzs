import time
import utils
from constant import height_ratio, width_ratio
from status import logger, info
from ocr import everyday_ocr
from control import control

addy = 0


def everyday():
    sum = 0
    num = 0

    img = utils.screenshot()
    img = img[int(140 * height_ratio):int(830 * height_ratio), int(350 * width_ratio):int(1810 * width_ratio)]
    res = everyday_ocr(img)

    for i in range(len(res)):
        if res[i] == "领取":
            sum += res[i + 1]
            num += 1
        if sum >= 100:
            for a in range(num):
                utils.random_click(1670, 195)
            utils.random_click(1720, 920)
            time.sleep(0.3)
            utils.random_click(960, 540)
            time.sleep(0.4)
            utils.is_lock()
            control.esc()
            info.echoNum += 1
            logger("每日任务已经做完", "绿")
            info.everyday = True
            time.sleep(0.5)
            return
