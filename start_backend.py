#!/usr/bin/env python3
"""
Startup script for the drowsiness detection system
Starts the Python ML backend server
"""

import os
import sys
import subprocess
import platform
import time

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow version: {tf.__version__}")
    except ImportError:
        print("❌ TensorFlow not found")
        return False
    
    try:
        import flask
        print(f"✅ Flask version: {flask.__version__}")
    except ImportError:
        print("❌ Flask not found")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV not found")
        return False
    
    return True

def start_backend():
    """Start the Python ML backend server"""
    
    # Get the backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        return False
    
    # Check if virtual environment exists
    venv_dir = os.path.join(backend_dir, 'venv')
    if not os.path.exists(venv_dir):
        print("❌ Virtual environment not found!")
        print(f"Expected location: {venv_dir}")
        print("\nTo create the virtual environment:")
        print(f"cd {backend_dir}")
        print("python -m venv venv")
        print("venv\\Scripts\\activate  # On Windows")
        print("source venv/bin/activate  # On Linux/Mac")
        print("pip install -r requirements.txt")
        return False
    
    # Determine the Python executable path
    if platform.system() == "Windows":
        python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
    else:
        python_path = os.path.join(venv_dir, 'bin', 'python')
    
    if not os.path.exists(python_path):
        print(f"❌ Python executable not found: {python_path}")
        return False
    
    # Check if the app directory and server file exist
    app_dir = os.path.join(backend_dir, 'app')
    server_file = os.path.join(app_dir, 'ml_server.py')
    
    if not os.path.exists(server_file):
        print(f"❌ Server file not found: {server_file}")
        print("Please ensure ml_server.py is in the backend/app/ directory")
        return False
    
    print("🚀 Starting ML Backend Server...")
    print(f" Backend directory: {backend_dir}")
    print(f"🐍 Using Python: {python_path}")
    print(f"📄 Server file: {server_file}")
    print("🌐 Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Change to app directory and run the server
        os.chdir(app_dir)
        subprocess.run([python_path, 'ml_server.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    
    return True

def main():
    """Main function"""
    print("🤖 Drowsiness Detection ML Backend")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them:")
        print("pip install tensorflow flask flask-cors opencv-python pillow numpy")
        return 1
    
    print("\n✅ All dependencies found!")
    
    # Start the backend
    success = start_backend()
    
    if not success:
        print("\n❌ Failed to start backend server")
        return 1
    
    print("\n✅ Backend server stopped successfully")
    return 0

if __name__ == '__main__':
    sys.exit(main()) 