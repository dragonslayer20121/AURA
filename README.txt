AURA — WINDOWS DESKTOP CUSTOMIZATION
=====================================

AURA is a local-first Windows desktop companion with a dark control center and lightweight floating overlays.

FEATURES
- Dashboard tabs: Widgets, Audio, Full screen, Profiles, and System
- Digital clock overlay
- Circular audio visualizer using Windows WASAPI loopback
- Local .LRC lyrics overlay with manual start/pause/reset sync
- Full-screen animated ambient clock/ring scene (Esc or right-click to exit)
- Built-in and user-saved widget profiles
- Saved widget toggles and visualizer sensitivity
- Audio capture error feedback in the dashboard
- Reset overlay positions
- Custom AURA logo and Windows app icon
- Windows executable build + automatic Desktop shortcut

LYRICS
AURA loads user-provided .LRC files. Choose Load .LRC, then Start sync when the song starts. Pause or reset the manual timer as needed. This is not automatic player/media synchronization yet; lyric timing depends on manually starting the timer.

FULL-SCREEN SCENE
The Full screen tab launches an animated fullscreen clock and neon ring. Press Esc or right-click to exit. This is an ambient overlay, not a wallpaper pinned behind desktop icons.

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

The build creates an isolated .venv-build environment so unrelated packages from your main Python install are not bundled. It uses PyInstaller's onedir mode. Keep the whole dist\AURA folder together; the shortcut points to the executable inside it.

OVERLAYS
- Toggle widgets from the dashboard.
- Drag overlays with the left mouse button.
- Right-click an overlay to close it.
- Overlays are frameless and transparent. They float above normal windows; they are not pinned behind desktop icons as a true wallpaper layer.

AUDIO
AURA captures the Windows output mix through WASAPI loopback. Audio is processed locally for the live visualizer; AURA does not save or upload audio. If the ring is silent, check that Windows has an active output device and read the Audio tab status message.

KNOWN LIMITATIONS
- Lyrics are local LRC files with manual timer sync; automatic media-player sync and online lyric search are not implemented.
- The full-screen scene is an animated overlay, not a wallpaper engine.
- Audio capture must be tested with the user's Windows output device.
