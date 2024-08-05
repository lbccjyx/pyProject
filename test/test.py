# -*- coding: utf-8 -*-
import base64
import unittest

class Test(unittest.TestCase):

    def test_a(self):
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.info("hello")
        logging.error("what?")
        return

    def test_b(self):
        import pyttsx3
        say = pyttsx3.init()
        say.say("这么快的反应 必然是离线的")
        say.runAndWait()

    def test_wakeup_hello(self):
        import os
        from pocketsphinx import LiveSpeech, get_model_path
        model_path = get_model_path()
        speech = LiveSpeech(
            verbose=False,
            sampling_rate=16000,
            buffer_size=2048,
            no_search=False,
            full_utt=False,
            hmm=os.path.join(model_path, 'en-us'),
            lm=os.path.join('..\\ClientWakeUp\\cfg\\TAR5567\\', '5567.lm'),
            dic=os.path.join('..\\ClientWakeUp\\cfg\\TAR5567\\', '5567.dic')
        )
        for phrase in speech:
            if str(phrase) in ["hello", "helloo", "HELLO", "HELLOO"]:
                print("已唤醒")

    def test_remote_test(self):
        import paramiko
        # 创建 SSH 客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到远程 Linux 电电脑
        ssh.connect('192.168.1.1', username='username', password='passwd')

        # 执行 shell 脚本
        stdin, stdout, stderr = ssh.exec_command('sh /home/hotgame/.local/test.sh')

        # 打印执行结果
        print(stdout.read().decode())

        # 关闭连接
        ssh.close()

    def test_pictopy(self):
        """
        将图像文件转换为py文件
        """
        write_data = []
        py_name = "memory_pic"
        picture_names = ["photo/lnp.png", "photo/mfz.png"]
        for picture_name in picture_names:
            filename = picture_name.replace('.', '_')
            open_pic = open("%s" % picture_name, 'rb')
            b64str = base64.b64encode(open_pic.read())
            open_pic.close()
            # 注意这边b64str一定要加上.decode()
            write_data.append('%s = "%s"\n' % (filename, b64str.decode()))

        f = open('%s.py' % py_name, 'w+')
        for data in write_data:
            f.write(data)
        f.close()

    def test_remote_window(selfself):
        import wmi, json
        import time

        conn = wmi.WMI(computer="192.168.1.78", user="gs", password="xxx")
        filename = r"CopyCfg_ReStart.bat \n"  # 此文件在远程服务器上
        cmd_callbat = r"cd /d D:\md2_svr\md2 && %s" % filename
        conn.Win32_Process.Create(CommandLine=cmd_callbat)  # 执行bat文件

    def test_send_socket(self):
        import socket
        HOST = '127.0.0.1'
        PORT = 65101
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        message = r"reload" + '\n'
        client_socket.send(message.encode('utf-8'))
        client_socket.send(message.encode('utf-8'))
        client_socket.close()

    def test_lock_svn(self):
        import subprocess

        file_path = r'xxx'
        remote_file_uri = 'xxx'
        lock_message = "lock"
        try:
            lock_command = ['svn', 'lock', remote_file_uri, '-m', lock_message]
            subprocess.run(lock_command, check=True)
            print(f"File {file_path} locked with message: {lock_message}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to lock file {file_path}: {e}")

    def test_unlock_svn(self):
        import subprocess
        remote_file_uri = 'xxx'
        try:
            lock_command = ['svn', 'unlock', remote_file_uri]
            subprocess.run(lock_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to lock: {e}")