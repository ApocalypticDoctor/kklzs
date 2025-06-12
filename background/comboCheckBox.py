from ctypes import windll

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QComboBox, QLineEdit, QListWidget, QCheckBox, QListWidgetItem, QApplication
from PyQt5.QtCore import pyqtSignal
import sys
import win32api

scale_factor = windll.shcore.GetScaleFactorForDevice(0) / 100  # 返回百分比形式的缩放因子

screen = (win32api.GetSystemMetrics(1) * scale_factor) / 1080
scale_factor = 1.25 / scale_factor * screen


class ComboCheckBox(QComboBox):
    signa = pyqtSignal(list)

    def __init__(self, frame, items):  # items==[str,str...]
        super(ComboCheckBox, self).__init__(frame)
        self.items = items
        font = QtGui.QFont()
        font.setFamily("Noto Sans SC")
        font.setPointSize(int(12 * scale_factor))
        self.setFont(font)
        self.row_num = len(self.items)
        self.Selectedrow_num = 0
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setFont(font)
        self.qLineEdit.setReadOnly(True)
        self.qLineEdit.setStyleSheet("background-color: rgb(240,240,240)")
        self.qListWidget = CustomListWidget(self)
        font = QtGui.QFont()
        font.setFamily("Noto Sans SC")
        font.setPointSize(int(15 * scale_factor))
        self.qListWidget.setFont(font)
        self.qListWidget.setStyleSheet("QListWidget{background-color: rgb(240,240,240)}")

        for i in range(0, self.row_num):
            self.addQCheckBox(i, font)
            self.qCheckBox[i].stateChanged.connect(self.show0)
        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)
        self.setLineEdit(self.qLineEdit)
        self.setMaxVisibleItems(10)  # 避免滑条的出现引起滑条偷吃标签的问题

        # 设置列表项交互
        self.qListWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.qListWidget.setSelectionMode(QListWidget.NoSelection)
        # 连接自定义信号
        self.qListWidget.itemClicked.connect(self.onItemClicked)
    # def All(self, zhuangtai):
    #     if zhuangtai == 2:
    #         for i in range(1, self.row_num):
    #             self.qCheckBox[i].setChecked(True)
    #     elif zhuangtai == 1:
    #         if self.Selectedrow_num == 0:
    #             self.qCheckBox[0].setCheckState(2)
    #     elif zhuangtai == 0:
    #         self.clear()

    def showPopup(self):
        self.qListWidget.verticalScrollBar().setValue(0)
        # 调用父类的方法来显示下拉框
        super(ComboCheckBox, self).showPopup()

    def hidePopup(self):
        self.qListWidget.verticalScrollBar().setValue(0)
        super(ComboCheckBox, self).hidePopup()

    def addQCheckBox(self, i, font):
        # 创建标准复选框
        checkbox = QCheckBox(self.items[i])
        checkbox.setFont(font)
        checkbox.setStyleSheet(
            "QCheckBox::indicator { width: " + str(int(20 * scale_factor)) +
            "px; height: " + str(int(20 * scale_factor)) + "px;}"
        )

        self.qCheckBox.append(checkbox)

        # 创建列表项并设置小部件
        qItem = QListWidgetItem(self.qListWidget)
        qItem.setSizeHint(checkbox.sizeHint())
        self.qListWidget.setItemWidget(qItem, checkbox)

    def Selectlist(self):
        Outputlist = []
        for i in range(0, self.row_num):
            if self.qCheckBox[i].isChecked() == True:
                Outputlist.append(self.qCheckBox[i].text())
        self.Selectedrow_num = len(Outputlist)
        return Outputlist

    def show0(self):
        show0 = ''
        Outputlist = self.Selectlist()
        self.signa.emit(Outputlist)

        # 禁用事件处理以防止闪烁
        self.blockSignals(True)
        self.qLineEdit.setReadOnly(False)
        self.qLineEdit.clear()
        for i in Outputlist:
            show0 += i + ','
        self.qLineEdit.setText(show0)
        self.qLineEdit.setReadOnly(True)
        self.blockSignals(False)

    def onItemClicked(self, item):
        row = self.qListWidget.row(item)
        if 0 <= row < len(self.qCheckBox):
            # 切换复选框状态
            checkbox = self.qCheckBox[row]
            checkbox.setChecked(not checkbox.isChecked())

            # 防止列表项被选中
            self.qListWidget.setCurrentItem(None)

            # 阻止默认的关闭行为
            return True
        return False

# 自定义列表控件，处理鼠标事件
class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)
        self.parent = parent

    def mousePressEvent(self, event):
        # 获取点击的项
        item = self.itemAt(event.pos())
        if item:
            # 通知父控件处理点击事件
            if self.parent.onItemClicked(item):
                # 事件已处理，不传播
                return

        # 其他情况执行默认行为
        super(CustomListWidget, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # 阻止默认的释放事件处理
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = ComboCheckBox(None, ["无妄者", "角", "赫卡忒", "鸣钟之龟", "朔雷之鳞", "燎照之骑", "无常凶鹭", "辉萤军势", "飞廉之猩", "哀声鸷", "无冠者", "聚械机偶", "云闪之鳞", "无归的谬误", "罗蕾莱", "异构武装", "叹息古龙", "梦魇飞廉之猩", "梦魇无常凶鹭", "梦魇云闪之鳞", "梦魇朔雷之鳞", "梦魇无冠者", "梦魇燎照之骑", "梦魇哀声鸷"])
    def solt11(x):
        print(x)
    mainWindow.signa.connect(solt11)
    mainWindow.show()
    sys.exit(app.exec_())
