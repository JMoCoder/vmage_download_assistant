#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Image Download Assistant - One Click Deploy Script

This script will automatically complete the following operations:
1. Check Python version and environment
2. Intelligently install required dependency packages
3. Create necessary directory structure
4. Start Flask application
5. Automatically open browser to access the application

Suitable for any new user without manual environment configuration.
"""

import os
import sys
import subprocess
import platform
import time
import webbrowser
import threading
from pathlib import Path

def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           🖼️  WeChat Image Download Assistant  🖼️            ║
    ║                                                              ║
    ║              WeChat Image Download Assistant                 ║
    ║                                                              ║
    ║                     One Click Deploy v2.0                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("🚀 Preparing application environment for you, please wait...")
    print("=" * 70)

def check_python_version():
    """Check Python version"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Error: Python 3.8 or higher required")
        print(f"   Current version: {platform.python_version()}")
        print("   Please upgrade Python and try again")
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        print(f"✅ Python version check passed: {platform.python_version()}")
        return True

def get_pip_command():
    """Get pip command"""
    # Try different pip commands
    pip_commands = ['pip', 'pip3', f'{sys.executable} -m pip']
    
    for cmd in pip_commands:
        try:
            if cmd.startswith(sys.executable):
                result = subprocess.run(cmd.split() + ['--version'], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return cmd
        except:
            continue
    
    return f'{sys.executable} -m pip'

def upgrade_pip():
    """Upgrade pip to latest version"""
    print("🔧 Upgrading pip to latest version...")
    pip_cmd = get_pip_command()
    try:
        if pip_cmd.startswith(sys.executable):
            subprocess.run(pip_cmd.split() + ['install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
        else:
            subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
        print("✅ pip upgrade completed")
        return True
    except:
        print("⚠️  pip upgrade failed, continuing with current version")
        return False

def install_package_smart(package_name, pip_cmd, mirrors):
    """Smart install single package, try multiple methods"""
    print(f"   Installing {package_name}...")
    
    # Different installation methods
    install_methods = [
        # Method 1: Use domestic mirror sources
        {'args': [package_name, '-i', mirrors[0]], 'desc': 'Tsinghua Mirror'},
        {'args': [package_name, '-i', mirrors[1]], 'desc': 'Aliyun Mirror'},
        {'args': [package_name, '-i', mirrors[2]], 'desc': 'Douban Mirror'},
        # Method 2: Use precompiled packages
        {'args': [package_name, '--only-binary=all'], 'desc': 'Precompiled Package'},
        # Method 3: Skip specific package dependency check
        {'args': [package_name, '--no-deps'], 'desc': 'No Dependencies'},
        # Method 4: Use official source
        {'args': [package_name], 'desc': 'Official Source'},
    ]
    
    for method in install_methods:
        try:
            print(f"     Trying method: {method['desc']}")
            if pip_cmd.startswith(sys.executable):
                cmd = pip_cmd.split() + ['install'] + method['args']
            else:
                cmd = [pip_cmd, 'install'] + method['args']
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
            print(f"   ✅ {package_name} installed successfully")
            return True
        except subprocess.TimeoutExpired:
            print(f"     ⏰ Timeout, trying next method...")
            continue
        except subprocess.CalledProcessError as e:
            print(f"     ❌ Failed, trying next method...")
            continue
        except Exception as e:
            print(f"     ❌ Exception, trying next method...")
            continue
    
    return False

def install_dependencies_smart():
    """Smart install dependency packages"""
    print("\n🔧 Smart installing dependency packages...")
    
    # Domestic mirror source list
    mirrors = [
        'https://pypi.tuna.tsinghua.edu.cn/simple/',
        'https://mirrors.aliyun.com/pypi/simple/',
        'https://pypi.douban.com/simple/',
    ]
    
    # Core dependency packages, sorted by importance
    core_packages = [
        'flask',
        'flask-cors', 
        'requests',
        'beautifulsoup4',
    ]
    
    # Optional dependency packages
    optional_packages = [
        'pillow',
        'lxml',
    ]
    
    pip_cmd = get_pip_command()
    upgrade_pip()
    
    # Install core packages
    print("📦 Installing core dependency packages...")
    core_success = 0
    for package in core_packages:
        if install_package_smart(package, pip_cmd, mirrors):
            core_success += 1
        else:
            print(f"   ⚠️  {package} installation failed, will retry later")
    
    # Install optional packages
    print("\n📦 Installing optional dependency packages...")
    optional_success = 0
    for package in optional_packages:
        if install_package_smart(package, pip_cmd, mirrors):
            optional_success += 1
        else:
            print(f"   ⚠️  {package} installation failed, application can still run")
    
    print(f"\n📊 Installation results:")
    print(f"   Core packages: {core_success}/{len(core_packages)} successful")
    print(f"   Optional packages: {optional_success}/{len(optional_packages)} successful")
    
    # Check minimum requirements
    if core_success >= 3:  # At least flask, flask-cors, requests
        print("✅ Minimum running requirements met")
        return True
    else:
        print("❌ Minimum running requirements not met")
        return False

def verify_dependencies():
    """Verify if dependency packages are correctly installed"""
    print("\n🔍 Verifying dependency package installation...")
    
    required_modules = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('requests', 'requests'),
        ('bs4', 'BeautifulSoup4'),
    ]
    
    success_count = 0
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {display_name}")
            success_count += 1
        except ImportError:
            print(f"   ❌ {display_name} - Not installed")
    
    optional_modules = [
        ('PIL', 'Pillow'),
        ('lxml', 'lxml'),
    ]
    
    for module_name, display_name in optional_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {display_name} (Optional)")
        except ImportError:
            print(f"   ⚠️  {display_name} (Optional) - Not installed")
    
    if success_count >= 3:
        print("✅ Dependency verification passed")
        return True
    else:
        print("❌ Dependency verification failed")
        return False

def create_project_structure():
    """Create project directory structure"""
    print("\n📁 Creating project directory structure...")
    
    directories = ['downloads', 'temp', 'logs']
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"   ✅ {directory}/")
        except Exception as e:
            print(f"   ❌ Failed to create {directory}/ : {e}")
    
    print("✅ Project directory structure created")

def check_project_files():
    """Check if project files exist"""
    print("\n🔍 Checking project files...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/index.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print("\n⚠️  Some files are missing. Please ensure:")
        print("   1. You downloaded the complete project")
        print("   2. You are running this script in the project root directory")
        return False
    else:
        print("✅ All project files are present")
        return True

def test_flask_app():
    """Test if Flask app can start"""
    print("\n🧪 Testing Flask application...")
    
    try:
        # Try to import the app
        from app import app
        print("   ✅ Flask app imported successfully")
        
        # Test basic functionality
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("   ✅ Flask app routes working")
                return True
            else:
                print(f"   ❌ Flask app route test failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Flask app test failed: {e}")
        return False

def open_browser_delayed(url, delay=3):
    """Open browser after delay"""
    def open_browser():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"🌐 Browser opened: {url}")
        except:
            print(f"🌐 Please manually open: {url}")
    
    # Start browser opening thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

def start_application():
    """Start Flask application"""
    print("\n🚀 Starting Flask application...")
    print("=" * 70)
    
    try:
        from app import app
        
        # Set access URLs
        local_url = "http://127.0.0.1:5000"
        network_url = "http://0.0.0.0:5000"
        
        print("🌐 Application URLs:")
        print(f"   Local access: {local_url}")
        print(f"   Network access: {network_url}")
        print()
        print("💡 Usage Instructions:")
        print("   1. Open the above URL in your browser")
        print("   2. Enter WeChat article link")
        print("   3. Click 'Start Analysis' button")
        print("   4. Select images to download")
        print("   5. Click 'Download Selected Images'")
        print()
        print("⏹️  Stop application: Press Ctrl+C")
        print("=" * 70)
        
        # Automatically open browser
        open_browser_delayed(local_url, 2)
        
        # Start Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application startup failed: {e}")
        print("\n💡 If the problem persists, please:")
        print("   1. Check if port 5000 is occupied")
        print("   2. Try running: python app.py")
        print("   3. Check the logs/ directory for error details")

def show_manual_instructions():
    """Show manual startup instructions"""
    print("\n" + "=" * 70)
    print("📖 Manual Startup Instructions")
    print("=" * 70)
    print()
    print("If automatic startup fails, please try manual startup:")
    print()
    print("1. Install dependencies:")
    print("   pip install flask flask-cors requests beautifulsoup4")
    print()
    print("2. Start application:")
    print("   python app.py")
    print()
    print("3. Open browser and visit:")
    print("   http://127.0.0.1:5000")
    print()
    print("=" * 70)

def main():
    """Main function"""
    try:
        # Print startup banner
        print_banner()
        
        # Check Python version
        if not check_python_version():
            return
        
        # Check project files
        if not check_project_files():
            return
            
        # Install dependencies
        if not install_dependencies_smart():
            print("❌ Dependency installation failed")
            show_manual_instructions()
            return
        
        # Verify dependencies
        if not verify_dependencies():
            print("❌ Dependency verification failed")
            show_manual_instructions()
            return
        
        # Create project structure
        create_project_structure()
        
        # Test Flask app
        if not test_flask_app():
            print("❌ Flask app test failed")
            show_manual_instructions()
            return
        
        print("\n🎉 Environment setup completed successfully!")
        print("🚀 Starting application...")
        
        # Start application
        start_application()
        
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        show_manual_instructions()
    finally:
        print("\n👋 Thank you for using WeChat Image Download Assistant!")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 