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