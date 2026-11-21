@echo off
setlocal
cd /d "%~dp0"
if exist "dist\AURA\AURA.exe" (
  start "" "dist\AURA\AURA.exe"
  exit /b 0
)
py aura_app.py
if errorlevel 1 pause
