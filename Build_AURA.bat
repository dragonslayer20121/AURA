@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv-build\Scripts\python.exe" (
  echo [AURA] Creating an isolated build environment...
  py -m venv .venv-build
  if errorlevel 1 goto failed
)

echo [AURA] Installing AURA and build tools into the isolated environment...
".venv-build\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv-build\Scripts\python.exe" -m pip install -r requirements.txt -r requirements-build.txt
if errorlevel 1 goto failed

echo [AURA] Creating app icon...
".venv-build\Scripts\python.exe" tools\generate_icon.py
if errorlevel 1 goto failed

echo [AURA] Packaging AURA as a Windows desktop app...
".venv-build\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --onedir --name AURA --icon assets\aura.ico --add-data "assets;assets" aura_app.py
if errorlevel 1 goto failed

echo [AURA] Creating desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -File ".\Create_Desktop_Shortcut.ps1"
if errorlevel 1 goto failed

echo.
echo AURA is ready: dist\AURA\AURA.exe
echo Desktop shortcut created.
pause
exit /b 0

:failed
echo.
echo Build failed. Scroll up and copy the error if you need help.
pause
exit /b 1
