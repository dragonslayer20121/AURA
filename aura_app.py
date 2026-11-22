from __future__ import annotations

import json
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QCheckBox, QGridLayout,
    QSlider, QMessageBox, QFileDialog, QInputDialog, QComboBox
)
from aura.widgets import ClockOverlay, RingOverlay, LyricsOverlay, SceneOverlay
from aura.audio import AudioCapture

APP_NAME = "AURA"
ACCENT = "#ff3b91"


def app_asset(name):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return str(base / "assets" / name)


class Toggle(QCheckBox):
    def __init__(self, checked=False):
        super().__init__()
        self.setChecked(checked)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QCheckBox::indicator { width: 42px; height: 24px; border-radius: 12px; background: #39313f; }
            QCheckBox::indicator:checked { background: #c92d78; }
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
        self.setWindowIcon(QIcon(app_asset("aura.ico")))
        self.resize(1040, 680)
        self.setMinimumSize(850, 560)

        self.audio = AudioCapture()
        self.audio.capture_error.connect(self.audio_error)
        self.clock = ClockOverlay()
        self.ring = RingOverlay(self.audio)
        self.lyrics = LyricsOverlay()
        self.scene = SceneOverlay()

        self.clock_toggle = Toggle(self.settings.value("clock", True, type=bool))
        self.ring_toggle = Toggle(self.settings.value("ring", False, type=bool))
        self.lyrics_toggle = Toggle(self.settings.value("lyrics", False, type=bool))
        self.clock_toggle.toggled.connect(self.toggle_clock)
        self.ring_toggle.toggled.connect(self.toggle_ring)
        self.lyrics_toggle.toggled.connect(self.toggle_lyrics)
        self.sensitivity_value = int(self.settings.value("sensitivity", 100))
        self.ring.set_sensitivity(self.sensitivity_value / 100)

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
        self.status = QLabel("●  AURA READY")
        self.status.setObjectName("status")
        side.addWidget(self.status)

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
        outer.addWidget(sidebar)
        outer.addWidget(content, 1)
        self.setCentralWidget(root)
        self.change_page(0)
        self.apply_style()

    def widgets_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.addWidget(WidgetCard("Digital clock", "Floating clock and date. Drag with left mouse; right-click to close.", self.clock_toggle), 0, 0)
        grid.addWidget(WidgetCard("Ring visualizer", "Live circular visualizer for Windows output audio.", self.ring_toggle), 0, 1)
        grid.addWidget(WidgetCard("LRC lyrics", "Load a local .lrc lyrics file and manually start/pause sync.", self.lyrics_toggle), 1, 0)
        layout.addLayout(grid)
        controls = QFrame()
        controls.setObjectName("sectionCard")
        row = QHBoxLayout(controls)
        load = QPushButton("Load .LRC")
        load.setObjectName("actionButton")
        load.clicked.connect(self.load_lyrics)
        start = QPushButton("Start sync")
        start.setObjectName("actionButton")
        start.clicked.connect(self.lyrics.start_sync)
        pause = QPushButton("Pause")
        pause.setObjectName("actionButton")
        pause.clicked.connect(self.lyrics.pause_sync)
        reset = QPushButton("Reset")
        reset.setObjectName("actionButton")
        reset.clicked.connect(self.lyrics.reset_sync)
        for btn in (load, start, pause, reset):
            row.addWidget(btn)
        layout.addWidget(controls)
        layout.addStretch()
        note = QLabel("Overlays float above normal windows. Full-screen scene exits with Esc or right-click.")
        note.setObjectName("smallMuted")
        layout.addWidget(note)
        return page

    def load_lyrics(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load synced lyrics", "", "LRC lyrics (*.lrc);;Text files (*.txt)")
        if not path:
            return
        try:
            count = self.lyrics.load_lrc(path)
            if count == 0:
                QMessageBox.warning(self, "No timed lyrics", "No [mm:ss] timestamps were found in this file.")
                return
            self.lyrics_toggle.setChecked(True)
            QMessageBox.information(self, "Lyrics loaded", f"Loaded {count} timed lyric lines. Start sync when the song begins.")
        except OSError as exc:
            QMessageBox.critical(self, "Could not load lyrics", str(exc))

    def audio_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("sectionCard")
        c = QVBoxLayout(card)
        title = QLabel("Audio visualizer")
        title.setObjectName("cardTitle")
        info = QLabel("AURA listens to your Windows output mix using WASAPI loopback. Audio is processed locally and is not saved or uploaded.")
        info.setObjectName("muted")
        info.setWordWrap(True)
        c.addWidget(title)
        c.addWidget(info)
        self.audio_status = QLabel("Audio capture starts when the ring is enabled.")
        self.audio_status.setObjectName("muted")
        c.addWidget(self.audio_status)
        c.addSpacing(10)
        c.addWidget(QLabel("Visualizer sensitivity"))
        sensitivity = QSlider(Qt.Orientation.Horizontal)
        sensitivity.setRange(50, 250)
        sensitivity.setValue(self.sensitivity_value)
        sensitivity.valueChanged.connect(self.set_sensitivity)
        c.addWidget(sensitivity)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def set_sensitivity(self, value):
        self.sensitivity_value = value
        self.ring.set_sensitivity(value / 100)
        self.settings.setValue("sensitivity", value)

    def audio_error(self, message):
        self.status.setText("●  AUDIO ERROR")
        if hasattr(self, "audio_status"):
            self.audio_status.setText("Audio capture failed: " + message)
        self.audio_status.setStyleSheet("color: #ff9ac6;")

    def fullscreen_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("sectionCard")
        c = QVBoxLayout(card)
        c.addWidget(QLabel("Full-screen ambient scene"))
        desc = QLabel("A fullscreen animated clock and neon ring scene. Press Esc or right-click to exit.")
        desc.setObjectName("muted")
        desc.setWordWrap(True)
        c.addWidget(desc)
        launch = QPushButton("Launch full-screen scene")
        launch.setObjectName("actionButton")
        launch.clicked.connect(self.launch_scene)
        c.addWidget(launch)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def launch_scene(self):
        self.scene.showFullScreen()
        self.scene.raise_()
        self.scene.activateWindow()

    def profiles_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("sectionCard")
        c = QVBoxLayout(card)
        c.addWidget(QLabel("Built-in profiles"))
        for name, states in [
            ("Minimal", (True, False, False)),
            ("Audio mode", (True, True, False)),
            ("All widgets", (True, True, True)),
        ]:
            btn = QPushButton(name)
            btn.setObjectName("actionButton")
            btn.clicked.connect(lambda checked=False, s=states: self.apply_profile(s))
            c.addWidget(btn)
        c.addSpacing(12)
        c.addWidget(QLabel("Saved profiles"))
        self.profile_combo = QComboBox()
        self.refresh_profiles()
        c.addWidget(self.profile_combo)
        buttons = QHBoxLayout()
        save = QPushButton("Save current")
        save.setObjectName("actionButton")
        save.clicked.connect(self.save_profile)
        load = QPushButton("Load selected")
        load.setObjectName("actionButton")
        load.clicked.connect(self.load_profile)
        delete = QPushButton("Delete selected")
        delete.setObjectName("actionButton")
        delete.clicked.connect(self.delete_profile)
        for btn in (save, load, delete):
            buttons.addWidget(btn)
        c.addLayout(buttons)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def profile_data(self):
        try:
            return json.loads(self.settings.value("custom_profiles", "{}"))
        except (TypeError, json.JSONDecodeError):
            return {}

    def refresh_profiles(self):
        if not hasattr(self, "profile_combo"):
            return
        self.profile_combo.clear()
        self.profile_combo.addItems(sorted(self.profile_data().keys()))

    def save_profile(self):
        name, ok = QInputDialog.getText(self, "Save profile", "Profile name:")
        name = name.strip()
        if not ok or not name:
            return
        data = self.profile_data()
        data[name] = {
            "clock": self.clock_toggle.isChecked(),
            "ring": self.ring_toggle.isChecked(),
            "lyrics": self.lyrics_toggle.isChecked(),
            "sensitivity": self.sensitivity_value,
        }
        self.settings.setValue("custom_profiles", json.dumps(data))
        self.refresh_profiles()
        self.profile_combo.setCurrentText(name)

    def load_profile(self):
        name = self.profile_combo.currentText()
        profile = self.profile_data().get(name)
        if not profile:
            return
        self.apply_profile((profile.get("clock", True), profile.get("ring", False), profile.get("lyrics", False)))
        self.set_sensitivity(int(profile.get("sensitivity", 100)))

    def delete_profile(self):
        name = self.profile_combo.currentText()
        if not name:
            return
        data = self.profile_data()
        data.pop(name, None)
        self.settings.setValue("custom_profiles", json.dumps(data))
        self.refresh_profiles()

    def system_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("sectionCard")
        c = QVBoxLayout(card)
        c.addWidget(QLabel("System"))
        c.addWidget(QLabel("AURA runs locally. Quit closes all overlays and stops audio capture."))
        reset = QPushButton("Reset overlay positions")
        reset.setObjectName("actionButton")
        reset.clicked.connect(self.reset_positions)
        c.addWidget(reset)
        quit_btn = QPushButton("Quit AURA")
        quit_btn.setObjectName("dangerButton")
        quit_btn.clicked.connect(self.close)
        c.addWidget(quit_btn)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def reset_positions(self):
        self.clock.move(70, 70)
        self.ring.move(80, 300)
        self.lyrics.move(430, 650)

    def change_page(self, index):
        self.stack.setCurrentIndex(index)
        self.page_title.setText(["Widgets", "Audio", "Full screen", "Profiles", "System"][index])
        self.page_subtitle.setText([
            "Manage your floating desktop widgets.",
            "Configure live audio visualization.",
            "Launch the immersive ambient scene.",
            "Save and switch widget setups.",
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
            self.status.setText("●  AURA AUDIO ACTIVE")
            self.audio.start()
            if hasattr(self, "audio_status"):
                self.audio_status.setText("Starting WASAPI loopback capture…")
        elif not self.lyrics_toggle.isChecked():
            self.audio.stop()
            self.status.setText("●  AURA READY")
            if hasattr(self, "audio_status"):
                self.audio_status.setText("Audio capture stopped.")

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
        for overlay in (self.clock, self.ring, self.lyrics, self.scene):
            overlay.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon(app_asset("aura.ico")))
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
