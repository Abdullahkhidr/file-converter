# File Converter

A powerful file conversion tool with a modern macOS GUI.

## Features

- Convert images between different formats (PNG, JPG, GIF, etc.)
- Convert PDF to Word documents
- Convert Markdown to HTML
- Convert HTML to PDF
- Convert Markdown to PDF

## Installation

### Prerequisites

- Python 3.10 or higher
- macOS 10.15 or higher

### Install Dependencies

1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install required system libraries:
   ```bash
   brew install pango cairo fontconfig libffi gobject-introspection
   ```

3. Install the Python package:
   ```bash
   pip install -e .
   ```

### Fix WeasyPrint for HTML to PDF Conversion

If the HTML to PDF or Markdown to PDF conversion features aren't working, run the fix script:

```bash
python3 fix_weasyprint.py
```

This script will:
- Set the correct environment variables
- Reinstall WeasyPrint with the proper configuration
- Provide instructions for permanently setting the environment variables

## Running the Application

For the best experience, use the provided shell script which sets up the environment:

```bash
./run_converter.sh
```

Or manually with:

```bash
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:/opt/homebrew/opt/libxml2/lib/pkgconfig"
export LDFLAGS="-L/opt/homebrew/lib -L/opt/homebrew/opt/libffi/lib"
export CPPFLAGS="-I/opt/homebrew/include -I/opt/homebrew/opt/libffi/include"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
export PYTHONPATH="$(pwd)"
python3 project/main.py
```

## Troubleshooting

### HTML to PDF Conversion Not Working

If you see an error about WeasyPrint not being able to find libraries:

1. Run the fix script: `python3 fix_weasyprint.py`
2. Add the recommended environment variables to your `~/.zshrc`
3. Use the `run_converter.sh` script to start the application

### Application Not Starting

Make sure you've installed all the dependencies and are using the correct Python version:

```bash
python3 --version  # Should be 3.10 or higher
pip install -e .   # Reinstall the package
```

## License

MIT 