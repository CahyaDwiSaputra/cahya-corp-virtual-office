@echo off
title CAHYA CORP - 3D Virtual Workspace
cd /d "%USERPROFILE%\virtual-office"
echo ======================================================
echo    CAHYA CORP - 3D Autonomous Multi-Agent Workspace
echo ======================================================
echo Memeriksa Bridge Server (Port 8090)...
powershell -NoProfile -Command "if (-not (Get-NetTCPConnection -LocalPort 8090 -ErrorAction SilentlyContinue)) { Start-Process python -ArgumentList 'server.py' -WindowStyle Hidden }"
timeout /t 1 /nobreak >nul
echo Membuka di Browser Default...
start http://127.0.0.1:8090
echo Selesai! Aplikasi berjalan di background.
