from win32gui import FindWindow, SendMessage
from os import environ

from mouse_reset import mouse_reset
from multiprocessing import Event, Process, current_process, Queue
from task import boss_task, synthesis_task, echo_lock4c_task
from win32con import WM_CLOSE
from subprocess import Popen
from schema import Task
from utils import *

environ['KMP_DUPLICATE_LIB_OK'] = 'True'
taskEvent = Event()  # 用于停止任务线程
mouseResetEvent = Event()  # 用于停止鼠标重置线程
mouse_reset_thread = Process()
thread = Process()
queue = Queue()
flag = 1

def restart_app():
    global thread
    def enum_callback(hd, lparam):
        window_title = win32gui.GetWindowText(hd)
        if "UE4" in window_title:  # 假设弹窗标题包含"弹窗"
            lparam.append(hd)
    while flag:
        time.sleep(3)
        found = []
        win32gui.EnumWindows(enum_callback, found)
        if found:
            logger("UE4-Client Game已崩溃，尝试重启游戏", "红")
            SendMessage(found[0], WM_CLOSE, 0, 0)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            psutil.Process(pid).terminate()
            # 等待窗口关闭
            time.sleep(2)
        if flag and config.Automatic:
            if FindWindow("UnrealWindow", "鸣潮  "):
                if thread.exitcode == 0:
                    if thread.name in ["合成", "锁定"]:
                        logger("自动启动BOSS脚本", )
                        thread = Process(target=run, args=(boss_task, taskEvent, queue, True), name="boss")
                        thread.start()
                    elif thread.name == "boss":
                        logger("自动启动合成脚本")
                        thread = Process(target=run, args=(synthesis_task, taskEvent, queue), name="合成")
                        thread.start()
            else:
                logger("未找到游戏窗口", "红")
                taskEvent.clear()  # 清理BOSS脚本线程(防止多次重启线程占用-导致无法点击进入游戏)
                thread.terminate()
                Popen([config.AppPath], start_new_session=True)
                time.sleep(25)
                logger("自动启动BOSS脚本")
                thread = Process(target=run, args=(boss_task, taskEvent, queue, True), name="boss")
                thread.start()


def run(task: Task, e: Event, q: Queue, ok: bool = False):
    if ok:
        with open(os.path.join(root_path, "mc_log.txt"), "r", encoding="utf-8") as file:
            lines = file.readlines()
            last_line = lines[-2]
            if "锁定个数" in last_line:
                info.echoLockNum = int(last_line[last_line.index("锁定个数") + 5:last_line.rindex(" ")])
    info.q = q
    logger("任务进程开始运行")
    logger("请将鼠标移出游戏窗口, 避免干扰脚本运行")
    e.set()
    temp = []
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'].lower() == "Wuthering Waves.exe".lower():
            p = psutil.Process(proc.info['pid'])
            p.terminate()  # 尝试正常终止进程
    if current_process().name == "boss":
        # 热更 登录 战斗/离开 boss名
        temp = [(1230, 665, 1330, 720), (890, 980, 1030, 1040), (20, 265, 320, 310), (660, 10, 1260, 80)]
    elif current_process().name == "合成":
        # 合成 结束 全选 高级 获得
        temp = [(1330, 965, 1450, 1010), (830, 190, 1088, 235), (470, 970, 530, 1020), (870, 575, 1075, 615), (880, 150, 1040, 540)]
    try:
        while e.is_set():
            img = screenshot()
            res = []
            for i in temp:
                img1 = img[int(i[1] * height_ratio):int(i[3] * height_ratio), int(i[0] * width_ratio):int(i[2] * width_ratio)]
                res += ocr(img1)
            if task(img, res) == 1:
                e.clear()
                return
    except Exception as e:
        logger(str(e) + " run", "红")
        return


def over():
    global mouse_reset_thread, taskEvent, thread, flag
    mouse_reset_thread.terminate()
    thread.terminate()
    taskEvent.clear()
    flag = 0
    mouse_reset_thread.join()
    thread.join()
    logger("结束脚本")


def getPrint():
    while flag:
        try:
            output = queue.get(timeout=0.1)
            if output:
                print(output)
        except:
            pass


def start(name):
    global mouse_reset_thread, thread, taskEvent, queue, flag
    if os.path.exists(os.path.join(root_path, "mc_log.txt")):
        if int(time.time()) - int(os.path.getctime(os.path.join(root_path, "mc_log.txt"))) >= 86400:
            os.remove(os.path.join(root_path, "mc_log.txt"))

    mouse_reset_thread = Process(target=mouse_reset, args=(mouseResetEvent,), name="mouse_reset")
    mouse_reset_thread.start()
    flag = 1

    threading.Thread(target=restart_app).start()
    threading.Thread(target=getPrint).start()

    if name == "boss":
        logger("启动脚本")
        thread = Process(target=run, args=(boss_task, taskEvent, queue), name="boss")
        thread.start()
    elif name == "合成":
        logger("启动合成脚本")
        thread = Process(target=run, args=(synthesis_task, taskEvent, queue), name="合成")
        thread.start()
    elif name == "锁定":
        logger("启动锁定脚本")
        thread = Process(target=run, args=(echo_lock4c_task, taskEvent, queue), name="锁定")
        thread.start()
