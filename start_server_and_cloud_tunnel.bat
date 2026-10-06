@echo off
title TNEA College Explorer - Public Cloud Server & Tunnel
cd /d "%~dp0"
echo ======================================================================
echo   Starting TNEA College Explorer - Public Cloud Synchronized Server
echo ======================================================================

echo [*] Starting Local Backend Server on port 8000...
start /B python -u server.py 8000

timeout /t 2 /nobreak >nul

echo [*] Starting Cloudflare Public HTTPS Tunnel...
start "" cloudflared.exe tunnel --url http://localhost:8000

echo ======================================================================
echo [SUCCESS] Server and Cloud Tunnel are running!
echo You can check the tunnel window for your permanent live HTTPS link.
echo ======================================================================
pause
