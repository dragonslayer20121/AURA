AURA — WINDOWS DESKTOP CUSTOMIZATION
=====================================

AURA is a local-first Windows desktop companion with a dark control center and lightweight floating overlays.

WHAT'S INCLUDED
- Dashboard tabs: Widgets, Audio, Full screen, Profiles, and System
- Digital clock overlay
- Circular ring visualizer using Windows WASAPI loopback
- Lyrics placeholder overlay
- Saved widget toggles and quick profiles
- Custom AURA logo and Windows app icon
- Windows executable build + automatic Desktop shortcut

FIRST RUN (SOURCE)
1. Install Python 3.10+ for Windows from https://www.python.org/downloads/
   During installation, enable "Add Python to PATH".
2. Open the AURA repository folder in File Explorer.
3. Click the address bar, type cmd, and press Enter.
4. Run:
   py -m pip install --upgrade pip
   py -m pip install -r requirements.txt
5. Start:
   py aura_app.py

Double-click Start_AURA.vbs for a background launch.
Run_AURA.bat opens a console so errors can be read.

BUILD A WINDOWS DESKTOP APP
1. Double-click Build_AURA.bat from the AURA folder.
2. It installs build-only tools, creates the icon, packages AURA, and creates a Desktop shortcut.
3. The executable is dist\AURA\AURA.exe.
4. The shortcut is named AURA on your Windows Desktop.

The build uses PyInstaller's onedir mode. This avoids the extra unpacking step of one-file mode and is generally easier to troubleshoot for Qt apps. Keep the whole dist\AURA folder together; the shortcut points to the executable inside it.

OVERLAYS
- Toggle widgets from the dashboard.
- Drag overlays with the left mouse button.
- Right-click an overlay to close it.
- Overlays are frameless and transparent. They float above normal windows; they are not pinned behind desktop icons as a true wallpaper layer.

AUDIO
AURA captures the Windows output mix through WASAPI loopback. Audio is processed locally for the live visualizer; AURA does not save or upload audio. If the ring is silent, check that Windows has an active output device and review the console for capture errors.

DESIGN AND IMPLEMENTATION REFERENCES
- Qt documentation: translucent windows require a frameless top-level window on Windows:
  https://doc.qt.io/qt-6/qwidget.html
- Qt documentation: Qt's non-native ("alien") widgets can improve painting/resizing and reduce flicker:
  https://doc.qt.io/qt-6/qwidget.html
- PyAudioWPatch project: use the WASAPI loopback analogue of the active output device:
  https://github.com/s0d3s/PyAudioWPatch
- Microsoft WASAPI loopback overview:
  https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording
- PyInstaller documentation: windowed builds and executable icon options:
  https://pyinstaller.org/en/latest/usage.html

These references informed the implementation choices: Qt-native translucent frameless overlays, audio capture on a separate thread, local audio processing, and a bundled executable with a Windows icon.

KNOWN LIMITATIONS
- Lyrics are a visual placeholder; synced lyrics and media-provider integration are not implemented.
- Full-screen wallpaper scenes are planned, not active yet.
- Audio capture and packaged launch still need testing on the target Windows machine and selected output device.
- AURA is not a true desktop wallpaper-layer widget.
