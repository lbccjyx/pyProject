import time
from PySide6.QtWidgets import QWidget, QCompleter, QMessageBox, QLineEdit, QFileDialog, QPushButton
from PySide6.QtCore import Qt, QTimer, QSize, QCoreApplication
from PySide6.QtGui import QTextCursor, QKeyEvent, QFont
from ui_form import Ui_Widget
from CommonClient import common as myCommon
from CommonClient import AnimationShadowEffect
import paramiko
import logging
import re
import config as myConfig
import socket


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


class BaseButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(QSize(120, 80))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)
        self.setAutoFillBackground(False)
        self.clicked.connect(self.on_base_click)
        self.timerInterval = 10000

    def on_base_click(self):
        self.on_forbidden()
        self.on_click()
        QTimer.singleShot(self.timerInterval, self.on_timer)  # 10秒后执行函数

    def on_timer(self):
        pass

    def on_click(self):
        pass

    def on_forbidden(self):
        pass


class LinuxButton(BaseButton):
    def __init__(self, btn_name: str, parent=None, linux_ssh_channel=None):
        super().__init__(parent)
        # 设置 Linux 按钮的样式和其他属性
        self.setStyleSheet(f"background: url(\"photo/{btn_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")
        self.setText(QCoreApplication.translate("Widget", f"Linux_GS_{btn_name}", None))
        self.linux_ssh_channel = linux_ssh_channel
        self.button_name = btn_name

    def on_forbidden(self):
        self.setEnabled(False)
        self.setStyleSheet(f"background: url(\"photo/dark_{self.button_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")

    def on_click(self):
        # 重启的时候会删除老旧的res.zip包、但是会保留一个 如果想保留多个 可以使用 tail -n +3
        command = f"cd $HOME/gs_svr/*{self.button_name}; ls -t *res.zip | tail -n +2 | xargs rm; ./RestartSvr.sh"
        self.linux_ssh_channel.send(command + '\n')
        if self.linux_ssh_channel.recv_ready():
            output = self.linux_ssh_channel.recv(1024).decode()
            logging.info(output)

    def on_timer(self):
        logging.info("检测是否成功中")
        command = f"ps -aux | grep -i mmoserver | grep {self.button_name} | wc -l"
        self.linux_ssh_channel.send(command + '\n')
        if self.linux_ssh_channel.recv_ready():
            output = self.linux_ssh_channel.recv(1024).decode()
            logging.info(output)
            if '1' in output:
                logging.info(f"检测到GS_{self.button_name}进程重启成功")
            else:
                logging.info("检测失败")
        self.setEnabled(True)  # 禁用按钮
        self.setStyleSheet(f"background: url(\"photo/{self.button_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")


class WinButton(BaseButton):
    def __init__(self, btn_name: str, parent=None, client_socket=None):
        super().__init__(parent)
        # 设置 Windows 按钮的样式和其他属性
        self.setStyleSheet(f"background: url(\"photo/{btn_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")
        self.setText(QCoreApplication.translate("Widget", f"WIN_GS_{btn_name}", None))
        self.client_socket = client_socket
        self.button_name = btn_name

    def on_forbidden(self):
        self.setEnabled(False)
        self.setStyleSheet(f"background: url(\"photo/dark_{self.button_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")

    def on_click(self):
        # window 的处理方法
        strCommand = self.button_name + '\n'
        self.client_socket.send(strCommand.encode('utf-8'))

    def on_timer(self):
        logging.info(f"成功重启{self.button_name}")
        self.setEnabled(True)
        self.setStyleSheet(f"background: url(\"photo/{self.button_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")


class LinuxBsButton(BaseButton):
    def __init__(self, btn_name: str, parent=None, linux_ssh_channel=None):
        super().__init__(parent)
        # 设置 Linux BS 按钮的样式和其他属性
        self.setStyleSheet(f"background: url(\"photo/{btn_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")
        self.setText(QCoreApplication.translate("Widget", f"BS{btn_name}", None))
        self.linux_ssh_channel = linux_ssh_channel
        self.button_name = btn_name

    def on_forbidden(self):
        self.setEnabled(False)
        self.setStyleSheet(f"background: url(\"photo/dark_{self.button_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")

    def on_click(self):
        # 重启的时候会删除老旧的res.zip包、但是会保留一个 如果想保留多个 可以使用 tail -n +3
        logging.info(f"BS_{self.button_name} on_click suc")
        command = f"cd $HOME/xBattleServer/xBattleServer*{self.button_name}; ./start.sh"
        self.linux_ssh_channel.send(command + '\n')
        if self.linux_ssh_channel.recv_ready():
            output = self.linux_ssh_channel.recv(1024).decode()
            logging.info(output)

    def on_timer(self):
        logging.info("检测是否成功中")
        command = f"ps -aux | grep -i battle | grep {self.button_name} | wc -l"
        self.linux_ssh_channel.send(command + '\n')
        if self.linux_ssh_channel.recv_ready():
            output = self.linux_ssh_channel.recv(1024).decode()
            logging.info(output)
            if '1' in output:
                logging.info(f"检测到BS_{self.button_name}进程重启成功")
            else:
                logging.info("检测失败")

        self.setEnabled(True)
        self.setStyleSheet(f"background: url(\"photo/{self.button_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")


class LinuxUploadButton(BaseButton):
    def __init__(self, btn_name: str, parent=None, linux_ssh_channel=None,  linux_ssh=None):
        super().__init__(parent)
        # 设置 Linux Upload 按钮的样式和其他属性
        self.new_path = None
        self.setStyleSheet(f"background: url(\"photo/{btn_name}.png\");\n"
                           "color: black;\n"
                           "border-radius: 20;")
        self.setText(QCoreApplication.translate("Widget", f"LUA{btn_name}", None))
        self.linux_ssh_channel = linux_ssh_channel
        self.linux_ssh = linux_ssh
        self.button_name = btn_name

    def on_forbidden(self):
        pass

    def on_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "选择 Lua 文件", "", "Lua Files (*.lua)", options=options)
        if file_name:
            logging.info(f"选择的 Lua 文件是：{file_name}")
            sftp = self.linux_ssh.open_sftp()
            command = f"cd $HOME/gs_svr/*{self.button_name}/*res; pwd"
            stdin, stdout, stderr = self.linux_ssh.exec_command(command)
            target_path = stdout.read().decode()
            self.new_path = get_lua_path_and_append(file_name, target_path)
            sftp.put(file_name, self.new_path)
            logging.info(f"原路径：{file_name} 目标路径:{self.new_path} 上传成功")
            sftp.close()

    def on_timer(self):
        pass


class AWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ColorMode = myCommon.DarkNormalMode(self)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.__init_Member_variables()
        self.__init_Add_UI()
        self.__begin_show()

    def __init_Member_variables(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("__init_Member_variables")
        self.classConfig = myConfig.myConfig()
        self.aniblue = AnimationShadowEffect.AnimationShadowEffect(Qt.blue)
        self.aniblue.start()
        self.ui.edit_cmd_linux.setGraphicsEffect(self.aniblue)

        self.ui.pushButton_Mode.clicked.connect(self.on_Mode_changed)
        self.ui.edit_cmd_linux.textChanged.connect(self.on_text_changed)

        # logging打印出来的log 显示在self.ui.textBrowser上
        myCommon.LoggingHandler(self.on_log_changed)
        # 创建 SSH 客户端
        self.linux_ssh = paramiko.SSHClient()
        self.linux_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到远程 Linux 电电脑
        self.linux_ssh.connect(self.classConfig.linux_id, username=self.classConfig.linux_username, password=self.classConfig.linux_password)
        logging.info(f"connect to Linux {self.classConfig.linux_id} !!!")

        self.linux_ssh_channel = self.linux_ssh.invoke_shell()
        time.sleep(1)
        if self.linux_ssh_channel.recv_ready():
            output = self.linux_ssh_channel.recv(1024).decode()
            logging.info(output)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.classConfig.win_HOST, self.classConfig.win_PORT))
        logging.info(f"connect to window ip {self.classConfig.win_HOST} port {self.classConfig.win_PORT} !!!")

    def __init_Add_UI(self):
        for btn_name in self.classConfig.linux_gs_app:
            btn = LinuxButton(btn_name, self, self.linux_ssh_channel)
            self.ui.gs_restart_layout.insertWidget(0, btn)

        for btn_name in self.classConfig.win_gs_app:
            btn = WinButton(btn_name, self)
            self.ui.gs_restart_layout.insertWidget(0, btn)

        for btn_name in self.classConfig.linux_bs_app:
            btn = LinuxBsButton(btn_name, self, self.linux_ssh_channel)
            self.ui.bs_restart_layout.insertWidget(0, btn)

        for btn_name in self.classConfig.linux_lua_app:
            btn = LinuxUploadButton(btn_name, self, self.linux_ssh_channel, self.linux_ssh)
            self.ui.upload_lua_layout.insertWidget(0, btn)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出确认', '确定要退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.linux_ssh_channel.close()
            self.linux_ssh.close()
            self.client_socket.close()
            event.accept()
        else:
            event.ignore()

    def on_log_changed(self, msg: str):
        self.ui.textBrowser.moveCursor(QTextCursor.End)
        self.ui.textBrowser.append(msg)
        self.ui.textBrowser.moveCursor(QTextCursor.End)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if isinstance(self.focusWidget(), QLineEdit):
                self.onConfirm()
        else:
            super().keyPressEvent(event)

    def onConfirm(self):
        if len(self.ui.edit_cmd_linux.text()) > 0:
            self.linux_ssh_channel.send(self.ui.edit_cmd_linux.text() + '\n')
            time.sleep(1)
            if self.linux_ssh_channel.recv_ready():
                output = self.linux_ssh_channel.recv(1024).decode()
                logging.info(output)

            self.TargetLanIPHistory.add(self.ui.edit_cmd_linux.text())
            completer = QCompleter(self.TargetLanIPHistory, self.ui.edit_cmd_linux)
            self.ui.edit_cmd_linux.setCompleter(completer)
            self.ui.edit_cmd_linux.clear()

    def __begin_show(self):
        logging.info("__begin_show")
        # 缓存
        self.TargetLanIPHistory = set(["ls -lrt gs_svr/dl_jp_mfz/*res/lua/jp/dl.lua",
                                       "pgrep MMOServer_lnp.e",
                                       "pgrep MMOServer_mfz.e",
                                       "ps -aux | grep MMOServer_mfz | awk 'NR==1{print $9}'",
                                       "ps -aux | grep MMOServer_lnp | awk 'NR==1{print $9}'"])
        completer = QCompleter(self.TargetLanIPHistory, self.ui.edit_cmd_linux)
        self.ui.edit_cmd_linux.setCompleter(completer)

    def on_text_changed(self):
        if "rm" in self.ui.edit_cmd_linux.text():
            self.ui.edit_cmd_linux.clear()

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
