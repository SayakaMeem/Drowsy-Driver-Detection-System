#!/usr/bin/env python3
"""
Startup script for the ML server
Activates virtual environment and starts the server
"""

import os
import sys
import subprocess
import platform

def activate_venv_and_run():
    """Activate virtual environment and run the server"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, 'venv')
    app_dir = os.path.join(script_dir, 'app')
    
    # Check if virtual environment exists
    if not os.path.exists(venv_dir):
        print("❌ Virtual environment not found!")
        print(f"Expected location: {venv_dir}")
        print("Please create the virtual environment first:")
        print(f"cd {script_dir}")
        print("python -m venv venv")
        return False
    
    # Determine the Python executable path based on OS
    if platform.system() == "Windows":
        python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip.exe')
    else:
        python_path = os.path.join(venv_dir, 'bin', 'python')
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
    
    # Check if Python executable exists
    if not os.path.exists(python_path):
        print("❌ Python executable not found in virtual environment!")
        print(f"Expected location: {python_path}")
        return False
    
    # Install requirements if needed
    requirements_file = os.path.join(script_dir, 'requirements.txt')
    if os.path.exists(requirements_file):
        print("📦 Installing/updating requirements...")
        try:
            subprocess.run([pip_path, 'install', '-r', requirements_file], check=True)
            print("✅ Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    
    # Change to app directory and run the server
    os.chdir(app_dir)
    
    print("�� Starting ML Server...")
    print(f"�� Working directory: {app_dir}")
    print(f"🐍 Using Python: {python_path}")
    print("🌐 Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the server
        subprocess.run([python_path, 'ml_server.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    
    return True

if __name__ == '__main__':
    success = activate_venv_and_run()
    if not success:
        sys.exit(1)