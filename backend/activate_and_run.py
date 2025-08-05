#!/usr/bin/env python3
"""
Script to properly activate virtual environment and run the server
"""

import os
import sys
import subprocess
import platform

def activate_venv_and_install():
    """Activate virtual environment and install requirements"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, 'venv')
    
    print(f"📁 Script directory: {script_dir}")
    print(f"📁 Virtual environment directory: {venv_dir}")
    
    # Check if virtual environment exists
    if not os.path.exists(venv_dir):
        print("❌ Virtual environment not found!")
        print(f"Creating virtual environment in: {venv_dir}")
        
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
            print("✅ Virtual environment created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    # Determine the pip path based on OS
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip.exe')
        python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
    else:
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
        python_path = os.path.join(venv_dir, 'bin', 'python')
    
    print(f"🐍 Python path: {python_path}")
    print(f"📦 Pip path: {pip_path}")
    
    # Check if pip exists
    if not os.path.exists(pip_path):
        print(f"❌ pip not found in virtual environment: {pip_path}")
        return False
    
    # Install requirements
    requirements_file = os.path.join(script_dir, 'requirements.txt')
    print(f"📄 Requirements file: {requirements_file}")
    
    if os.path.exists(requirements_file):
        print("📦 Installing requirements in virtual environment...")
        try:
            # Upgrade pip first
            print("⬆️  Upgrading pip...")
            subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
            
            print("📦 Installing requirements...")
            result = subprocess.run([pip_path, 'install', '-r', requirements_file], 
                                  capture_output=True, text=True, check=True)
            print("✅ Requirements installed successfully!")
            print("📋 Installation output:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            print(f"Error output: {e.stderr}")
            return False
    else:
        print(f"⚠️  requirements.txt not found at: {requirements_file}")
        print("Installing basic packages...")
        basic_packages = [
            'tensorflow',
            'flask',
            'flask-cors',
            'opencv-python',
            'pillow',
            'numpy',
            'requests'
        ]
        try:
            for package in basic_packages:
                print(f"Installing {package}...")
                subprocess.run([pip_path, 'install', package], check=True)
            print("✅ Basic packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    return python_path

def run_server(python_path):
    """Run the server using the virtual environment Python"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, 'app')
    server_file = os.path.join(app_dir, 'ml_server.py')
    
    print(f"📁 App directory: {app_dir}")
    print(f"📄 Server file: {server_file}")
    
    if not os.path.exists(server_file):
        print(f"❌ Server file not found: {server_file}")
        print("Please ensure ml_server.py is in the backend/app/ directory")
        return False
    
    print("�� Starting ML Server with virtual environment...")
    print(f"🐍 Using Python: {python_path}")
    print(f"🏠 Working directory: {app_dir}")
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
    
    # Activate venv and install requirements
    python_path = activate_venv_and_install()
    if not python_path:
        return 1
    
    # Run the server
    success = run_server(python_path)
    
    if not success:
        print("\n❌ Failed to start server")
        return 1
    
    print("\n✅ Server stopped successfully")
    return 0

if __name__ == '__main__':
    sys.exit(main()) 