#!/usr/bin/env python3
"""
Build standalone executable for Sentry Vision MVP using PyInstaller.
Usage: python src/build_exe.py
"""

import os
import subprocess
import sys

def main():
    print("Building Sentry Vision MVP executable...")

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable
        "--windowed",  # No console window
        "--name", "SentryVisionMVP",
        "--add-data", "config/config.yaml;config",
        "--add-data", "models;models",
        "src/vision_mvp.py"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("Build successful! Executable created in 'dist/' folder.")
        print("Run: dist/SentryVisionMVP.exe")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()