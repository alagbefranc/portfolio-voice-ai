#!/usr/bin/env python3
"""
Setup script for Portfolio Voice AI Assistant

This script helps you set up the voice AI backend for your portfolio.
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is 3.9 or later"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or later is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        return False

def download_model_files():
    """Download required model files"""
    print("\n🔄 Downloading model files...")
    try:
        subprocess.run([sys.executable, "agent.py", "download-files"], check=True)
        print("✅ Model files downloaded successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to download model files")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists(".env"):
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("Please copy .env.template to .env and fill in your API keys")
        return False

def main():
    print("🎤 Portfolio Voice AI Assistant Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Download model files
    if not download_model_files():
        return False
    
    # Check environment file
    env_exists = check_env_file()
    
    print("\n" + "=" * 40)
    if env_exists:
        print("🎉 Setup complete! You can now run the voice AI agent.")
        print("\nTo start the agent:")
        print("  python agent.py dev")
    else:
        print("⚠️  Setup almost complete!")
        print("Next steps:")
        print("1. Copy .env.template to .env")
        print("2. Fill in your API keys in the .env file")
        print("3. Run: python agent.py dev")
    
    return True

if __name__ == "__main__":
    main()
