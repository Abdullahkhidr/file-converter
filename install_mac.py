#!/usr/bin/env python3
"""
macOS installation script for File Converter.
This script creates an application bundle in the Applications folder.
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path


def create_app_bundle():
    """Create a macOS .app bundle for File Converter."""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the application name
    app_name = "File Converter.app"
    
    # Define application paths
    applications_dir = os.path.expanduser("~/Applications")
    app_bundle_path = os.path.join(applications_dir, app_name)
    
    # Create directories
    os.makedirs(applications_dir, exist_ok=True)
    
    # Remove existing bundle if it exists
    if os.path.exists(app_bundle_path):
        print(f"Removing existing application bundle: {app_bundle_path}")
        shutil.rmtree(app_bundle_path)
    
    # Create the bundle structure
    print(f"Creating application bundle: {app_bundle_path}")
    
    # Create the basic structure
    os.makedirs(os.path.join(app_bundle_path, "Contents", "MacOS"), exist_ok=True)
    os.makedirs(os.path.join(app_bundle_path, "Contents", "Resources"), exist_ok=True)
    
    # Create the Info.plist file
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>FileConverter</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.fileconverter.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>File Converter</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
"""
    
    with open(os.path.join(app_bundle_path, "Contents", "Info.plist"), "w") as f:
        f.write(info_plist)
    
    # Create the launcher script
    launcher_script = f"""#!/bin/bash
# Launcher script for File Converter

# Get the directory of the script
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"

# Activate the virtual environment
source "$DIR/../Resources/venv/bin/activate"

# Launch the application
python -m project.main "$@"
"""
    
    launcher_path = os.path.join(app_bundle_path, "Contents", "MacOS", "FileConverter")
    with open(launcher_path, "w") as f:
        f.write(launcher_script)
    
    # Make the launcher script executable
    os.chmod(launcher_path, 0o755)
    
    # Create a virtual environment in the Resources directory
    venv_path = os.path.join(app_bundle_path, "Contents", "Resources", "venv")
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
    
    # Install the package in the virtual environment
    print("Installing File Converter and dependencies...")
    subprocess.run([
        os.path.join(venv_path, "bin", "pip"),
        "install",
        "-e",
        current_dir
    ], check=True)
    
    # Copy the application files to the Resources directory
    resources_path = os.path.join(app_bundle_path, "Contents", "Resources")
    project_path = os.path.join(resources_path, "project")
    
    # Copy the project directory
    if os.path.exists(os.path.join(current_dir, "project")):
        shutil.copytree(
            os.path.join(current_dir, "project"),
            project_path,
            dirs_exist_ok=True
        )
    
    print(f"Application bundle created at: {app_bundle_path}")
    print("Installation complete!")


if __name__ == "__main__":
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("This installation script is only for macOS.")
        sys.exit(1)
    
    # Create the application bundle
    create_app_bundle()
    
    print("")
    print("File Converter has been installed to your Applications folder.")
    print("You can launch it from there or from Spotlight.")
    print("") 