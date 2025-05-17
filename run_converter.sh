#!/bin/bash
# Script to run the File Converter application with the correct environment variables for WeasyPrint

# Set environment variables for WeasyPrint
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:/opt/homebrew/opt/libxml2/lib/pkgconfig"
export LDFLAGS="-L/opt/homebrew/lib -L/opt/homebrew/opt/libffi/lib"
export CPPFLAGS="-I/opt/homebrew/include -I/opt/homebrew/opt/libffi/include"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
export PYTHONPATH="$(pwd)"

# Run the application
echo "Starting File Converter..."
python3 project/main.py

# Exit with the same code as the application
exit $? 