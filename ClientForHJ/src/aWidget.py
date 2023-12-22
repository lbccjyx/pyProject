import os
from datetime import time
from functools import partial

from PySide6.QtWidgets import QWidget, QCompleter, QMessageBox, QLineEdit, QFileDialog
from PySide6.QtCore import Qt, QTimer, QFile, QTextStream
from PySide6.QtGui import QTextCursor, QKeyEvent

import bilibili
import douyin
from ui_form import Ui_Widget
from CommonClient import common as myCommon
from CommonClient import AnimationShadowEffect
import paramiko
import logging
import re

def get_lua_path_and_append(original_path, target_path):
    # 找到 "lua" 在原始路径中的位置
    lua_index = original_path.find("lua")
    if lua_index == -1:
        return "在原始路径中没有找到 'lua'。"
    # 获取 "lua" 后面的部分
    lua_path = original_path[lua_index:]
    # 将这个部分拼接到目标路径的后面
    new_path = target_path.strip() + "/" + lua_path
    return new_path

class AWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.threadworker_RunDOUYIN = None
        self.ColorMode = myCommon.DarkNormalMode(self)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.__init_Member_variables()
        self.__begin_show()

    def on_log_changed(self, msg: str):
        self.ui.textBrowser.append(msg)
        self.ui.textBrowser.moveCursor(QTextCursor.End)

    def __init_Member_variables(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("__init_Member_variables")

        self.aniblue = AnimationShadowEffect.AnimationShadowEffect(Qt.blue)
        self.aniblue.start()
        self.ui.edtCommand.setGraphicsEffect(self.aniblue)

        self.ui.pushButton_DOUYIN.clicked.connect(self.Button_start_DOUYIN_click)
        self.ui.pushButton_BILIBILI.clicked.connect(self.Button_start_BILIBILI_click)
        self.ui.pushButton_Mode.clicked.connect(self.on_Mode_changed)
        self.ui.edtCommand.textChanged.connect(self.on_text_changed)

        # 缓存
        self.edtCommandHistory = set()
        completer = QCompleter(self.edtCommandHistory, self.ui.edtCommand)
        self.ui.edtCommand.setCompleter(completer)

        # logging打印出来的log 显示在self.ui.textBrowser上
        myCommon.LoggingHandler(self.on_log_changed)

        # 打开文件并读取内容
        file = QFile("../cfg/config.py")
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            self.ui.textEdit.setPlainText(stream.readAll())
            file.close()

        # 连接信号和槽
        self.ui.textEdit.textChanged.connect(self.saveToFile)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if isinstance(self.focusWidget(), QLineEdit):
                self.onConfirm()
        else:
            super().keyPressEvent(event)

    def saveToFile(self):
        # 当文本编辑器的内容改变时，将新的内容保存到文件中
        file = QFile("../cfg/config.py")
        if file.open(QFile.WriteOnly | QFile.Text):
            stream = QTextStream(file)
            stream << self.ui.textEdit.toPlainText()
            file.close()

    def onConfirm(self):
        if len(self.ui.edtCommand.text()) > 0:
            logging.info(f"roomid: {self.ui.edtCommand.text()}")


    def __begin_show(self):
        logging.info("__begin_show")

        # 缓存
        self.edtCommandHistory = set()
        completer = QCompleter(self.edtCommandHistory, self.ui.edtCommand)
        self.ui.edtCommand.setCompleter(completer)

    def on_text_changed(self):
        if "rm" in self.ui.edtCommand.text():
            self.ui.edtCommand.clear()

    def Button_start_BILIBILI_click(self):
        self.ui.pushButton_BILIBILI.setDisabled(True)
        bilibili.begin_bilibili_websocket()

    def Button_start_DOUYIN_click(self):
        if len(self.ui.edtCommand.text()) <= 0:
            logging.info("抖音房间还没给出来")
            return
        self.ui.pushButton_DOUYIN.setDisabled(True)

        bound_RunMoveGS = partial(
            douyin.begin_douyin_websocket, self.ui.edtCommand.text()
        )
        self.threadworker_RunDOUYIN = myCommon.ThreadWorker(bound_RunMoveGS)
        self.threadworker_RunDOUYIN.signal.connect(self.__on_movegs_success)
        self.threadworker_RunDOUYIN.start()

    def __on_movegs_success(self):
        logging.info("===========================================")

    def on_Mode_changed(self):
        self.ColorMode.turnMode()
        if self.ColorMode.mode == myCommon.Mode.NORMAL:
            self.aniblue.setColor(Qt.blue)

            html_content = self.ui.textBrowser.toHtml()
            html_content_modified = re.sub("color:#ffffff", "color:#000000", html_content)
            self.ui.textBrowser.setHtml(html_content_modified)

        if self.ColorMode.mode == myCommon.Mode.DARK:
            self.aniblue.setColor(Qt.cyan)

            html_content = self.ui.textBrowser.toHtml()
            html_content_modified = re.sub("color:#000000", "color:#ffffff", html_content)
            self.ui.textBrowser.setHtml(html_content_modified)
