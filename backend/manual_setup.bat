@echo off
REM Manual setup script for backend (Windows)
echo Manual setup for Drowsiness Detection Backend
cd /d %~dp0
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
echo.
echo ✅ Manual setup complete! To run the server, use: python run_server.py
pause 