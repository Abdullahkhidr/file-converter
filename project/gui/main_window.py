import os
import sys
import logging
from typing import Optional, List, Dict, Callable, Tuple, Any
from pathlib import Path
import threading
import time

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QComboBox, QProgressBar,
    QMessageBox, QScrollArea, QFrame, QGridLayout, QSpacerItem, QSizePolicy,
    QCheckBox, QGroupBox, QRadioButton, QButtonGroup, QSlider
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer, QSettings, QUrl, QObject
from PyQt6.QtGui import QIcon, QPixmap, QDragEnterEvent, QDropEvent

from project.gui.styles import StyleManager, AppTheme
from project.utils.file_handler import FileHandler
from project.utils.error_handler import ErrorHandler
from project.converters.image_converter import ImageConverter
from project.converters.pdf_to_word import PdfToWordConverter
from project.converters.md_to_html import MarkdownToHtmlConverter
from project.converters.html_to_pdf import HtmlToPdfConverter
from project.converters.md_to_pdf import MarkdownToPdfConverter


class WorkerSignals(QObject):
    """
    Defines the signals available for a worker thread.
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class ConversionWorker(QThread):
    """
    Worker thread for handling file conversions without blocking the GUI.
    """
    def __init__(
        self, 
        converter_func: Callable, 
        args: List, 
        kwargs: Dict[str, Any]
    ):
        super().__init__()
        self.converter_func = converter_func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        """Execute the conversion function in a separate thread."""
        try:
            # Run the conversion function with the provided arguments
            result = self.converter_func(*self.args, **self.kwargs)
            
            # Emit the success signal with the result
            self.signals.result.emit(result)
            
        except Exception as e:
            # Log the error
            logging.error(f"Error in conversion worker: {str(e)}")
            
            # Emit the error signal with a user-friendly message
            self.signals.error.emit(ErrorHandler.get_error_message(e))
            
        finally:
            # Always emit finished signal
            self.signals.finished.emit()


class DragDropFileWidget(QWidget):
    """
    Widget that supports drag and drop of files.
    """
    fileDropped = pyqtSignal(str)
    
    def __init__(self, accepted_extensions: List[str], parent=None):
        super().__init__(parent)
        self.accepted_extensions = [ext.lower().lstrip('.') for ext in accepted_extensions]
        self.setup_ui()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Drop area styling
        self.setMinimumHeight(100)
        self.setObjectName("dropArea")
        self.setStyleSheet("""
            QWidget#dropArea {
                border: 2px dashed #AAAAAA;
                border-radius: 8px;
                background-color: rgba(0, 0, 0, 0.03);
            }
        """)
        
        # Instructions label
        self.label = QLabel(f"Drag & drop files here\n(Accepted formats: {', '.join(self.accepted_extensions)})")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # Browse button
        self.browse_button = QPushButton("Browse Files")
        self.browse_button.setObjectName("secondaryButton")
        self.browse_button.clicked.connect(self.browse_files)
        layout.addWidget(self.browse_button, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for files."""
        if event.mimeData().hasUrls():
            # Check if any of the dragged files have an accepted extension
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if any(file_path.lower().endswith(f".{ext}") for ext in self.accepted_extensions):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for files."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if any(file_path.lower().endswith(f".{ext}") for ext in self.accepted_extensions):
                self.fileDropped.emit(file_path)
                event.acceptProposedAction()
                return
        event.ignore()
    
    def browse_files(self):
        """Open file dialog to select files."""
        extensions = " ".join(f"*.{ext}" for ext in self.accepted_extensions)
        filter_str = f"Accepted Files ({extensions})"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select File", 
            "", 
            filter_str
        )
        
        if file_path:
            self.fileDropped.emit(file_path)


class ConverterTabBase(QWidget):
    """
    Base class for converter tabs with common functionality.
    """
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.input_file = ""
        self.output_dir = ""
        self.worker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components for the converter tab."""
        layout = QVBoxLayout(self)
        layout.setSpacing(StyleManager.get_margin("medium"))
        
        # Title
        title_label = QLabel(self.title)
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # Container for the form
        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setSpacing(StyleManager.get_margin("medium"))
        layout.addWidget(self.form_widget)
        
        # To be implemented by subclasses
        self.setup_form()
        
        # Status area
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
        
        # Add spacer at the bottom
        layout.addStretch()
    
    def setup_form(self):
        """To be implemented by subclasses to set up specific form fields."""
        pass
    
    def add_file_input_section(self, accepted_extensions: List[str], label_text: str = "Input File"):
        """Add a file input section to the form."""
        # Section label
        label = QLabel(label_text)
        label.setObjectName("headingLabel")
        self.form_layout.addWidget(label)
        
        # File drop area
        self.file_drop_widget = DragDropFileWidget(accepted_extensions)
        self.file_drop_widget.fileDropped.connect(self.handle_file_dropped)
        self.form_layout.addWidget(self.file_drop_widget)
        
        # Selected file display
        file_layout = QHBoxLayout()
        file_layout.setSpacing(StyleManager.get_margin("small"))
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.clicked.connect(self.clear_file)
        self.clear_button.setVisible(False)
        file_layout.addWidget(self.clear_button)
        
        self.form_layout.addLayout(file_layout)
    
    def add_output_section(self, default_format: Optional[str] = None, formats: Optional[List[str]] = None):
        """
        Add an output section to the form.
        
        Args:
            default_format: Default output format
            formats: List of available output formats
        """
        # Section label
        label = QLabel("Output Options")
        label.setObjectName("headingLabel")
        self.form_layout.addWidget(label)
        
        # Output format selection (if formats provided)
        if formats:
            format_layout = QHBoxLayout()
            format_layout.setSpacing(StyleManager.get_margin("small"))
            
            format_label = QLabel("Output Format:")
            format_layout.addWidget(format_label)
            
            self.format_combo = QComboBox()
            self.format_combo.addItems(formats)
            if default_format in formats:
                self.format_combo.setCurrentText(default_format)
            format_layout.addWidget(self.format_combo)
            
            self.form_layout.addLayout(format_layout)
        
        # Output directory selection
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(StyleManager.get_margin("small"))
        
        dir_label = QLabel("Output Directory:")
        dir_layout.addWidget(dir_label)
        
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("Same as input file")
        self.dir_edit.setReadOnly(True)
        dir_layout.addWidget(self.dir_edit)
        
        self.browse_dir_button = QPushButton("Browse")
        self.browse_dir_button.setObjectName("secondaryButton")
        self.browse_dir_button.clicked.connect(self.browse_output_dir)
        dir_layout.addWidget(self.browse_dir_button)
        
        self.form_layout.addLayout(dir_layout)
        
        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.start_conversion)
        self.form_layout.addWidget(self.convert_button, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def handle_file_dropped(self, file_path: str):
        """Handle when a file is dropped or selected."""
        self.input_file = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.clear_button.setVisible(True)
        self.update_convert_button()
    
    def clear_file(self):
        """Clear the selected file."""
        self.input_file = ""
        self.file_label.setText("No file selected")
        self.clear_button.setVisible(False)
        self.update_convert_button()
    
    def browse_output_dir(self):
        """Open directory dialog to select output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Directory", 
            self.output_dir or os.path.expanduser("~")
        )
        
        if directory:
            self.output_dir = directory
            self.dir_edit.setText(directory)
    
    def update_convert_button(self):
        """Update the enabled state of the convert button based on input."""
        self.convert_button.setEnabled(bool(self.input_file))
    
    def update_status(self, message: str, is_error: bool = False):
        """Update the status message and apply appropriate styling."""
        self.status_label.setText(message)
        if is_error:
            self.status_label.setObjectName("errorLabel")
        else:
            self.status_label.setObjectName("")
        self.status_label.setStyleSheet("")  # Force style refresh
    
    def set_busy(self, busy: bool):
        """Set the UI state to busy or ready."""
        self.file_drop_widget.setEnabled(not busy)
        self.browse_dir_button.setEnabled(not busy)
        self.convert_button.setEnabled(not busy and bool(self.input_file))
        self.progress_bar.setVisible(busy)
        
        if busy:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.update_status("Converting... Please wait.")
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
    
    def conversion_complete(self, result):
        """Handle conversion complete."""
        self.set_busy(False)
        
        if result:
            # Unpack tuple if result is a tuple (for backward compatibility)
            if isinstance(result, tuple) and len(result) >= 2:
                success, file_path = result[:2]
                if not success:
                    # This is an error message
                    self.conversion_error(file_path)
                    return
                result = file_path
            
            if isinstance(result, str) and os.path.exists(result):
                self.update_status(f"Conversion complete: {os.path.basename(result)}")
                
                # Ask if user wants to open the file
                reply = QMessageBox.question(
                    self, 
                    "Conversion Complete", 
                    f"The file has been converted successfully. Do you want to open the output file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.open_file(result)
            else:
                self.update_status("Conversion complete")
    
    def conversion_error(self, error_message: str):
        """Handle conversion error."""
        self.set_busy(False)
        self.update_status(f"Error: {error_message}", is_error=True)
        
        # Show error dialog
        QMessageBox.critical(
            self, 
            "Conversion Error", 
            f"An error occurred during conversion:\n\n{error_message}"
        )
    
    def open_file(self, file_path: str):
        """Open a file with the default application."""
        # Handle tuple for backward compatibility
        if isinstance(file_path, tuple) and len(file_path) >= 2:
            success, path = file_path[:2]
            if not success:
                QMessageBox.warning(
                    self, 
                    "File Not Found", 
                    f"Could not open the file: {path}"
                )
                return
            file_path = path
        
        if not os.path.exists(file_path):
            QMessageBox.warning(
                self, 
                "File Not Found", 
                f"The file {file_path} could not be found."
            )
            return
        
        # Use platform-specific approach to open the file
        if sys.platform == 'darwin':  # macOS
            os.system(f'open "{file_path}"')
        elif sys.platform == 'win32':  # Windows
            os.system(f'start "" "{file_path}"')
        else:  # Linux/Unix
            os.system(f'xdg-open "{file_path}"')
    
    def start_conversion(self):
        """Start the conversion process - to be implemented by subclasses."""
        pass
    
    def cleanup(self):
        """Clean up resources used by the tab."""
        try:
            if self.worker and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
        except (RuntimeError, AttributeError):
            # Handle the case where the worker object has been deleted or corrupted
            pass


class ImageConverterTab(ConverterTabBase):
    """Tab for converting images between different formats."""
    
    def __init__(self, parent=None):
        self.converter = ImageConverter()
        super().__init__("Image Converter", parent)
    
    def setup_form(self):
        # File input section
        self.add_file_input_section(
            self.converter.SUPPORTED_FORMATS,
            "Input Image"
        )
        
        # Add output format selection
        self.add_output_section(
            default_format="png",
            formats=self.converter.SUPPORTED_FORMATS
        )
        
        # Add quality slider for JPG/JPEG
        quality_layout = QHBoxLayout()
        quality_layout.setSpacing(StyleManager.get_margin("small"))
        
        quality_label = QLabel("Quality (for JPEG):")
        quality_layout.addWidget(quality_label)
        
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(95)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(10)
        quality_layout.addWidget(self.quality_slider)
        
        self.quality_value = QLabel("95%")
        quality_layout.addWidget(self.quality_value)
        
        self.form_layout.addLayout(quality_layout)
        
        # Connect quality slider to update label
        self.quality_slider.valueChanged.connect(self.update_quality_label)
        
        # Connect format combo to enable/disable quality slider
        self.format_combo.currentTextChanged.connect(self.update_quality_slider_visibility)
        
        # Initial visibility
        self.update_quality_slider_visibility(self.format_combo.currentText())
    
    def update_quality_label(self, value):
        """Update the quality label to show the current slider value."""
        self.quality_value.setText(f"{value}%")
    
    def update_quality_slider_visibility(self, format_text):
        """Show/hide quality slider based on format."""
        is_jpeg = format_text.lower() in ['jpg', 'jpeg']
        quality_layout = self.quality_slider.parent().layout()
        for i in range(quality_layout.count()):
            item = quality_layout.itemAt(i).widget()
            if item:
                item.setVisible(is_jpeg)
    
    def start_conversion(self):
        """Start the image conversion process."""
        if not self.input_file:
            return
        
        # Get selected output format
        output_format = self.format_combo.currentText()
        
        # Get output path
        if self.output_dir:
            filename = FileHandler.get_filename(self.input_file)
            output_path = os.path.join(self.output_dir, f"{filename}.{output_format}")
        else:
            output_path = None
        
        # Get quality for JPEG
        quality = self.quality_slider.value() if output_format.lower() in ['jpg', 'jpeg'] else None
        
        # Set UI to busy state
        self.set_busy(True)
        
        # Create worker thread
        self.worker = ConversionWorker(
            self.converter.convert_image,
            [self.input_file],
            {
                'output_path': output_path,
                'output_format': output_format,
                'quality': quality
            }
        )
        
        # Connect signals
        self.worker.signals.result.connect(self.conversion_complete)
        self.worker.signals.error.connect(self.conversion_error)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        
        # Start the worker thread
        self.worker.start()


class PdfToWordTab(ConverterTabBase):
    """Tab for converting PDF to Word documents."""
    
    def __init__(self, parent=None):
        self.converter = PdfToWordConverter()
        super().__init__("PDF to Word Converter", parent)
    
    def setup_form(self):
        # File input section
        self.add_file_input_section(
            self.converter.SUPPORTED_INPUT_FORMATS,
            "Input PDF"
        )
        
        # Add output section
        self.add_output_section(
            default_format="docx",
            formats=self.converter.SUPPORTED_OUTPUT_FORMATS
        )
        
        # Add page range options
        page_group = QGroupBox("Page Range")
        page_layout = QVBoxLayout(page_group)
        
        # All pages option
        self.all_pages_radio = QRadioButton("All Pages")
        self.all_pages_radio.setChecked(True)
        page_layout.addWidget(self.all_pages_radio)
        
        # Page range option
        range_layout = QHBoxLayout()
        self.page_range_radio = QRadioButton("Page Range:")
        range_layout.addWidget(self.page_range_radio)
        
        self.start_page_edit = QLineEdit()
        self.start_page_edit.setPlaceholderText("Start")
        self.start_page_edit.setEnabled(False)
        self.start_page_edit.setFixedWidth(70)
        range_layout.addWidget(self.start_page_edit)
        
        range_layout.addWidget(QLabel("to"))
        
        self.end_page_edit = QLineEdit()
        self.end_page_edit.setPlaceholderText("End")
        self.end_page_edit.setEnabled(False)
        self.end_page_edit.setFixedWidth(70)
        range_layout.addWidget(self.end_page_edit)
        
        range_layout.addStretch()
        page_layout.addLayout(range_layout)
        
        # Create button group for radio buttons
        self.page_button_group = QButtonGroup(self)
        self.page_button_group.addButton(self.all_pages_radio)
        self.page_button_group.addButton(self.page_range_radio)
        
        # Connect radio buttons to enable/disable page range inputs
        self.page_range_radio.toggled.connect(self.toggle_page_range)
        
        self.form_layout.addWidget(page_group)
    
    def toggle_page_range(self, checked):
        """Enable/disable page range inputs based on radio button selection."""
        self.start_page_edit.setEnabled(checked)
        self.end_page_edit.setEnabled(checked)
    
    def start_conversion(self):
        """Start the PDF to Word conversion process."""
        if not self.input_file:
            return
        
        # Get output path
        if self.output_dir:
            filename = FileHandler.get_filename(self.input_file)
            output_path = os.path.join(self.output_dir, f"{filename}.docx")
        else:
            output_path = None
        
        # Get page range
        start_page = None
        end_page = None
        
        if self.page_range_radio.isChecked():
            try:
                if self.start_page_edit.text().strip():
                    start_page = max(0, int(self.start_page_edit.text()) - 1)  # Convert to 0-based
                if self.end_page_edit.text().strip():
                    end_page = int(self.end_page_edit.text())
            except ValueError:
                QMessageBox.warning(
                    self, 
                    "Invalid Page Range", 
                    "Please enter valid page numbers."
                )
                return
        
        # Set UI to busy state
        self.set_busy(True)
        
        # Create worker thread
        self.worker = ConversionWorker(
            self.converter.convert_pdf_to_word,
            [self.input_file],
            {
                'output_path': output_path,
                'start_page': start_page if start_page is not None else 0,
                'end_page': end_page
            }
        )
        
        # Connect signals
        self.worker.signals.result.connect(self.conversion_complete)
        self.worker.signals.error.connect(self.conversion_error)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        
        # Start the worker thread
        self.worker.start()


class MarkdownToHtmlTab(ConverterTabBase):
    """Tab for converting Markdown to HTML."""
    
    def __init__(self, parent=None):
        self.converter = MarkdownToHtmlConverter()
        super().__init__("Markdown to HTML Converter", parent)
    
    def setup_form(self):
        # File input section
        self.add_file_input_section(
            self.converter.SUPPORTED_INPUT_FORMATS,
            "Input Markdown File"
        )
        
        # Add output section
        self.add_output_section(
            default_format="html",
            formats=self.converter.SUPPORTED_OUTPUT_FORMATS
        )
        
        # Add styling options
        style_group = QGroupBox("Styling Options")
        style_layout = QVBoxLayout(style_group)
        
        # Title option
        title_layout = QHBoxLayout()
        title_label = QLabel("Document Title:")
        title_layout.addWidget(title_label)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Auto (use filename)")
        title_layout.addWidget(self.title_edit)
        
        style_layout.addLayout(title_layout)
        
        # CSS option
        self.use_default_css = QCheckBox("Use Default CSS Styling")
        self.use_default_css.setChecked(True)
        style_layout.addWidget(self.use_default_css)
        
        self.form_layout.addWidget(style_group)
    
    def start_conversion(self):
        """Start the Markdown to HTML conversion process."""
        if not self.input_file:
            return
        
        # Get output path
        if self.output_dir:
            filename = FileHandler.get_filename(self.input_file)
            output_path = os.path.join(self.output_dir, f"{filename}.html")
        else:
            output_path = None
        
        # Get title if provided
        title = self.title_edit.text().strip() or None
        
        # Set UI to busy state
        self.set_busy(True)
        
        # Create worker thread
        self.worker = ConversionWorker(
            self.converter.convert_md_to_html,
            [self.input_file],
            {
                'output_path': output_path,
                'title': title,
                'use_default_css': self.use_default_css.isChecked()
            }
        )
        
        # Connect signals
        self.worker.signals.result.connect(self.conversion_complete)
        self.worker.signals.error.connect(self.conversion_error)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        
        # Start the worker thread
        self.worker.start()


class HtmlToPdfTab(ConverterTabBase):
    """Tab for converting HTML to PDF."""
    
    def __init__(self, parent=None):
        self.converter = HtmlToPdfConverter()
        super().__init__("HTML to PDF Converter", parent)
    
    def setup_form(self):
        # File input section
        self.add_file_input_section(
            self.converter.SUPPORTED_INPUT_FORMATS,
            "Input HTML File"
        )
        
        # Add output section
        self.add_output_section(
            default_format="pdf",
            formats=self.converter.SUPPORTED_OUTPUT_FORMATS
        )
    
    def start_conversion(self):
        """Start the HTML to PDF conversion process."""
        if not self.input_file:
            return
        
        # Get output path
        if self.output_dir:
            filename = FileHandler.get_filename(self.input_file)
            output_path = os.path.join(self.output_dir, f"{filename}.pdf")
        else:
            output_path = None
        
        # Set UI to busy state
        self.set_busy(True)
        
        # Create worker thread
        self.worker = ConversionWorker(
            self.converter.convert_html_to_pdf,
            [self.input_file],
            {'output_path': output_path}
        )
        
        # Connect signals
        self.worker.signals.result.connect(self.conversion_complete)
        self.worker.signals.error.connect(self.conversion_error)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        
        # Start the worker thread
        self.worker.start()


class MarkdownToPdfTab(ConverterTabBase):
    """Tab for converting Markdown to PDF."""
    
    def __init__(self, parent=None):
        self.converter = MarkdownToPdfConverter()
        super().__init__("Markdown to PDF Converter", parent)
    
    def setup_form(self):
        # File input section
        self.add_file_input_section(
            self.converter.SUPPORTED_INPUT_FORMATS,
            "Input Markdown File"
        )
        
        # Add output section
        self.add_output_section(
            default_format="pdf",
            formats=self.converter.SUPPORTED_OUTPUT_FORMATS
        )
        
        # Add styling options
        style_group = QGroupBox("Styling Options")
        style_layout = QVBoxLayout(style_group)
        
        # Title option
        title_layout = QHBoxLayout()
        title_label = QLabel("Document Title:")
        title_layout.addWidget(title_label)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Auto (use filename)")
        title_layout.addWidget(self.title_edit)
        
        style_layout.addLayout(title_layout)
        
        # CSS option
        self.use_default_css = QCheckBox("Use Default CSS Styling")
        self.use_default_css.setChecked(True)
        style_layout.addWidget(self.use_default_css)
        
        # Keep HTML option
        self.keep_html = QCheckBox("Keep intermediate HTML file")
        self.keep_html.setChecked(False)
        style_layout.addWidget(self.keep_html)
        
        self.form_layout.addWidget(style_group)
    
    def start_conversion(self):
        """Start the Markdown to PDF conversion process."""
        if not self.input_file:
            return
        
        # Get output path
        if self.output_dir:
            filename = FileHandler.get_filename(self.input_file)
            output_path = os.path.join(self.output_dir, f"{filename}.pdf")
        else:
            output_path = None
        
        # Get title if provided
        title = self.title_edit.text().strip() or None
        
        # Set UI to busy state
        self.set_busy(True)
        
        # Create worker thread
        self.worker = ConversionWorker(
            self.converter.convert_md_to_pdf,
            [self.input_file],
            {
                'output_path': output_path,
                'title': title,
                'use_default_css': self.use_default_css.isChecked(),
                'keep_html': self.keep_html.isChecked()
            }
        )
        
        # Connect signals
        self.worker.signals.result.connect(self.conversion_complete)
        self.worker.signals.error.connect(self.conversion_error)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        
        # Start the worker thread
        self.worker.start()


class MainWindow(QMainWindow):
    """
    Main application window with tabs for different converters.
    """
    def __init__(self):
        super().__init__()
        
        # Set up application preferences
        self.settings = QSettings("FileConverter", "FileConverter")
        
        # Initialize UI
        self.setup_ui()
        
        # Apply user preferences
        self.load_settings()
        
        # Set up error handler and logging
        ErrorHandler.setup_logging()
    
    def setup_ui(self):
        """Set up the main window UI."""
        # Window setup
        self.setWindowTitle("File Converter")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create converter tabs that are always available
        self.image_tab = ImageConverterTab()
        self.pdf_word_tab = PdfToWordTab()
        self.md_html_tab = MarkdownToHtmlTab()
        
        # Add always-available tabs
        self.tab_widget.addTab(self.image_tab, "Image Converter")
        self.tab_widget.addTab(self.pdf_word_tab, "PDF to Word")
        self.tab_widget.addTab(self.md_html_tab, "Markdown to HTML")
        
        # Check if HTML to PDF conversion is available (depends on WeasyPrint)
        html_to_pdf_available = HtmlToPdfConverter.is_available()
        md_to_pdf_available = MarkdownToPdfConverter.is_available()
        
        # Conditionally create and add tabs that depend on WeasyPrint
        if html_to_pdf_available:
            self.html_pdf_tab = HtmlToPdfTab()
            self.tab_widget.addTab(self.html_pdf_tab, "HTML to PDF")
        else:
            self.html_pdf_tab = None
            
        if md_to_pdf_available:
            self.md_pdf_tab = MarkdownToPdfTab()
            self.tab_widget.addTab(self.md_pdf_tab, "Markdown to PDF")
        else:
            self.md_pdf_tab = None
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Show message if some converters are not available
        if not html_to_pdf_available or not md_to_pdf_available:
            message = "Some conversion features are not available due to missing dependencies. "
            message += "To enable HTML to PDF and Markdown to PDF conversion, please install WeasyPrint and its dependencies."
            QTimer.singleShot(500, lambda: QMessageBox.warning(self, "Missing Dependencies", message))
    
    def load_settings(self):
        """Load and apply user settings."""
        # Window geometry
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            # Default window position and size
            self.resize(900, 700)
            self.center_on_screen()
        
        # Theme
        theme_value = self.settings.value("theme", AppTheme.SYSTEM.value)
        theme = AppTheme(int(theme_value)) if isinstance(theme_value, (int, str)) else AppTheme.SYSTEM
        StyleManager.set_app_theme(QApplication.instance(), theme)
        
        # Remember last tab
        last_tab = self.settings.value("last_tab", 0)
        tab_index = int(last_tab) if isinstance(last_tab, (int, str)) else 0
        # Make sure the index is valid
        if 0 <= tab_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(tab_index)
    
    def save_settings(self):
        """Save user settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("last_tab", self.tab_widget.currentIndex())
        
        # Save last used directories for each tab if available
        tab_configs = [
            ("image", self.image_tab), 
            ("pdf_word", self.pdf_word_tab), 
            ("md_html", self.md_html_tab)
        ]
        
        # Add conditional tabs if they exist
        if self.html_pdf_tab:
            tab_configs.append(("html_pdf", self.html_pdf_tab))
        if self.md_pdf_tab:
            tab_configs.append(("md_pdf", self.md_pdf_tab))
        
        # Save directory for each tab
        for tab_name, tab in tab_configs:
            if tab and tab.output_dir:
                self.settings.setValue(f"last_dir_{tab_name}", tab.output_dir)
    
    def center_on_screen(self):
        """Center the window on the screen."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
    
    def closeEvent(self, event):
        """Handle window close event to save settings."""
        # Save settings
        self.save_settings()
        
        # Clean up tab resources for tabs that exist
        tabs = [self.image_tab, self.pdf_word_tab, self.md_html_tab]
        
        # Add conditional tabs if they exist
        if self.html_pdf_tab:
            tabs.append(self.html_pdf_tab)
        if self.md_pdf_tab:
            tabs.append(self.md_pdf_tab)
        
        # Cleanup each tab
        for tab in tabs:
            tab.cleanup()
        
        event.accept() 