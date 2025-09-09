#!/usr/bin/env python3
"""
Setup Script for YouTube Dataset Creation Environment
Automatically installs dependencies and checks FFmpeg on any PC
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

def print_status(message, status="INFO"):
    """Print formatted status messages"""
    if status == "SUCCESS":
        print(f"✅ {message}")
    elif status == "ERROR":
        print(f"❌ {message}")
    elif status == "WARNING":
        print(f"⚠️  {message}")
    else:
        print(f"ℹ️  {message}")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_status("Python 3.8+ is required", "ERROR")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print_status(f"Python version: {version.major}.{version.minor}.{version.micro}", "SUCCESS")
    return True

def install_pip_packages():
    """Install required Python packages"""
    print_status("Installing Python packages...")
    
    packages = [
        "yt-dlp>=2023.12.30",
        "opencv-python>=4.8.0",
        "pandas>=2.0.0",
        "ffmpeg-python>=0.2.0",
        "tqdm>=4.65.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0"
    ]
    
    for package in packages:
        try:
            print_status(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print_status(f"Successfully installed {package}", "SUCCESS")
        except subprocess.CalledProcessError as e:
            print_status(f"Failed to install {package}: {e}", "ERROR")
            return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_status("FFmpeg is already installed and accessible", "SUCCESS")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print_status("FFmpeg not found. Attempting to install...", "WARNING")
    return install_ffmpeg()

def install_ffmpeg():
    """Install FFmpeg based on the operating system"""
    system = platform.system().lower()
    
    if system == "windows":
        return install_ffmpeg_windows()
    elif system == "linux":
        return install_ffmpeg_linux()
    elif system == "darwin":  # macOS
        return install_ffmpeg_macos()
    else:
        print_status(f"Unsupported operating system: {system}", "ERROR")
        return False

def install_ffmpeg_windows():
    """Install FFmpeg on Windows"""
    try:
        print_status("Installing FFmpeg on Windows...")
        
        # Try using winget first
        try:
            subprocess.check_call(['winget', 'install', 'FFmpeg'], timeout=300)
            print_status("FFmpeg installed successfully via winget", "SUCCESS")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print_status("winget installation failed, trying manual download...", "WARNING")
        
        # Manual download and installation
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = "ffmpeg.zip"
        
        print_status("Downloading FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        print_status("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Find the extracted directory
        extracted_dir = None
        for item in os.listdir("."):
            if item.startswith("ffmpeg-master-latest-win64-gpl"):
                extracted_dir = item
                break
        
        if extracted_dir:
            # Add to PATH for current session
            bin_path = os.path.join(os.getcwd(), extracted_dir, "bin")
            os.environ['PATH'] = bin_path + os.pathsep + os.environ.get('PATH', '')
            
            # Test if it works
            try:
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print_status("FFmpeg installed successfully", "SUCCESS")
                    print_status(f"Add this to your PATH: {bin_path}", "INFO")
                    return True
            except subprocess.TimeoutExpired:
                pass
        
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        print_status("FFmpeg installation failed", "ERROR")
        return False
        
    except Exception as e:
        print_status(f"FFmpeg installation failed: {e}", "ERROR")
        return False

def install_ffmpeg_linux():
    """Install FFmpeg on Linux"""
    try:
        # Try different package managers
        package_managers = [
            ['apt-get', 'update', '&&', 'apt-get', 'install', '-y', 'ffmpeg'],
            ['yum', 'install', '-y', 'ffmpeg'],
            ['dnf', 'install', '-y', 'ffmpeg'],
            ['pacman', '-S', '--noconfirm', 'ffmpeg']
        ]
        
        for manager in package_managers:
            try:
                if manager[0] == 'apt-get':
                    subprocess.check_call(['bash', '-c', ' '.join(manager)], timeout=300)
                else:
                    subprocess.check_call(manager, timeout=300)
                print_status(f"FFmpeg installed successfully via {manager[0]}", "SUCCESS")
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
        
        print_status("FFmpeg installation failed with all package managers", "ERROR")
        return False
        
    except Exception as e:
        print_status(f"FFmpeg installation failed: {e}", "ERROR")
        return False

def install_ffmpeg_macos():
    """Install FFmpeg on macOS"""
    try:
        # Try using Homebrew
        subprocess.check_call(['brew', 'install', 'ffmpeg'], timeout=300)
        print_status("FFmpeg installed successfully via Homebrew", "SUCCESS")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print_status("Homebrew installation failed", "ERROR")
        return False
    except FileNotFoundError:
        print_status("Homebrew not found. Please install Homebrew first.", "ERROR")
        return False

def create_test_csv():
    """Create a small test CSV file if it doesn't exist"""
    test_csv_path = "avspeech_test_100.csv"
    
    if os.path.exists(test_csv_path):
        print_status("Test CSV file already exists", "SUCCESS")
        return True
    
    # Check if main CSV exists to create test version
    main_csv_path = "avspeech_test.csv"
    if not os.path.exists(main_csv_path):
        print_status("Main CSV file not found. Please add avspeech_test.csv to continue.", "WARNING")
        return False
    
    try:
        import pandas as pd
        df = pd.read_csv(main_csv_path)
        test_df = df.head(100)
        test_df.to_csv(test_csv_path, index=False)
        print_status(f"Created test CSV with {len(test_df)} rows", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Failed to create test CSV: {e}", "ERROR")
        return False

def verify_environment():
    """Verify that all components are working"""
    print_status("Verifying environment...")
    
    # Test imports
    try:
        import yt_dlp
        import cv2
        import pandas
        import ffmpeg
        import tqdm
        import numpy
        from PIL import Image
        print_status("All Python packages imported successfully", "SUCCESS")
    except ImportError as e:
        print_status(f"Import error: {e}", "ERROR")
        return False
    
    # Test FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_status("FFmpeg is working correctly", "SUCCESS")
        else:
            print_status("FFmpeg test failed", "ERROR")
            return False
    except Exception as e:
        print_status(f"FFmpeg test failed: {e}", "ERROR")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 YouTube Dataset Creation Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install Python packages
    if not install_pip_packages():
        return False
    
    # Install/check FFmpeg
    if not check_ffmpeg():
        return False
    
    # Create test CSV if needed
    create_test_csv()
    
    # Verify environment
    if not verify_environment():
        return False
    
    print("\n" + "=" * 50)
    print_status("🎉 Environment setup completed successfully!", "SUCCESS")
    print("\n📋 Next steps:")
    print("1. Edit config.py to set MODE = 'TEST' or 'PRODUCTION'")
    print("2. Run: python youtube_download_portable.py")
    print("3. For production, change MODE to 'PRODUCTION' in config.py")
    print("\n📁 Files created:")
    print("- config.py (configuration file)")
    print("- youtube_download_portable.py (main script)")
    print("- requirements.txt (Python dependencies)")
    print("- setup_portable.py (this setup script)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
