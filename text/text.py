# -*- coding: utf-8 -*-
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
            lm=os.path.join('..\\ClientDemo\\cfg\\TAR5567\\', '5567.lm'),
            dic=os.path.join('..\\ClientDemo\\cfg\\TAR5567\\', '5567.dic')
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
