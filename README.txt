PROJECT AURA — DESKTOP CONTROL CENTER
======================================

A lightweight Windows desktop companion built with Python and PyQt6.

CURRENT FEATURES
- Dark control-center dashboard with Widgets, Audio, Full screen, Profiles, and System pages
- Digital clock overlay (toggle, drag to move, right-click to close)
- Circular audio ring overlay using Windows WASAPI loopback
- Lyrics placeholder overlay
- Quick profiles: Minimal, Audio mode, All widgets
- Audio is processed locally; AURA does not record or upload it

IMPORTANT WINDOWS NOTE
The overlays are transparent and stay above regular windows. Windows does not provide a simple portable API to pin a normal app window behind desktop icons, so this version is not a true wallpaper-layer widget.

INSTALL
1. Install Python 3.10 or newer from python.org. During setup, enable "Add Python to PATH".
2. Open the AURA folder in File Explorer.
3. Click the address bar, type cmd, and press Enter.
4. Run:
   py -m pip install -r requirements.txt

RUN
- Double-click Start_AURA.vbs for a background launch.
- Or double-click Run_AURA.bat to see errors in a terminal.

AUDIO
The ring captures the current Windows output audio with WASAPI loopback.
If audio capture is unavailable, check that Windows has an active output device and that the required packages installed successfully.

CONTROLS
- Toggle overlays from the Widgets page.
- Drag an overlay with the left mouse button.
- Right-click an overlay to close it.
- Quit AURA from the System page.

NEXT
- Lyrics provider and media integration
- Full-screen experience
- More overlay themes and saved positions

The original AURA.py prototype is preserved in the repository.
