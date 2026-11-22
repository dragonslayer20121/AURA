from __future__ import annotations

import math
import re
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QLinearGradient
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class OverlayBase(QWidget):
    def __init__(self, title, size=(280, 150), position=(70, 70)):
        flags = (Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
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
        self.phase += 0.025
        for i in range(64):
            angle = (2 * math.pi * i / 64) - math.pi / 2
            wave = 0.12 + self.level * self.sensitivity * (0.45 + 0.55 * math.sin(i * 0.47 + self.phase) ** 2)
            length = 8 + min(50, wave * 52)
            x1, y1 = cx + math.cos(angle) * 67, cy + math.sin(angle) * 67
            x2, y2 = cx + math.cos(angle) * (67 + length), cy + math.sin(angle) * (67 + length)
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
    """Displays user-provided LRC files with a manual playback timer."""
    def __init__(self):
        super().__init__("AURA Lyrics", (520, 150), (430, 650))
        self.lines = []
        self.elapsed = 0.0
        self.started_at = None
        self.label = QLabel("Load an .LRC file from AURA's dashboard")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font: 17px 'Segoe UI'; color: #f5edf8;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.addWidget(self.label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_line)
        self.timer.start(100)

    def load_lrc(self, path):
        parsed = []
        pattern = re.compile(r"\[(\d{2}):(\d{2})(?:\.(\d{1,3}))?\](.*)")
        with open(path, "r", encoding="utf-8-sig", errors="replace") as file:
            for raw in file:
                match = pattern.match(raw.strip())
                if match:
                    minutes, seconds, fraction, text = match.groups()
                    millis = int((fraction or "0").ljust(3, "0"))
                    parsed.append((int(minutes) * 60 + int(seconds) + millis / 1000, text.strip()))
        self.lines = sorted(parsed, key=lambda item: item[0])
        self.elapsed = 0.0
        self.started_at = None
        self.refresh_line()
        return len(self.lines)

    def start_sync(self):
        if self.lines and self.started_at is None:
            self.started_at = datetime.now().timestamp()

    def pause_sync(self):
        if self.started_at is not None:
            self.elapsed += max(0, datetime.now().timestamp() - self.started_at)
            self.started_at = None

    def reset_sync(self):
        self.elapsed = 0.0
        self.started_at = None
        self.refresh_line()

    def refresh_line(self):
        current = self.elapsed
        if self.started_at is not None:
            current += max(0, datetime.now().timestamp() - self.started_at)
        index = -1
        for i, (stamp, _) in enumerate(self.lines):
            if stamp <= current:
                index = i
            else:
                break
        if index < 0:
            self.label.setText("♪\n" + (self.lines[0][1] if self.lines else "Load an .LRC file"))
        else:
            current_text = self.lines[index][1] or "♪"
            next_text = self.lines[index + 1][1] if index + 1 < len(self.lines) else ""
            self.label.setText(current_text + ("\n\n" + next_text if next_text else ""))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(13, 8, 21, 190))
        painter.drawRoundedRect(self.rect(), 16, 16)
        painter.setPen(QPen(QColor(255, 59, 145, 110), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)


class SceneOverlay(QWidget):
    """A lightweight fullscreen ambient clock scene; Esc exits."""
    def __init__(self):
        flags = (Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
                 Qt.WindowType.WindowStaysOnTopHint)
        super().__init__(None, flags)
        self.setWindowTitle("AURA Full-screen Scene")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#090611"))
        gradient.setColorAt(0.55, QColor("#21102d"))
        gradient.setColorAt(1, QColor("#07121f"))
        painter.fillRect(self.rect(), gradient)
        self.phase += 0.025
        cx, cy = self.width() / 2, self.height() / 2
        for i in range(96):
            angle = 2 * math.pi * i / 96 + self.phase
            pulse = 18 + 34 * abs(math.sin(self.phase + i * 0.22))
            r1, r2 = min(self.width(), self.height()) * 0.16, min(self.width(), self.height()) * 0.16 + pulse
            color = QColor("#ff3b91" if i < 64 else "#ff8b48")
            color.setAlpha(190)
            painter.setPen(QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(cx + math.cos(angle) * r1), int(cy + math.sin(angle) * r1),
                             int(cx + math.cos(angle) * r2), int(cy + math.sin(angle) * r2))
        painter.setPen(QColor("#fff4fb"))
        painter.setFont(QFont("Segoe UI Light", max(32, int(self.height() * 0.09))))
        painter.drawText(self.rect().adjusted(0, -30, 0, 0), Qt.AlignmentFlag.AlignCenter,
                         datetime.now().strftime("%I:%M %p").lstrip("0"))
        painter.setPen(QColor("#d28bb6"))
        painter.setFont(QFont("Segoe UI", 16))
        painter.drawText(self.rect().adjusted(0, 100, 0, 0), Qt.AlignmentFlag.AlignCenter,
                         datetime.now().strftime("%A  •  %B %d, %Y").upper())
        painter.setPen(QColor("#8b789c"))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(self.rect().adjusted(0, 0, 0, -24), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                         "ESC OR RIGHT-CLICK TO EXIT")
