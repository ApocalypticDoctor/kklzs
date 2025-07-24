import random
import subprocess
import sys
import time

from PyQt5.QtCore import pyqtSignal
from pygame import mixer
import threading
from ctypes import windll
from datetime import datetime

import win32api
import win32con
import win32gui
import yaml
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFontDatabase, QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pynput import keyboard

from comboCheckBox import ComboCheckBox, scale_factor, screen
from config import config
from update import *
num = 0
def get_color(percentage):
    if percentage <= 0.6:
        red = 0
        green = 255
    else:
        red = 255
        green = int(255 * (1 - (percentage - 0.6) / 0.4))
    return "#{:02X}{:02X}{:02X}".format(red, green, 0)


class OutputRedirector:
    def __init__(self, text_browser, echoNum, over):
        self.text_browser = text_browser
        self.echoNum = echoNum
        self.over = over

    def write(self, text):
        global num
        # 去除尾部的换行符，避免 QTextBrowser 的自动换行
        text = text.rstrip('\n')
        if "屌毛" in text:
            self.over()
        if "当前个数为" in text:
            num = int(text[text.index("当前个数为") + 5:-1])
            self.echoNum.setText(f'<font color="{get_color(num / 3000)}">当前声骸<br/>个数: {num}</font>')
        if "吸收声骸" in text:
            num += 1
            self.echoNum.setText(f'<font color="{get_color(num / 3000)}">当前声骸<br/>个数: {num}</font>')
        if text:
            if text[-1] == "红":
                text = f'<font color="red">{text[:-1]}</font>'
            elif text[-1] == "绿":
                text = f'<font color="#00ff96">{text[:-1]}</font>'
            elif text[-1] == "蓝":
                text = f'<font color="#0096ff">{text[:-1]}</font>'
            else:
                text = f'<font color="white">{text}</font>'
            # 每次缓冲的文本达到一定长度时再更新 QTextBrowser
            try:
                QtCore.QMetaObject.invokeMethod(self.text_browser, "append", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, text))
                time.sleep(0.05)
                QtCore.QMetaObject.invokeMethod(self.text_browser.verticalScrollBar(), "setValue", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(int, self.text_browser.verticalScrollBar().maximum()))
            except:
                return

    def flush(self):
        pass  # 对于文件操作流，这个方法通常需要定义，但我们这里不需要它


class Ui_MainWindow(QtCore.QObject):
    signal = pyqtSignal(int)
    progress_signal = pyqtSignal(int)  # 新增信号，用于更新进度条
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.signal.connect(self.download_new)
        self.progress_signal.connect(self.update_progress_bar)
        self.name = ""
        self.temp1 = 0
        self.up = 0
        self.flag = False
        self.bossList = config.TargetBoss

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(int(1248 * screen), int(702 * screen))
        MainWindow.setWindowIcon(QIcon("icon.png"))
        QFontDatabase.addApplicationFont("ChikuziAMaru.ttf")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 右上角
        self.frame0 = QtWidgets.QFrame(self.centralwidget)
        self.frame0.setGeometry(QtCore.QRect(int(1158 * screen), int(20 * screen), int(70 * screen), int(30 * screen)))
        self.frame0.setAutoFillBackground(False)
        self.frame0.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame0.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame0.setObjectName("frame0")
        self.closeButton = QtWidgets.QPushButton(self.frame0)
        self.closeButton.setGeometry(QtCore.QRect(int(40 * screen), int(0 * screen), int(30 * screen), int(30 * screen)))
        self.closeButton.setStyleSheet("border-image: url(:/icon/close.png);border:none")
        self.closeButton.setText("")
        self.closeButton.setObjectName("closeButton")
        self.miniButton = QtWidgets.QPushButton(self.frame0)
        self.miniButton.setGeometry(QtCore.QRect(int(0 * screen), int(0 * screen), int(30 * screen), int(30 * screen)))
        self.miniButton.setStyleSheet("border-image: url(:/icon/mini.png);border:none")
        self.miniButton.setText("")
        self.miniButton.setObjectName("miniButton")

        # 左侧
        self.frame1 = QtWidgets.QFrame(self.centralwidget)
        self.frame1.setGeometry(QtCore.QRect(int(0 * screen), int(0 * screen), int(120 * screen), int(702 * screen)))
        self.frame1.setStyleSheet("#frame1{background-color:rgb(60,60,60);border-top-left-radius:40px;border-bottom-left-radius:40px}")
        self.frame1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame1.setObjectName("frame1")

        # 字体
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(16 * scale_factor))

        # 首页按钮
        self.homeButton = QtWidgets.QPushButton(self.frame1)
        self.homeButton.setEnabled(True)
        self.homeButton.setGeometry(QtCore.QRect(int(0 * screen), int(20 * screen), int(120 * screen), int(81 * screen)))
        self.homeButton.setFont(font)
        self.homeButton.setStyleSheet("QPushButton{background-color:transparent;color:rgb(240,240,240)}QPushButton:hover{color:rgb(248,195,1)}")
        self.homeButton.setObjectName("homeButton")

        # 基础配置按钮
        self.basicButton = QtWidgets.QPushButton(self.frame1)
        self.basicButton.setEnabled(True)
        self.basicButton.setGeometry(QtCore.QRect(int(0 * screen), int(110 * screen), int(120 * screen), int(81 * screen)))
        self.basicButton.setFont(font)
        self.basicButton.setStyleSheet("QPushButton{background-color:transparent;color:rgb(240,240,240)}QPushButton:hover{color:rgb(248,195,1)}")
        self.basicButton.setObjectName("basicButton")

        # 声骸配置按钮
        self.echoButton = QtWidgets.QPushButton(self.frame1)
        self.echoButton.setEnabled(True)
        self.echoButton.setGeometry(QtCore.QRect(int(0 * screen), int(200 * screen), int(120 * screen), int(81 * screen)))
        self.echoButton.setFont(font)
        self.echoButton.setStyleSheet("QPushButton{background-color:transparent;color:rgb(240,240,240)}QPushButton:hover{color:rgb(248,195,1)}")
        self.echoButton.setObjectName("echoButton")

        # 其他功能按钮
        self.otherButton = QtWidgets.QPushButton(self.frame1)
        self.otherButton.setEnabled(True)
        self.otherButton.setGeometry(QtCore.QRect(int(0 * screen), int(290 * screen), int(120 * screen), int(81 * screen)))
        self.otherButton.setFont(font)
        self.otherButton.setStyleSheet("QPushButton{background-color:transparent;color:rgb(240,240,240)}QPushButton:hover{color:rgb(248,195,1)}")
        self.otherButton.setObjectName("otherButton")

        # 日志按钮
        self.logButton = QtWidgets.QPushButton(self.frame1)
        self.logButton.setEnabled(True)
        self.logButton.setGeometry(QtCore.QRect(int(0 * screen), int(380 * screen), int(120 * screen), int(81 * screen)))
        self.logButton.setFont(font)
        self.logButton.setStyleSheet("QPushButton{background-color:transparent;color:rgb(240,240,240)}QPushButton:hover{color:rgb(248,195,1)}")
        self.logButton.setObjectName("logButton")

        # 用前必看按钮
        self.questionButton = QtWidgets.QPushButton(self.frame1)
        self.questionButton.setEnabled(True)
        self.questionButton.setGeometry(QtCore.QRect(int(0 * screen), int(615 * screen), int(120 * screen), int(81 * screen)))
        self.questionButton.setFont(font)
        self.questionButton.setStyleSheet("QPushButton{background-color:transparent;color:rgb(240,240,240)}QPushButton:hover{color:rgb(248,195,1)}")
        self.questionButton.setObjectName("questionButton")

        # 按钮图标
        self.icon0 = QtWidgets.QLabel(self.frame1)
        self.icon0.setEnabled(True)
        self.icon0.setGeometry(QtCore.QRect(int(40 * screen), int(20 * screen), int(40 * screen), int(40 * screen)))
        self.icon0.setStyleSheet("border-image:url(:/icon/0.png)")
        self.icon0.setText("")
        self.icon0.setObjectName("icon0")
        self.icon1 = QtWidgets.QLabel(self.frame1)
        self.icon1.setGeometry(QtCore.QRect(int(40 * screen), int(110 * screen), int(40 * screen), int(40 * screen)))
        self.icon1.setStyleSheet("border-image:url(:/icon/1.png)")
        self.icon1.setText("")
        self.icon1.setObjectName("icon1")
        self.icon2 = QtWidgets.QLabel(self.frame1)
        self.icon2.setGeometry(QtCore.QRect(int(40 * screen), int(200 * screen), int(40 * screen), int(40 * screen)))
        self.icon2.setStyleSheet("border-image:url(:/icon/2.png)")
        self.icon2.setText("")
        self.icon2.setObjectName("icon2")
        self.icon3 = QtWidgets.QLabel(self.frame1)
        self.icon3.setGeometry(QtCore.QRect(int(40 * screen), int(290 * screen), int(40 * screen), int(40 * screen)))
        self.icon3.setStyleSheet("border-image:url(:/icon/3.png)")
        self.icon3.setText("")
        self.icon3.setObjectName("icon3")
        self.icon4 = QtWidgets.QLabel(self.frame1)
        self.icon4.setGeometry(QtCore.QRect(int(40 * screen), int(380 * screen), int(40 * screen), int(40 * screen)))
        self.icon4.setStyleSheet("border-image:url(:/icon/4.png)")
        self.icon4.setText("")
        self.icon4.setObjectName("icon4")
        self.icon5 = QtWidgets.QLabel(self.frame1)
        self.icon5.setGeometry(QtCore.QRect(int(40 * screen), int(615 * screen), int(40 * screen), int(40 * screen)))
        self.icon5.setStyleSheet("border-image:url(:/icon/5.png)")
        self.icon5.setText("")
        self.icon5.setObjectName("icon5")
        self.icon0.raise_()
        self.icon1.raise_()
        self.icon2.raise_()
        self.icon3.raise_()
        self.icon4.raise_()
        self.icon5.raise_()
        self.homeButton.raise_()
        self.basicButton.raise_()
        self.echoButton.raise_()
        self.otherButton.raise_()
        self.logButton.raise_()
        self.questionButton.raise_()

        # 首页页面
        self.frame2 = QtWidgets.QFrame(self.centralwidget)
        self.frame2.setGeometry(QtCore.QRect(int(120 * screen), int(0 * screen), int(1128 * screen), int(702 * screen)))
        self.frame2.setStyleSheet("#frame2{background-color: rgb(39, 45, 43);border-top-right-radius:40px;border-bottom-right-radius:40px}")
        self.frame2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame2.setObjectName("frame2")

        # 首页图
        self.home = QtWidgets.QLabel(self.frame2)
        self.home.setGeometry(QtCore.QRect(0, int(0 * screen), int(1128 * screen), int(560 * screen)))
        self.home.setStyleSheet("border-top-right-radius:35px;border-image: url(:/icon/home.png);")
        self.home.setText("")
        self.home.setObjectName("home")

        # boss按钮
        self.bossButton = QtWidgets.QPushButton(self.frame2)
        self.bossButton.setEnabled(False)
        self.bossButton.setGeometry(QtCore.QRect(int(153 * screen), int(645 * screen), int(80 * screen), int(40 * screen)))
        self.bossButton.setFont(font)
        # self.bossButton.setStyleSheet("background-color: rgb(41, 230, 240)")
        self.bossButton.setObjectName("bossButton")

        # 合成按钮
        self.synthesisButton = QtWidgets.QPushButton(self.frame2)
        self.synthesisButton.setGeometry(QtCore.QRect(int(501 * screen), int(645 * screen), int(80 * screen), int(40 * screen)))
        self.synthesisButton.setFont(font)
        # self.synthesisButton.setStyleSheet("background-color: rgb(41, 230, /240)")
        self.synthesisButton.setObjectName("synthesisButton")


        # 结束按钮
        self.overButton = QtWidgets.QPushButton(self.frame2)
        self.overButton.setEnabled(False)
        self.overButton.setGeometry(QtCore.QRect(int(850 * screen), int(645 * screen), int(120 * screen), int(40 * screen)))
        self.overButton.setFont(font)
        # self.overButton.setStyleSheet("background-color: rgb(41, 230, 240)")
        self.overButton.setObjectName("overButton")

        # 按钮图标
        self.icon6 = QtWidgets.QLabel(self.frame2)
        self.icon6.setGeometry(QtCore.QRect(int(160 * screen), int(570 * screen), int(70 * screen), int(70 * screen)))
        self.icon6.setStyleSheet("border-image: url(:/icon/6.png);")
        self.icon6.setText("")
        self.icon6.setObjectName("icon6")
        self.icon7 = QtWidgets.QLabel(self.frame2)
        self.icon7.setGeometry(QtCore.QRect(int(505 * screen), int(570 * screen), int(70 * screen), int(70 * screen)))
        self.icon7.setStyleSheet("border-image: url(:/icon/7.png);")
        self.icon7.setText("")
        self.icon7.setObjectName("icon7")
        self.icon9 = QtWidgets.QLabel(self.frame2)
        self.icon9.setGeometry(QtCore.QRect(int(870 * screen), int(570 * screen), int(70 * screen), int(70 * screen)))
        self.icon9.setStyleSheet("border-image: url(:/icon/9.png);")
        self.icon9.setText("")
        self.icon9.setObjectName("icon9")

        # 提示
        self.tips = QtWidgets.QLabel(self.frame2)
        self.tips.setGeometry(QtCore.QRect(int(10 * screen), int(560 * screen), int(111 * screen), int(121 * screen)))
        self.tips.setStyleSheet("color: rgb(240, 240, 240)")
        self.tips.setFont(font)
        self.tips.setTextFormat(QtCore.Qt.AutoText)
        self.tips.setObjectName("tips")

        # 基础配置页面
        self.frame3 = QtWidgets.QFrame(self.centralwidget)
        self.frame3.setGeometry(QtCore.QRect(int(120 * screen), int(0 * screen), int(1128 * screen), int(702 * screen)))
        self.frame3.setStyleSheet("#frame3{background-color: rgb(39, 45, 43);border-top-right-radius:40px;border-bottom-right-radius:40px}")
        self.frame3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame3.setObjectName("frame3")

        # 游戏路径
        self.path = QtWidgets.QLabel(self.frame3)
        self.path.setGeometry(QtCore.QRect(int(30 * screen), int(20 * screen), int(731 * screen), int(40 * screen)))
        self.path.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.path.setFont(font)
        self.path.setObjectName("path")
        self.pathButton = QtWidgets.QPushButton(self.frame3)
        self.pathButton.setGeometry(QtCore.QRect(int(920 * screen), int(30 * screen), int(93 * screen), int(28 * screen)))
        self.pathButton.setStyleSheet("background-color: rgb(240, 240, 240)")
        self.pathButton.setFont(font)
        self.pathButton.setObjectName("pathButton")

        # 周本等级
        self.level = QtWidgets.QLabel(self.frame3)
        self.level.setGeometry(QtCore.QRect(int(30 * screen), int(60 * screen), int(90 * screen), int(40 * screen)))
        self.level.setStyleSheet("color: rgb(240, 240, 240)")
        self.level.setFont(font)
        self.level.setObjectName("level")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.levelBox = QtWidgets.QComboBox(self.frame3)
        self.levelBox.setGeometry(QtCore.QRect(int(130 * screen), int(65 * screen), int(60 * screen), int(30 * screen)))
        self.levelBox.setFont(font)
        self.levelBox.setObjectName("levelBox")
        self.levelBox.addItem("80")
        self.levelBox.addItem("70")
        self.levelBox.addItem("60")
        self.levelBox.addItem("50")
        self.levelBox.addItem("40")

        # 角色索引
        self.role = QtWidgets.QLabel(self.frame3)
        self.role.setGeometry(QtCore.QRect(int(330 * screen), int(60 * screen), int(100 * screen), int(40 * screen)))
        self.role.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.role.setFont(font)
        self.role.setObjectName("role")
        self.roleBox = QtWidgets.QSpinBox(self.frame3)
        self.roleBox.setGeometry(QtCore.QRect(int(450 * screen), int(65 * screen), int(100 * screen), int(31 * screen)))
        self.roleBox.setStyleSheet("background-color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.roleBox.setFont(font)
        self.roleBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.roleBox.setAccelerated(False)
        self.roleBox.setMinimum(1)
        self.roleBox.setMaximum(333333333)
        self.roleBox.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.roleBox.setProperty("value", 123)
        self.roleBox.setDisplayIntegerBase(10)
        self.roleBox.setObjectName("roleBox")

        # 是否维
        self.iswei = QtWidgets.QLabel(self.frame3)
        self.iswei.setGeometry(QtCore.QRect(int(620 * screen), int(60 * screen), int(140 * screen), int(40 * screen)))
        self.iswei.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.iswei.setFont(font)
        self.iswei.setObjectName("iswei")
        self.radioButton1 = QtWidgets.QRadioButton(self.frame3)
        self.radioButton1.setGeometry(QtCore.QRect(int(770 * screen), int(65 * screen), int(80 * screen), int(31 * screen)))
        self.radioButton1.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.radioButton1.setFont(font)
        self.radioButton1.setObjectName("radioButton1")
        self.radioButton2 = QtWidgets.QRadioButton(self.frame3)
        self.radioButton2.setGeometry(QtCore.QRect(int(860 * screen), int(65 * screen), int(80 * screen), int(31 * screen)))
        self.radioButton2.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.radioButton2.setFont(font)
        self.radioButton2.setObjectName("radioButton2")

        self.group1 = QtWidgets.QButtonGroup(self.frame3)
        self.group1.addButton(self.radioButton1)
        self.group1.addButton(self.radioButton2)

        # boss列表
        self.boss = QtWidgets.QLabel(self.frame3)
        self.boss.setGeometry(QtCore.QRect(int(30 * screen), int(100 * screen), int(90 * screen), int(40 * screen)))
        self.boss.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.boss.setFont(font)
        self.boss.setObjectName("boss")
        self.bossBox = ComboCheckBox(self.frame3, ["无妄者", "角", "赫卡忒", "芙露德莉斯", "梦魇赫卡忒", "罗蕾莱", "异构武装", "叹息古龙", "荣耀狮像", "梦魇凯尔匹", "梦魇飞廉之猩", "梦魇无常凶鹭", "梦魇云闪之鳞", "梦魇朔雷之鳞", "梦魇无冠者", "梦魇燎照之骑", "梦魇哀声鸷", "梦魇辉萤军势", "鸣钟之龟", "无归的谬误", "朔雷之鳞", "燎照之骑", "无常凶鹭", "辉萤军势", "飞廉之猩", "哀声鸷", "无冠者", "聚械机偶", "云闪之鳞"])
        self.bossBox.setGeometry(QtCore.QRect(int(130 * screen), int(105 * screen), int(180 * screen), int(31 * screen)))
        self.bossBox.setObjectName("bossBox")

        # 是否2命维
        self.twoWei = QtWidgets.QLabel(self.frame3)
        self.twoWei.setGeometry(QtCore.QRect(int(330 * screen), int(100 * screen), int(140 * screen), int(40 * screen)))
        self.twoWei.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.twoWei.setFont(font)
        self.twoWei.setObjectName("twoWei")
        self.radioButton3 = QtWidgets.QRadioButton(self.frame3)
        self.radioButton3.setGeometry(QtCore.QRect(int(460 * screen), int(107 * screen), int(80 * screen), int(31 * screen)))
        self.radioButton3.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.radioButton3.setFont(font)
        self.radioButton3.setObjectName("radioButton3")
        self.radioButton4 = QtWidgets.QRadioButton(self.frame3)
        self.radioButton4.setGeometry(QtCore.QRect(int(550 * screen), int(107 * screen), int(80 * screen), int(31 * screen)))
        self.radioButton4.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.radioButton4.setFont(font)
        self.radioButton4.setObjectName("radioButton4")

        self.group2 = QtWidgets.QButtonGroup(self.frame3)
        self.group2.addButton(self.radioButton3)
        self.group2.addButton(self.radioButton4)

        # 是否自动启动
        self.auto = QtWidgets.QLabel(self.frame3)
        self.auto.setGeometry(QtCore.QRect(int(620 * screen), int(100 * screen), int(140 * screen), int(40 * screen)))
        self.auto.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.auto.setFont(font)
        self.auto.setObjectName("auto")
        self.radioButton5 = QtWidgets.QRadioButton(self.frame3)
        self.radioButton5.setGeometry(QtCore.QRect(int(770 * screen), int(107 * screen), int(80 * screen), int(31 * screen)))
        self.radioButton5.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.radioButton5.setFont(font)
        self.radioButton5.setObjectName("radioButton5")
        self.radioButton6 = QtWidgets.QRadioButton(self.frame3)
        self.radioButton6.setGeometry(QtCore.QRect(int(860 * screen), int(107 * screen), int(80 * screen), int(31 * screen)))
        self.radioButton6.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.radioButton6.setFont(font)
        self.radioButton6.setObjectName("radioButton6")

        self.group3 = QtWidgets.QButtonGroup(self.frame3)
        self.group3.addButton(self.radioButton5)
        self.group3.addButton(self.radioButton6)

        # 每日
        self.everyday = QtWidgets.QLabel(self.frame3)
        self.everyday.setGeometry(QtCore.QRect(int(30 * screen), int(140 * screen), int(90 * screen), int(40 * screen)))
        self.everyday.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.everyday.setFont(font)
        self.everyday.setObjectName("everyday")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.tarBox = QtWidgets.QComboBox(self.frame3)
        self.tarBox.setGeometry(QtCore.QRect(int(130 * screen), int(150 * screen), int(120 * screen), int(30 * screen)))
        self.tarBox.setFont(font)
        self.tarBox.setObjectName("tarBox")
        self.tarBox.setMaxVisibleItems(7)
        self.tarBox.addItem("关闭")
        self.tarBox.addItem("无")
        self.tarBox.addItem("愿戴/奔狼")
        self.tarBox.addItem("流云/幽夜")
        self.tarBox.addItem("此间/无惧")
        self.tarBox.addItem("凌冽/此间")
        self.tarBox.addItem("幽夜/高天")
        self.tarBox.addItem("风套/冰套")
        self.tarBox.addItem("冰套/雷套")
        self.tarBox.addItem("光套/不绝")
        self.tarBox.addItem("雷套/火套")
        self.tarBox.addItem("暗套/轻云")
        self.tarBox.addItem("迅刀")
        self.tarBox.addItem("音感仪")
        self.tarBox.addItem("长刃")
        self.tarBox.addItem("拳套")
        self.tarBox.addItem("枪")
        # 连招
        self.fight = QtWidgets.QLabel(self.frame3)
        self.fight.setGeometry(QtCore.QRect(int(30 * screen), int(230 * screen), int(90 * screen), int(40 * screen)))
        self.fight.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.fight.setFont(font)
        self.fight.setObjectName("fight")
        self.fightText = QtWidgets.QTextBrowser(self.frame3)
        self.fightText.setGeometry(QtCore.QRect(int(130 * screen), int(250 * screen), int(381 * screen), int(310 * screen)))
        self.fightText.setStyleSheet("color: rgb(240,240,240);border: 1px solid block;QTextBrowser:active{border: 1px solid rgb(0,120,215)}")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.fightText.setFont(font)
        self.fightText.setReadOnly(False)
        self.fightText.setObjectName("rightText")

        # 开大连招
        self.ultFight = QtWidgets.QLabel(self.frame3)
        self.ultFight.setGeometry(QtCore.QRect(int(540 * screen), int(230 * screen), int(90 * screen), int(40 * screen)))
        self.ultFight.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.ultFight.setFont(font)
        self.ultFight.setObjectName("ultFight")
        self.ultFightText = QtWidgets.QTextBrowser(self.frame3)
        self.ultFightText.setGeometry(QtCore.QRect(int(640 * screen), int(250 * screen), int(381 * screen), int(310 * screen)))
        self.ultFightText.setStyleSheet("color: rgb(240,240,240);border: 1px solid block;QTextBrowser:active{border: 1px solid rgb(0,120,215)}")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.ultFightText.setFont(font)
        self.ultFightText.setReadOnly(False)
        self.ultFightText.setObjectName("ultFightText")

        # 编写
        self.fightTip = QtWidgets.QLabel(self.frame3)
        self.fightTip.setGeometry(QtCore.QRect(int(280 * screen), int(555 * screen), int(571 * screen), int(161 * screen)))
        self.fightTip.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.fightTip.setFont(font)
        self.fightTip.setObjectName("fightTip")

        # 声骸配置
        self.frame4 = QtWidgets.QFrame(self.centralwidget)
        self.frame4.setGeometry(QtCore.QRect(int(120 * screen), int(0 * screen), int(1128 * screen), int(702 * screen)))
        self.frame4.setStyleSheet("#frame4{background-color: rgb(39, 45, 43);border-top-right-radius:40px;border-bottom-right-radius:40px}")
        self.frame4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame4.setObjectName("frame4")

        # 开发
        self.frame5 = QtWidgets.QFrame(self.centralwidget)
        self.frame5.setGeometry(QtCore.QRect(int(120 * screen), int(0 * screen), int(1128 * screen), int(702 * screen)))
        self.frame5.setStyleSheet("#frame5{background-color: rgb(39, 45, 43);border-top-right-radius:40px;border-bottom-right-radius:40px}")
        self.frame5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame5.setObjectName("frame5")

        # 日志
        self.frame6 = QtWidgets.QFrame(self.centralwidget)
        self.frame6.setGeometry(QtCore.QRect(int(120 * screen), int(0 * screen), int(1128 * screen), int(702 * screen)))
        self.frame6.setStyleSheet("QFrame{background-color: rgb(39, 45, 43);border-top-right-radius:40px;border-bottom-right-radius:40px}")
        self.frame6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame6.setObjectName("frame6")

        self.logText = QtWidgets.QTextBrowser(self.frame6)
        self.logText.setGeometry(QtCore.QRect(int(20 * screen), int(10 * screen), int(971 * screen), int(671 * screen)))
        self.logText.setStyleSheet("background-color: rgb(60,60,60);border: 1px solid white;border-top-right-radius:0px;border-bottom-right-radius:0px;color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.logText.setFont(font)
        self.logText.setReadOnly(True)
        self.logText.setObjectName("logText")

        self.clearLogButton = QtWidgets.QPushButton(self.frame6)
        self.clearLogButton.setGeometry(QtCore.QRect(int(1000 * screen), int(640 * screen), int(93 * screen), int(41 * screen)))
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.clearLogButton.setFont(font)
        self.clearLogButton.setObjectName("clearLogButton")

        self.shenmiButton = QtWidgets.QPushButton(self.frame6)
        self.shenmiButton.setGeometry(QtCore.QRect(int(1000 * screen), int(580 * screen), int(93 * screen), int(41 * screen)))
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(12 * scale_factor))
        self.shenmiButton.setFont(font)
        self.shenmiButton.setObjectName("shenmiButton")

        # 统计
        self.echoNum = QtWidgets.QLabel(self.frame6)
        self.echoNum.setGeometry(QtCore.QRect(int(1000 * screen), int(60 * screen), int(111 * screen), int(121 * screen)))
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(16 * scale_factor))
        self.echoNum.setFont(font)
        self.echoNum.setTextFormat(QtCore.Qt.AutoText)
        self.echoNum.setObjectName("echoNum")

        # 用前必看
        self.frame7 = QtWidgets.QFrame(self.centralwidget)
        self.frame7.setGeometry(QtCore.QRect(int(120 * screen), int(0 * screen), int(1128 * screen), int(702 * screen)))
        self.frame7.setStyleSheet("#frame7{background-color: rgb(39, 45, 43);border-top-right-radius:40px;border-bottom-right-radius:40px}")
        self.frame7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame7.setObjectName("frame7")

        self.questionLabel = QtWidgets.QLabel(self.frame7)
        self.questionLabel.setGeometry(QtCore.QRect(int(30 * screen), int(15 * screen), int(991 * screen), int(230 * screen)))
        self.questionLabel.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.questionLabel.setFont(font)
        self.questionLabel.setTextFormat(QtCore.Qt.AutoText)
        self.questionLabel.setObjectName("questionLabel")

        # 下载进度条
        self.progressLabel = QtWidgets.QLabel(self.frame7)
        self.progressLabel.setGeometry(QtCore.QRect(int(30 * screen), int(650 * screen), int(120 * screen), int(20 * screen)))
        self.progressLabel.setStyleSheet("color: rgb(240, 240, 240)")
        font = QtGui.QFont()
        font.setFamily("筑紫A丸")
        font.setPointSize(int(15 * scale_factor))
        self.progressLabel.setFont(font)
        self.progressLabel.setTextFormat(QtCore.Qt.AutoText)
        self.progressLabel.setObjectName("progressLabel")
        self.progressBar = QtWidgets.QProgressBar(self.frame7)
        self.progressBar.setGeometry(QtCore.QRect(int(160 * screen), int(650 * screen), int(700 * screen), int(25 * screen)))
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)  # 初始值为0
        self.progressBar.setStyleSheet("color: rgb(240, 240, 240)")
        self.progressBar.setFont(font)

        self.frame7.raise_()
        self.frame6.raise_()
        self.frame5.raise_()
        self.frame4.raise_()
        self.frame3.raise_()
        self.frame2.raise_()
        self.frame1.raise_()
        self.frame0.raise_()
        sys.stdout = OutputRedirector(self.logText, self.echoNum, self.startOver)
        MainWindow.setCentralWidget(self.centralwidget)

        def isdown():
            if self.flag:
                msgBox = QMessageBox()
                msgBox.setWindowIcon(QIcon("icon.png"))  # 设置自定义图标
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setWindowTitle("?")  # 设置窗口标题
                msgBox.setText("还没下载完就想走? 哪有这种好事")  # 设置消息内容
                msgBox.exec_()
                return
            return MainWindow.close()

        self.retranslateUi(MainWindow)
        self.miniButton.clicked.connect(MainWindow.showMinimized)  # type: ignore
        self.closeButton.clicked.connect(isdown)  # type: ignore
        self.homeButton.clicked.connect(self.frame2.show)  # type: ignore
        self.homeButton.clicked.connect(self.frame3.hide)  # type: ignore
        self.homeButton.clicked.connect(self.frame4.hide)  # type: ignore
        self.homeButton.clicked.connect(self.frame5.hide)  # type: ignore
        self.homeButton.clicked.connect(self.frame6.hide)  # type: ignore
        self.homeButton.clicked.connect(self.frame7.hide)  # type: ignore

        self.basicButton.clicked.connect(self.frame2.hide)  # type: ignore
        self.basicButton.clicked.connect(self.frame3.show)  # type: ignore
        self.basicButton.clicked.connect(self.frame4.hide)  # type: ignore
        self.basicButton.clicked.connect(self.frame5.hide)  # type: ignore
        self.basicButton.clicked.connect(self.frame6.hide)  # type: ignore
        self.basicButton.clicked.connect(self.frame7.hide)  # type: ignore

        self.echoButton.clicked.connect(self.frame2.hide)  # type: ignore
        self.echoButton.clicked.connect(self.frame3.hide)  # type: ignore
        self.echoButton.clicked.connect(self.frame4.show)  # type: ignore
        self.echoButton.clicked.connect(self.frame5.hide)  # type: ignore
        self.echoButton.clicked.connect(self.frame6.hide)  # type: ignore
        self.echoButton.clicked.connect(self.frame7.hide)  # type: ignore

        self.otherButton.clicked.connect(self.frame2.hide)  # type: ignore
        self.otherButton.clicked.connect(self.frame3.hide)  # type: ignore
        self.otherButton.clicked.connect(self.frame4.hide)  # type: ignore
        self.otherButton.clicked.connect(self.frame5.show)  # type: ignore
        self.otherButton.clicked.connect(self.frame6.hide)  # type: ignore
        self.otherButton.clicked.connect(self.frame7.hide)  # type: ignore

        self.logButton.clicked.connect(self.frame2.hide)   # type: ignore
        self.logButton.clicked.connect(self.frame3.hide)   # type: ignore
        self.logButton.clicked.connect(self.frame4.hide)   # type: ignore
        self.logButton.clicked.connect(self.frame5.hide)   # type: ignore
        self.logButton.clicked.connect(self.frame6.show)   # type: ignore
        self.logButton.clicked.connect(self.frame7.hide)   # type: ignore

        self.questionButton.clicked.connect(self.frame2.hide)  # type: ignore
        self.questionButton.clicked.connect(self.frame3.hide)  # type: ignore
        self.questionButton.clicked.connect(self.frame4.hide)  # type: ignore
        self.questionButton.clicked.connect(self.frame5.hide)  # type: ignore
        self.questionButton.clicked.connect(self.frame6.hide)  # type: ignore
        self.questionButton.clicked.connect(self.frame7.show)  # type: ignore

        self.bossButton.clicked.connect(self.startBoss)  # type: ignore
        self.synthesisButton.clicked.connect(self.startSynthesis)  # type: ignore
        self.overButton.clicked.connect(self.startOver)  # type: ignore

        self.pathButton.clicked.connect(self.openFile)  # type: ignore
        self.bossBox.signa.connect(self.getBoss)  # type: ignore
        self.clearLogButton.clicked.connect(self.clearLog)  # type: ignore
        self.shenmiButton.clicked.connect(self.download)  # type: ignore
        if version_now == version_new:
            self.initConfig()
        threading.Thread(target=self.saveConfig).start()
        thread = threading.Thread(target=self.listener)
        thread.daemon = True  # 设置为守护线程
        thread.start()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def update_progress_bar(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            self.signal.emit(2)

    def download_new(self, value):
        if value == 1:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon("icon.png"))  # 设置自定义图标
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("发现更新")
            msg_box.setText(f"发现新版本 {version_new}，是否立即更新?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            reply = msg_box.exec_()
            if reply == QMessageBox.Yes:
                self.up = 1
                self.frame1.raise_()
                self.frame2.raise_()
                self.frame3.raise_()
                self.frame4.raise_()
                self.frame5.raise_()
                self.frame6.raise_()
                self.frame7.raise_()
                self.frame0.raise_()
            else:
                self.up = 2
                self.initConfig()
        else:
            msg_box = QMessageBox()
            msg_box.setWindowIcon(QIcon("icon.png"))  # 设置自定义图标
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("更新完成")
            msg_box.setText(f"更新完成,请重新启动")
            msg_box.setStandardButtons(QMessageBox.Yes)
            msg_box.setDefaultButton(QMessageBox.Yes)
            msg_box.exec_()
            os._exit(0)


    def startBoss(self):
        self.name = "boss"
        self.bossButton.setEnabled(False)
        self.synthesisButton.setEnabled(False)
        self.overButton.setEnabled(True)
        threading.Thread(target=self.action).start()
        threading.Thread(target=self.ys).start()

    def startSynthesis(self):
        self.name = "合成"
        self.bossButton.setEnabled(False)
        self.synthesisButton.setEnabled(False)
        self.overButton.setEnabled(True)
        threading.Thread(target=self.action).start()

    def startOver(self):
        if self.overButton.isEnabled():
            self.name = "over"
            threading.Thread(target=self.over).start()
            print(f"{datetime.now().strftime('%m-%d %H:%M:%S')} 等待结束...")

    def action(self):
        print(f"{datetime.now().strftime('%m-%d %H:%M:%S')} 正在初始化...")
        try:
            from start import start
        except Exception as e:
            self.name = ""
            print(f"{datetime.now().strftime('%m-%d %H:%M:%S')} 初始化失败红")
            print(e)
            return
        start(self.name)

    def over(self):
        try:
            from start import over
        except:
            return
        finally:
            if self.temp1:
                self.bossButton.setEnabled(True)
            self.synthesisButton.setEnabled(True)
            self.overButton.setEnabled(False)
        over()

    def on_press(self, key):
        if key == keyboard.Key.f6:
            self.startOver()

    def listener(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def openFile(self):
        path = QFileDialog.getOpenFileNames(None, "选择游戏路径")[0]
        if path:
            self.path.setText("游戏路径:  " + path[0])

    def clearLog(self):
        self.logText.clear()

    def getBoss(self, x):
        self.bossList = x

    def download(self):
        self.shenmiButton.setEnabled(False)
        threading.Thread(target=self.load).start()

    def load(self):
        self.flag = True
        print("你做了错误的选择!红")
        res = random.randint(1, 3)
        if res == 1:
            response = requests.get("https://autopatchcn.yuanshen.com/client_app/download/launcher/20250317181110_rtA8y57iZNFVnGJx/mihoyo/yuanshen_setup_202503072031.exe", stream=True)
        elif res == 2:
            response = requests.get("https://autopatchcn.bhsr.com/client/cn/20250317183241_lhOtRZWQ64Sza68d/gw_PC/StarRail_setup_1.5.2.exe", stream=True)
        else:
            response = requests.get("https://autopatchcn.juequling.com/package_download/op/client_app/download/20250324175258_GO21zPUn69HuWpUk/ZenlessZoneZero_setup_202503241539.exe", stream=True)
        response.raise_for_status()
        try:
            with open("genshin.exe", 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
        except:
            print("算你运气好红")
            self.flag = False
            return
        print("米游启动器下载完成!绿")
        subprocess.Popen("genshin.exe")
        time.sleep(2)
        hw = win32gui.FindWindow("Qt51517QWindowIcon", "米哈游启动器 安装程序")
        windll.shcore.SetProcessDpiAwareness(1)  # 设置dpi感知
        long_position = win32api.MAKELONG(int(55 / scale_factor), int(530 / scale_factor))
        win32gui.PostMessage(hw, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
        win32gui.PostMessage(hw, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)
        time.sleep(0.1)
        long_position = win32api.MAKELONG(int(500 * scale_factor), int(400 * scale_factor))
        win32gui.PostMessage(hw, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
        win32gui.PostMessage(hw, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)
        self.ys()
        self.flag = False
    def ys(self):
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        mixer.init()
        mixer.music.load(os.path.join(root_path, "template/ys.mp3"))
        mixer.music.play()
        while mixer.music.get_busy():
            pass
        mixer.quit()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", f"卡卡罗助手v{version_now}"))
        self.basicButton.setText(_translate("MainWindow", "\n基础配置"))
        self.echoButton.setText(_translate("MainWindow", "\n声骸配置"))
        self.questionButton.setText(_translate("MainWindow", "\n用前必看"))
        self.logButton.setText(_translate("MainWindow", "\n日志"))
        self.homeButton.setText(_translate("MainWindow", "\n首页"))
        self.otherButton.setText(_translate("MainWindow", "\n其他功能"))
        self.path.setText(_translate("MainWindow", "游戏路径:  "))
        self.pathButton.setText(_translate("MainWindow", "选择"))
        self.level.setText(_translate("MainWindow", "周本等级:"))
        self.role.setText(_translate("MainWindow", "角色索引:"))
        self.boss.setText(_translate("MainWindow", "Boss列表:"))
        self.iswei.setText(_translate("MainWindow", "1号位是否维: "))
        self.twoWei.setText(_translate("MainWindow", "是否二命维: "))
        self.auto.setText(_translate("MainWindow", "是否自动启动: "))
        self.everyday.setText(_translate("MainWindow", "每日双倍: "))
        self.radioButton1.setText(_translate("MainWindow", "是"))
        self.radioButton2.setText(_translate("MainWindow", "否"))
        self.radioButton3.setText(_translate("MainWindow", "是"))
        self.radioButton4.setText(_translate("MainWindow", "否"))
        self.radioButton5.setText(_translate("MainWindow", "是"))
        self.radioButton6.setText(_translate("MainWindow", "否"))
        self.fight.setText(_translate("MainWindow", "战斗策略:"))
        self.ultFight.setText(_translate("MainWindow", "大招策略:"))
        self.fightTip.setText(_translate("MainWindow", "                                             如何编写\n"
"a=普攻  e=共鸣技能  q=声骸技能  r=大招  s=跳跃  l=闪避(小写L)  \n"
"                  a(数字)=连续普攻数字秒  z=重击\n"
"                            每个按键用,分开 一个角色一行"))
        self.bossButton.setText(_translate("MainWindow", "Boss"))
        self.synthesisButton.setText(_translate("MainWindow", "合成"))
        self.overButton.setText(_translate("MainWindow", "结束(F6)"))
        self.tips.setText(_translate("MainWindow", "首次使用\n"
"建议先查看\n"
"用前必看"))
        self.clearLogButton.setText(_translate("MainWindow", "清空"))
        self.shenmiButton.setText(_translate("MainWindow", "神秘按钮"))
        self.echoNum.setText(_translate("MainWindow", '<font color="#f0f0f0">当前声骸<br/>个数: 0</font>'))
        self.progressLabel.setText(_translate("MainWindow", "更新进度条: "))
        self.questionLabel.setText(_translate("MainWindow", "1. 需要管理员模式打开程序才可以正常使用, 初始化时不要关闭\n"
                                                            "2. 游戏窗口必须为16:9, 推荐为1280*720, 镜头重置必须打开\n"
                                                            "3. 先写配置再启动, 合成需要进入合成界面, 其他在大世界\n"
                                                            "4. 更新神秘按钮\n"
                                                            "5. 探索工具需要用钩锁\n"
                                                            "6. 有问题先看日志"))

    def initConfig(self):
        a = 0
        if config.AppPath:
            self.path.setText("游戏路径:  " + config.AppPath)
            a += 1
        if config.DungeonWeeklyBossLevel:
            self.levelBox.setCurrentText(str(config.DungeonWeeklyBossLevel))
            a += 1
        if config.RoleIndex:
            self.roleBox.setValue(int(config.RoleIndex))
            a += 1
        if config.TargetBoss:
            for i in self.bossBox.qCheckBox:
                if i.text() in config.TargetBoss:
                    i.setCheckState(2)
            a += 1
        if config.IsWei:
            self.radioButton1.setChecked(True)
        else:
            self.radioButton2.setChecked(True)
        if config.TwoWei:
            if config.TwoWei == 2:
                self.radioButton3.setChecked(True)
            else:
                self.radioButton4.setChecked(True)
        if config.Automatic:
            self.radioButton5.setChecked(True)
        else:
            self.radioButton6.setChecked(True)
        if config.FightTactics:
            self.fightText.setText('\n'.join(map(str, config.FightTactics)))
            a += 1
        if config.FightTacticsUlt:
            self.ultFightText.setText('\n'.join(map(str, config.FightTacticsUlt)))
        self.tarBox.setCurrentText(str(config.TargetChallenge))
        if a == 5:
            self.bossButton.setEnabled(True)
            self.temp1 = 1

    def saveConfig(self):
        basicConfig = {}
        while True:
            try:
                time.sleep(1)
                self.path.text()
                if version_now != version_new and self.up == 0:
                    self.signal.emit(1)
                    while not self.up:
                        pass
                    if self.up == 1:
                        update(self.progress_signal.emit)
                        return
                if self.radioButton1.isChecked():
                    Iswei = True
                else:
                    Iswei = False
                if self.radioButton3.isChecked():
                    wei = 2
                else:
                    wei = 1
                if self.radioButton5.isChecked():
                    Automatic = True
                else:
                    Automatic = False
                temp = {
                    "AppPath": self.path.text()[7:],
                    "DungeonWeeklyBossLevel": self.levelBox.currentText(),
                    "RoleIndex": self.roleBox.text(),
                    "IsWei": Iswei,
                    "TwoWei": wei,
                    "TargetBoss": self.bossList,
                    "FightTactics": self.fightText.toPlainText().split("\n"),
                    "FightTacticsUlt": self.ultFightText.toPlainText().split("\n"),
                    "TargetChallenge": self.tarBox.currentText(),
                    "Automatic": Automatic
                }
                if basicConfig != temp:
                    if self.path.text()[7:] and self.bossList and self.fightText.toPlainText():
                        self.temp1 = 1
                        if self.name in ["", "over"]:
                            self.bossButton.setEnabled(True)
                    else:
                        self.temp1 = 0
                        self.bossButton.setEnabled(False)
                    basicConfig = temp
                    with open('config.yaml', 'w', encoding="utf-8") as f:
                        yaml.dump(basicConfig, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            except:
                return