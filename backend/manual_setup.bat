@echo off
echo 🤖 Setting up Drowsiness Detection Backend
echo ==========================================

echo �� Current directory: %CD%
echo.

echo �� Activating virtual environment...
call venv\Scripts\activate

echo.
echo 📦 Installing requirements...
pip install -r requirements.txt

echo.
echo 🚀 Starting server...
cd app
python ml_server.py 