#!/usr/bin/env python

from PySide6.QtGui import QColor
from PySide6.QtCore import QPropertyAnimation, Property as pyqtProperty
from PySide6.QtWidgets import QGraphicsDropShadowEffect


class AnimationShadowEffect(QGraphicsDropShadowEffect):
    def __init__(self, color: QColor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setColor(color)
        self.setOffset(0, 0)
        self.setBlurRadius(0)
        self._radius = 0
        self.animation = QPropertyAnimation(self)
        self.animation.setTargetObject(self)
        self.animation.setDuration(2000)  # 一次循环时间
        self.animation.setLoopCount(-1)  # 永久循环
        self.animation.setPropertyName(b"radius")
        # 插入值
        self.animation.setKeyValueAt(0, 1)
        self.animation.setKeyValueAt(0.5, 30)
        self.animation.setKeyValueAt(1, 1)

    def start(self):
        self.animation.start()

    def stop(self, r: int = 0):
        # 停止动画并修改半径值
        self.animation.stop()
        self.radius = r

    @pyqtProperty(int)
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, r: int):
        self._radius = r
        self.setBlurRadius(r)
