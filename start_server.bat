@echo off
title TNEA College Explorer - Persistent Server
cd /d "%~dp0"
echo ======================================================================
echo   Starting TNEA College Explorer Persistent & Synchronized Server...
echo ======================================================================
start http://localhost:8000
python server.py 8000
pause
