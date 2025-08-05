@echo off
echo 🤖 Setting up Drowsiness Detection Backend
echo ==========================================

echo.
echo �� Current directory: %CD%
echo.

echo 🧹 Cleaning up any existing installations...
pip uninstall tensorflow flask flask-cors opencv-python pillow numpy -y

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

echo.
echo 📦 Installing packages in virtual environment...
echo Installing tensorflow-cpu (lighter version)...
pip install tensorflow-cpu

echo Installing other packages...
pip install flask flask-cors opencv-python pillow numpy

echo.
echo ✅ Installation complete!
echo.
echo 🚀 To start the server, run: run.bat
echo.
pause 