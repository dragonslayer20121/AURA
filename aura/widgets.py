from __future__ import annotations

import math
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class OverlayBase(QWidget):
    def __init__(self, title, size=(280, 150), position=(70, 70)):
        flags = (Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.Tool |
                 Qt.WindowType.WindowStaysOnTopHint)
        super().__init__(None, flags)
        self.setWindowTitle(title)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.resize(*size)
        self.move(*position)
        self.drag_offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.close()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_offset = None


class ClockOverlay(OverlayBase):
    def __init__(self):
        super().__init__("AURA Clock", (350, 140), (70, 70))
        self.setStyleSheet("color: #f7f1ff;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 16, 22, 16)
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font: 52px 'Segoe UI Light'; color: #fff4fb;")
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("font: 11px 'Segoe UI'; color: #e28bb7; letter-spacing: 2px;")
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(500)
        self.update_clock()

    def update_clock(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M %p").lstrip("0"))
        self.date_label.setText(now.strftime("%A  •  %B %d").upper())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(13, 8, 21, 165))
        painter.drawRoundedRect(self.rect(), 18, 18)
        painter.setPen(QPen(QColor(255, 59, 145, 130), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 18, 18)


class RingOverlay(OverlayBase):
    def __init__(self, audio):
        super().__init__("AURA Audio Ring", (250, 250), (80, 300))
        self.audio = audio
        self.level = 0.0
        self.sensitivity = 1.0
        self.phase = 0.0
        self.audio.level_changed.connect(self.set_level)
        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(33)

    def set_level(self, level):
        self.level = max(0.0, min(1.0, level))

    def set_sensitivity(self, value):
        self.sensitivity = value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(10, 7, 17, 105))
        painter.drawEllipse(self.rect().adjusted(12, 12, -12, -12))
        cx, cy = self.width() / 2, self.height() / 2
        base = 67
        bars = 64
        self.phase += 0.025
        for i in range(bars):
            angle = (2 * math.pi * i / bars) - math.pi / 2
            wave = 0.12 + self.level * self.sensitivity * (0.45 + 0.55 * math.sin(i * 0.47 + self.phase) ** 2)
            length = 8 + min(50, wave * 52)
            r1, r2 = base, base + length
            x1, y1 = cx + math.cos(angle) * r1, cy + math.sin(angle) * r1
            x2, y2 = cx + math.cos(angle) * r2, cy + math.sin(angle) * r2
            color = QColor("#ff3b91") if i < 46 else QColor("#ff8b48")
            color.setAlpha(210)
            painter.setPen(QPen(color, 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(24, 13, 32, 225))
        painter.drawEllipse(int(cx - 58), int(cy - 58), 116, 116)
        painter.setPen(QColor("#ff9ac6"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "A U R A")


class LyricsOverlay(OverlayBase):
    def __init__(self):
        super().__init__("AURA Lyrics", (420, 110), (430, 650))
        self.label = QLabel("LYRICS\nComing soon")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font: 16px 'Segoe UI'; color: #f5edf8;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.addWidget(self.label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(13, 8, 21, 180))
        painter.drawRoundedRect(self.rect(), 16, 16)
        painter.setPen(QPen(QColor(255, 59, 145, 90), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)
