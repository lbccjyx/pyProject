from PySide6.QtWidgets import QWidget, QCompleter
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from ui_form import Ui_Widget
from CommonClient import common as myCommon
from CommonClient import AnimationShadowEffect

import logging
import re

class AWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ColorMode = myCommon.DarkNormalMode(self)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.__init_Member_variables()
        self.__begin_show()

    def on_log_changed(self, msg: str):
        self.ui.textBrowser.append(msg)
        self.ui.textBrowser.moveCursor(QTextCursor.End)

    def __init_Member_variables(self):
        logging.info("__init_Member_variables")

        self.aniblue = AnimationShadowEffect.AnimationShadowEffect(Qt.blue)
        self.aniblue.start()
        self.ui.LineEdit.setGraphicsEffect(self.aniblue)

        self.ui.pushButton_create.clicked.connect(self.Button_create_click)
        self.ui.pushButton_Mode.clicked.connect(self.on_Mode_changed)
        self.ui.LineEdit.textChanged.connect(self.on_text_changed)

        # logging打印出来的log 显示在self.ui.textBrowser上
        myCommon.LoggingHandler(self.on_log_changed)
        logging.info("hello")

    def __begin_show(self):
        logging.info("__begin_show")

        # 缓存
        self.TargetLanIPHistory = set()
        completer = QCompleter(self.TargetLanIPHistory, self.ui.LineEdit)
        self.ui.LineEdit.setCompleter(completer)

        # 做一个可拉动效果
        splitter = myCommon.QSplitter(self)
        splitter.addWidget(self.ui.tableWidget)
        splitter_between_widgets = myCommon.MySplitter(self)
        splitter.addWidget(splitter_between_widgets)
        splitter.addWidget(self.ui.textBrowser)
        splitter.setOrientation(Qt.Vertical)
        self.ui.verticalLayout.addWidget(splitter)

    def on_text_changed(self):
        logging.info("on_text_changed")

    def Button_create_click(self):
        logging.info("Button_create_click")


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
