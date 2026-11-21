@echo off
setlocal
cd /d "%~dp0"
echo [AURA] Installing runtime and build dependencies...
py -m pip install -r requirements.txt
if errorlevel 1 goto failed
py -m pip install -r requirements-build.txt
if errorlevel 1 goto failed

echo [AURA] Creating app icon...
py tools\generate_icon.py
if errorlevel 1 goto failed

echo [AURA] Packaging AURA as a Windows desktop app...
py -m PyInstaller --noconfirm --clean --windowed --onedir --name AURA --icon assets\aura.ico --add-data "assets;assets" aura_app.py
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
