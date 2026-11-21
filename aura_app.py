from __future__ import annotations

import sys
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QCheckBox, QGridLayout,
    QSlider, QMessageBox
)
from aura.widgets import ClockOverlay, RingOverlay, LyricsOverlay
from aura.audio import AudioCapture

APP_NAME = "AURA"
BG = "#0b0911"
PANEL = "#15111d"
PANEL_ALT = "#1b1524"
ACCENT = "#ff3b91"
TEXT = "#f5edf8"
MUTED = "#a99ab5"


class Toggle(QCheckBox):
    def __init__(self, checked=False):
        super().__init__()
        self.setChecked(checked)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QCheckBox { spacing: 0; }
            QCheckBox::indicator { width: 42px; height: 24px; border-radius: 12px;
                background: #39313f; }
            QCheckBox::indicator:checked { background: #c92d78; }
            QCheckBox::indicator:unchecked { background: #39313f; }
        """)


class WidgetCard(QFrame):
    def __init__(self, title, description, toggle):
        super().__init__()
        self.setObjectName("widgetCard")
        self.setMinimumHeight(130)
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        name = QLabel(title)
        name.setObjectName("cardTitle")
        top.addWidget(name)
        top.addStretch()
        top.addWidget(toggle)
        desc = QLabel(description)
        desc.setObjectName("muted")
        desc.setWordWrap(True)
        layout.addLayout(top)
        layout.addWidget(desc)
        layout.addStretch()


class AURAWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Aayush", "AURA")
        self.setWindowTitle("AURA Control Center")
        self.resize(1040, 680)
        self.setMinimumSize(850, 560)

        self.audio = AudioCapture()
        self.clock = ClockOverlay()
        self.ring = RingOverlay(self.audio)
        self.lyrics = LyricsOverlay()

        self.clock_toggle = Toggle(self.settings.value("clock", True, type=bool))
        self.ring_toggle = Toggle(self.settings.value("ring", False, type=bool))
        self.lyrics_toggle = Toggle(self.settings.value("lyrics", False, type=bool))
        self.clock_toggle.toggled.connect(self.toggle_clock)
        self.ring_toggle.toggled.connect(self.toggle_ring)
        self.lyrics_toggle.toggled.connect(self.toggle_lyrics)

        root = QWidget()
        root.setObjectName("root")
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(22, 26, 18, 20)
        brand = QLabel("A U R A")
        brand.setObjectName("brand")
        sub = QLabel("DESKTOP EXPERIENCE")
        sub.setObjectName("smallMuted")
        side.addWidget(brand)
        side.addWidget(sub)
        side.addSpacing(32)

        self.stack = QStackedWidget()
        self.nav_buttons = []
        for i, name in enumerate(["Widgets", "Audio", "Full screen", "Profiles", "System"]):
            button = QPushButton(name)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, index=i: self.change_page(index))
            side.addWidget(button)
            self.nav_buttons.append(button)
        side.addStretch()
        status = QLabel("●  AURA READY")
        status.setObjectName("status")
        side.addWidget(status)

        outer.addWidget(sidebar)
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(34, 28, 34, 28)
        content_layout.setSpacing(18)
        self.page_title = QLabel("Widgets")
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel("Personalize the elements floating on your desktop.")
        self.page_subtitle.setObjectName("muted")
        content_layout.addWidget(self.page_title)
        content_layout.addWidget(self.page_subtitle)
        self.stack.addWidget(self.widgets_page())
        self.stack.addWidget(self.audio_page())
        self.stack.addWidget(self.fullscreen_page())
        self.stack.addWidget(self.profiles_page())
        self.stack.addWidget(self.system_page())
        content_layout.addWidget(self.stack, 1)
        outer.addWidget(content, 1)
        self.setCentralWidget(root)
        self.change_page(0)
        self.apply_style()

    def widgets_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.addWidget(WidgetCard("Digital clock", "A clean floating clock with date. Right-click it to move or close.", self.clock_toggle), 0, 0)
        grid.addWidget(WidgetCard("Ring visualizer", "A circular audio visualizer for your Windows output audio.", self.ring_toggle), 0, 1)
        grid.addWidget(WidgetCard("Lyrics panel", "A lightweight placeholder for future synced lyrics support.", self.lyrics_toggle), 1, 0)
        layout.addLayout(grid)
        layout.addStretch()
        note = QLabel("Overlays are transparent, movable, and stay above normal windows.")
        note.setObjectName("smallMuted")
        layout.addWidget(note)
        return page

    def audio_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("sectionCard")
        c = QVBoxLayout(card)
        title = QLabel("Audio visualizer")
        title.setObjectName("cardTitle")
        info = QLabel("AURA uses Windows WASAPI loopback to listen to the audio currently playing on your output device. Audio is processed locally and is not recorded or sent anywhere.")
        info.setObjectName("muted")
        info.setWordWrap(True)
        c.addWidget(title)
        c.addWidget(info)
        c.addSpacing(10)
        c.addWidget(QLabel("Visualizer sensitivity"))
        sensitivity = QSlider(Qt.Orientation.Horizontal)
        sensitivity.setRange(50, 250)
        sensitivity.setValue(100)
        sensitivity.valueChanged.connect(lambda v: self.ring.set_sensitivity(v / 100))
        c.addWidget(sensitivity)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def fullscreen_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("sectionCard")
        c = QVBoxLayout(card)
        c.addWidget(QLabel("Full screen experience"))
        c.addWidget(QLabel("Full-screen wallpaper and immersive scene controls will be added in a later build."))
        layout.addWidget(card)
        layout.addStretch()
        return page

    def profiles_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("sectionCard")
        c = QVBoxLayout(card)
        c.addWidget(QLabel("Quick profiles"))
        for name, states in [
            ("Minimal", (True, False, False)),
            ("Audio mode", (True, True, False)),
            ("All widgets", (True, True, True)),
        ]:
            btn = QPushButton(name)
            btn.setObjectName("actionButton")
            btn.clicked.connect(lambda checked=False, s=states: self.apply_profile(s))
            c.addWidget(btn)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def system_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("sectionCard")
        c = QVBoxLayout(card)
        c.addWidget(QLabel("System"))
        c.addWidget(QLabel("AURA is a lightweight desktop companion. Use the Quit AURA button below to close all overlays and stop audio capture."))
        quit_btn = QPushButton("Quit AURA")
        quit_btn.setObjectName("dangerButton")
        quit_btn.clicked.connect(self.close)
        c.addWidget(quit_btn)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def change_page(self, index):
        self.stack.setCurrentIndex(index)
        self.page_title.setText(["Widgets", "Audio", "Full screen", "Profiles", "System"][index])
        self.page_subtitle.setText([
            "Personalize the elements floating on your desktop.",
            "Configure live audio visualization.",
            "Immersive desktop experiences.",
            "Switch your setup with one click.",
            "Manage AURA and its runtime."
        ][index])
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

    def toggle_clock(self, on):
        self.settings.setValue("clock", on)
        self.clock.setVisible(on)

    def toggle_ring(self, on):
        self.settings.setValue("ring", on)
        self.ring.setVisible(on)
        if on:
            self.audio.start()
        elif not self.lyrics_toggle.isChecked():
            self.audio.stop()

    def toggle_lyrics(self, on):
        self.settings.setValue("lyrics", on)
        self.lyrics.setVisible(on)

    def apply_profile(self, states):
        self.clock_toggle.setChecked(states[0])
        self.ring_toggle.setChecked(states[1])
        self.lyrics_toggle.setChecked(states[2])

    def apply_style(self):
        self.setStyleSheet("""
            QWidget#root { background: #0b0911; color: #f5edf8; font-family: "Segoe UI"; }
            QFrame#sidebar { background: #100d17; border-right: 1px solid #241b2c; }
            QLabel#brand { color: #ff3b91; font-size: 25px; font-weight: 700; letter-spacing: 4px; }
            QLabel#smallMuted { color: #756982; font-size: 10px; }
            QLabel#status { color: #9f7a9b; font-size: 11px; }
            QLabel#pageTitle { font-size: 28px; font-weight: 600; color: #f8f1fa; }
            QLabel#muted { color: #a99ab5; font-size: 12px; }
            QLabel#cardTitle { font-size: 16px; font-weight: 600; color: #f5edf8; }
            QPushButton#navButton { text-align: left; padding: 12px 14px; border: 0; border-radius: 9px; color: #a99ab5; font-size: 14px; }
            QPushButton#navButton:checked { background: #291729; color: #ff68ad; }
            QPushButton#navButton:hover { background: #211827; }
            QFrame#widgetCard, QFrame#sectionCard { background: #15111d; border: 1px solid #292031; border-radius: 14px; }
            QPushButton#actionButton { background: #211827; border: 1px solid #38253d; border-radius: 8px; padding: 12px; text-align: left; color: #f5edf8; }
            QPushButton#actionButton:hover { border-color: #ff3b91; }
            QPushButton#dangerButton { background: #351723; border: 1px solid #74304c; border-radius: 8px; padding: 10px; color: #ff9ac6; }
            QSlider::groove:horizontal { height: 5px; background: #35283c; border-radius: 2px; }
            QSlider::handle:horizontal { width: 14px; margin: -5px 0; border-radius: 7px; background: #ff3b91; }
        """)

    def closeEvent(self, event):
        self.audio.stop()
        for overlay in (self.clock, self.ring, self.lyrics):
            overlay.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = AURAWindow()
    window.show()
    window.clock.setVisible(window.clock_toggle.isChecked())
    window.ring.setVisible(window.ring_toggle.isChecked())
    window.lyrics.setVisible(window.lyrics_toggle.isChecked())
    if window.ring_toggle.isChecked():
        window.audio.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
