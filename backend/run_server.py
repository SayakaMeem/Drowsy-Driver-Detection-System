#!/usr/bin/env python3
"""
Unified run script for the backend. Activates venv and runs the main server.
"""
import os
import sys
import subprocess
import platform

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, 'venv')
    app_dir = os.path.join(script_dir, 'app')
    server_file = os.path.join(app_dir, 'ml_server.py')

    if not os.path.exists(venv_dir):
        print("❌ Virtual environment not found!")
        print(f"Expected location: {venv_dir}")
        print("Please create the virtual environment first:")
        print(f"cd {script_dir}")
        print("python -m venv venv")
        return 1

    if platform.system() == "Windows":
        python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
    else:
        python_path = os.path.join(venv_dir, 'bin', 'python')

    if not os.path.exists(python_path):
        print("❌ Python executable not found in virtual environment!")
        print(f"Expected location: {python_path}")
        return 1

    if not os.path.exists(server_file):
        print(f"❌ Server file not found: {server_file}")
        return 1

    print("🚀 Starting ML Server...")
    print(f"🐍 Using Python: {python_path}")
    print(f"🏠 Working directory: {app_dir}")
    print("🌐 Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    os.chdir(app_dir)
    try:
        subprocess.run([python_path, 'ml_server.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    return 0

if __name__ == '__main__':
    sys.exit(main())