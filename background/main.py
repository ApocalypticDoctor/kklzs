import ctypes
import multiprocessing
import os
import sys
import threading
import time

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from ui import Ui_MainWindow  # 界面
import img
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class LoginWindow(QMainWindow):
    # restore_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 设置该窗口是一个顶级窗口并去除窗口的框架和标题栏，使窗口无边框
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)
        # 设置窗口的背景为半透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置窗口在关闭时自动销毁（delete）
        self.setAttribute(Qt.WA_DeleteOnClose)
        # 设置其他窗口无法与之交互，直到该模态窗口关闭
        self.setWindowModality(Qt.ApplicationModal)

        self.m_bPressed = False
        self.m_point = QPoint()
        # self.restore_signal.connect(self._real_restore)
        # threading.Thread(target=self.restore).start()

    def restore(self):
        self.restore_signal.emit()  # 发送信号

    def _real_restore(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.m_bPressed = True
            self.m_point = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.m_bPressed:
            self.move(event.globalPos() - self.m_point)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.m_bPressed = False

    def closeEvent(self, event):
        self.ui.startOver()
        time.sleep(0.2)
        # 在关闭窗口时销毁（delete）该窗口
        self.deleteLater()
        # 调用父类的 closeEvent 方法，以确保窗口的正常关闭
        super().closeEvent(event)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, os.path.abspath(sys.argv[0]), None, 0)
        sys.exit(0)
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
