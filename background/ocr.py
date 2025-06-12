import os
import threading
from multiprocessing import current_process

import paddle

from paddleocr import PaddleOCR
import numpy as np
from status import logger
from constant import root_path
from schema import OcrResult, Position
import logging

def init():
    if paddle.version.cuda() != "False":
        return PaddleOCR(use_angle_cls=False, use_gpu=True, lang="ch", show_log=False,
                           cls_model_dir=root_path + "\\.paddleocr\\whl\\cls\\ch_ppocr_mobile_v2.0_cls_infer",
                           det_model_dir=root_path + '\\.paddleocr\\whl\\det\\ch\\ch_PP-OCRv4_det_infer',
                           rec_model_dir=root_path + '\\.paddleocr\\whl\\rec\\ch\\ch_PP-OCRv4_rec_infer')

    else:
        os.environ['FLAGS_use_mkldnn'] = '1'  # CPU启用mkldnn加速
        return PaddleOCR(use_angle_cls=False, use_gpu=False, lang="ch", show_log=False, cpu_threads=os.cpu_count(),
                           cls_model_dir=root_path + "\\.paddleocr\\whl\\cls\\ch_ppocr_mobile_v2.0_cls_infer",
                           det_model_dir=root_path + '\\.paddleocr\\whl\\det\\ch\\ch_PP-OCRv4_det_infer',
                           rec_model_dir=root_path + '\\.paddleocr\\whl\\rec\\ch\\ch_PP-OCRv4_rec_infer')


def ocr(img: np.ndarray) -> list[OcrResult]:
    ocr_mutex.acquire()
    try:
        results = ocrIns.ocr(img)[0]
        if not results:
            return []
        res = []
        for result in results:
            text = result[1][0]
            position = result[0]
            x1, y1, x2, y2 = position[0][0], position[0][1], position[2][0], position[2][1]
            position = Position(x1=x1, y1=y1, x2=x2, y2=y2)
            confidence = result[1][1]
            res.append(OcrResult(text=text, position=position, confidence=confidence))
        return res
    except Exception as e:
        logger(str(e) + " ocr", "红")
    finally:
        ocr_mutex.release()


def everyday_ocr(img: np.ndarray):
    results = ocrIns.ocr(img)[0]
    res = []
    for i in range(len(results)):
        temp = results[i][1][0]
        if "+" in temp and "/240" not in temp:
            num = int(temp[1:])
            task = results[i + 1][1][0]
            if i + 2 == len(results):
                task = "前往"
            elif results[i + 2][1][0] == "领取":
                task = "领取"
            res.append(task)
            res.append(num)
        elif "/240" in temp or "/3000" in temp:
            return int(temp[:temp.index("/")])
        elif "/3" in temp and "今日剩余双倍奖励次数" in temp:
            return int(temp[-3:-2])
        elif "数据融合次数" in temp:
            return int(temp[7:])
    return res


if current_process().name in ["boss", "合成", "锁定"]:
    ocr_mutex = threading.Lock()
    logging.disable(logging.WARNING)  # 关闭WARNING日志的打印
    ocrIns = init()
