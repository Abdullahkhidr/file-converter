#!/usr/bin/env python3
"""
Script to fix WeasyPrint installation on macOS.
This script sets the proper environment variables and reinstalls WeasyPrint.
"""

import os
import sys
import subprocess
import platform

def run_command(command):
    """Run a shell command and print its output."""
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, check=False,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    
    print("STDOUT:")
    print(process.stdout)
    
    if process.stderr:
        print("STDERR:")
        print(process.stderr)
    
    return process.returncode

def main():
    """Main function."""
    if platform.system() != "Darwin":
        print("This script is only for macOS.")
        sys.exit(1)
    
    print("Setting environment variables for WeasyPrint...")
    
    # Set environment variables for the current process
    brew_prefix = subprocess.check_output("brew --prefix", shell=True).decode().strip()
    
    env_vars = {
        "PKG_CONFIG_PATH": f"{brew_prefix}/lib/pkgconfig:{brew_prefix}/opt/libffi/lib/pkgconfig:{brew_prefix}/opt/libxml2/lib/pkgconfig",
        "LDFLAGS": f"-L{brew_prefix}/lib -L{brew_prefix}/opt/libffi/lib",
        "CPPFLAGS": f"-I{brew_prefix}/include -I{brew_prefix}/opt/libffi/include",
        "DYLD_LIBRARY_PATH": f"{brew_prefix}/lib"
    }
    
    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"  {var}={value}")
    
    print("\nUninstalling WeasyPrint...")
    run_command("pip uninstall -y weasyprint")
    
    print("\nReinstalling WeasyPrint...")
    run_command("pip install weasyprint --force-reinstall")
    
    print("\nWeasyPrint installation completed.")
    print("\nImportant: For the changes to take effect in your terminal sessions, add the following to your ~/.zshrc:")
    print(f"export PKG_CONFIG_PATH=\"{env_vars['PKG_CONFIG_PATH']}\"")
    print(f"export LDFLAGS=\"{env_vars['LDFLAGS']}\"")
    print(f"export CPPFLAGS=\"{env_vars['CPPFLAGS']}\"")
    print(f"export DYLD_LIBRARY_PATH=\"{env_vars['DYLD_LIBRARY_PATH']}\"")
    
    print("\nRelaunch your terminal or run 'source ~/.zshrc' to apply the changes.")
    print("Then try running the application again.")

if __name__ == "__main__":
    main() 