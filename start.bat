@echo off
REM AID-Service Startup Script (Windows)
cd /d %~dp0
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
