# File Converter

A powerful file conversion tool with a modern macOS-optimized GUI. Convert between various file formats with a simple, clean interface.

## Features

- **Image Converter**: Convert between PNG, JPEG, BMP, GIF, and TIFF formats
- **PDF to Word**: Convert PDF documents to editable Word (.docx) files
- **Markdown to HTML**: Convert Markdown files to HTML with customizable styling
- **HTML to PDF**: Convert HTML files to PDF documents
- **Markdown to PDF**: Convert Markdown files directly to PDF

## Installation

### Requirements

- Python 3.10 or higher
- macOS (optimized for macOS, but should work on other platforms)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/file-converter.git
   cd file-converter
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

From the project root directory:

```
python -m project.main
```

## Usage

1. Select the appropriate converter tab for your needs
2. Drag and drop a file onto the input area or use the Browse button to select a file
3. Configure conversion options (if applicable)
4. Select an output directory (optional - defaults to the same location as the input file)
5. Click the Convert button

## Supported Formats

### Image Converter
- Input: PNG, JPEG/JPG, BMP, GIF, TIFF/TIF
- Output: PNG, JPEG/JPG, BMP, GIF, TIFF/TIF

### PDF to Word
- Input: PDF
- Output: DOCX

### Markdown to HTML
- Input: MD, MARKDOWN
- Output: HTML

### HTML to PDF
- Input: HTML, HTM
- Output: PDF

### Markdown to PDF
- Input: MD, MARKDOWN
- Output: PDF

## Development

### Project Structure

```
project/
├── converters/         # Conversion modules
│   ├── image_converter.py
│   ├── pdf_to_word.py
│   ├── md_to_html.py
│   ├── html_to_pdf.py
│   └── md_to_pdf.py
├── gui/                # GUI components
│   ├── main_window.py
│   └── styles.py
├── utils/              # Utility functions
│   ├── file_handler.py
│   └── error_handler.py
├── tests/              # Test suite
├── main.py             # Application entry point
└── requirements.txt    # Dependencies
```

### Running Tests

```
pytest project/tests/
```

## Adding New Converters

To add a new converter:

1. Create a new converter class in the `converters` directory
2. Add an appropriate tab class in `gui/main_window.py`
3. Register the new tab in the `MainWindow` class

## License

[MIT License](LICENSE) 