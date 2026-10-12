@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\launch_offline_mirror.ps1"
if errorlevel 1 pause
