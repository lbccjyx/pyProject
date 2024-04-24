from logging import LogRecord
import logging
from enum import Enum
import re

from PySide6.QtWidgets import QWidget, QSplitter, QSplitterHandle
from PySide6.QtCore import QRegularExpression, QThread, Signal, QObject, Qt
from PySide6.QtGui import QRegularExpressionValidator


# 设置为只能输ip的方法：QineEdit.setValidator(validator)
ip_regex = QRegularExpression("^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$")
validator = QRegularExpressionValidator(ip_regex)


class Mode(Enum):
    NORMAL = 1
    DARK = 2


# 用于切换颜色模式
class DarkNormalMode:
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.mode = Mode.NORMAL

    def turnMode(self):
        if self.mode == Mode.NORMAL:
            self.switch_to_dark_mode()
            self.mode = Mode.DARK
        else:
            self.switch_to_normal_mode()
            self.mode = Mode.NORMAL

    # 黑夜模式
    def switch_to_dark_mode(self):
        dark_palette = """
        QWidget {
            background-color: #2b2b2b;
            color: #b3b3b3;
        }
        """
        self.widget.setStyleSheet(dark_palette)

    # 正常模式
    def switch_to_normal_mode(self):
        self.widget.setStyleSheet("")


class TextEditSignalEmitter(QObject):
    file_modified = Signal(str)


class TextEditHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.emitter = TextEditSignalEmitter()

        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d"
        self.formatter = logging.Formatter(log_format)

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)

        if record.levelno == logging.INFO:
            color = "black"
        elif record.levelno == logging.WARNING:
            color = "orange"
        elif record.levelno == logging.ERROR:
            color = "red"
        else:
            color = "green"

        self.emitter.file_modified.emit(f'<p style="color: {color};">{msg}</p>')

    def format(self, record: LogRecord) -> str:

        # 清理消息字符串
        # record.msg = clean_output(record.msg)
        # 使用正则表达式匹配并提取关键部分
        match = re.search(r'\[?2004.(.*?)\[\?2004*', record.msg, re.DOTALL)
        if match:
            record.msg = match.group(1).strip()
            matches = re.findall(r'\[01;34m(.*?)\[0m', record.msg)
            if matches:
                record.msg =matches

        return self.formatter.format(record)

def clean_output(raw_output):
    # 清理字符串，移除控制字符和乱码
    cleaned_output = ''.join(char for char in raw_output if 32 <= ord(char) <= 126)
    return cleaned_output

# 需要和 MyLogController 的 logging 配合使用
def LoggingHandler(callback_function: any):
    handler = TextEditHandler()
    handler.emitter.file_modified.connect(callback_function)
    logging.getLogger().addHandler(handler)


class ThreadWorker(QThread):
    signal = Signal(list)

    def __init__(self, func: any):
        QThread.__init__(self)
        self.func = func

    def run(self):
        result = self.func()
        self.signal.emit(result)


class SplitterHandle(QSplitterHandle):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果不设置这个，则鼠标只能在按下后移动才能响应mouseMoveEvent
        self.setMouseTracking(True)

    def mousePressEvent(self, event: any):
        super().mousePressEvent(event)
        if event.pos().y() <= 24:
            # 发送点击信号
            self.clicked.emit()

    def mouseMoveEvent(self, event: any):
        """鼠标移动事件"""
        # 当y坐标小于24时,也就是顶部的矩形框高度
        if event.pos().y() <= 24:
            # 取消鼠标样式
            self.unsetCursor()
            event.accept()
        else:
            # 设置默认的鼠标样式并可以移动
            self.setCursor(Qt.SplitHCursor if self.orientation() == Qt.Horizontal else Qt.SplitVCursor)
            super().mouseMoveEvent(event)


# 自定义带有手柄的 QSplitter
class MySplitter(QSplitter):
    def __init__(self, parent: any = None):
        super().__init__(parent)
