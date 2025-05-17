import os
import logging
import tempfile
import warnings
from typing import Optional, List, Dict, Tuple, Any, Union
from project.utils.error_handler import ErrorHandler
from project.utils.file_handler import FileHandler

# Try to import WeasyPrint, but make it optional
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    warnings.warn(f"WeasyPrint is not available: {e}. HTML to PDF conversion will be disabled.")


class HtmlToPdfConverter:
    """
    Converts HTML files to PDF format with customizable
    styling and rendering options.
    """
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = ["html", "htm"]
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = ["pdf"]
    
    # Text direction options
    TEXT_DIRECTION_LTR = "ltr"
    TEXT_DIRECTION_RTL = "rtl"
    
    # Default rendering options
    DEFAULT_OPTIONS = {
        "presentational_hints": True,
        "optimize_size": ('fonts', 'images'),
    }
    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """Return dictionary of supported input and output formats."""
        return {
            "input": HtmlToPdfConverter.SUPPORTED_INPUT_FORMATS,
            "output": HtmlToPdfConverter.SUPPORTED_OUTPUT_FORMATS
        }
    
    @staticmethod
    def is_available() -> bool:
        """Check if HTML to PDF conversion is available."""
        return WEASYPRINT_AVAILABLE
    
    @ErrorHandler.handle_exception
    def convert_html_to_pdf(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        stylesheet: Optional[Union[str, List[str]]] = None,
        base_url: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        text_direction: Optional[str] = None
    ) -> str:
        """
        Convert HTML file to PDF.
        
        Args:
            input_path: Path to the input HTML file
            output_path: Path to save the output PDF file (if None, will be generated)
            stylesheet: Optional CSS stylesheets to apply (file path or list of paths)
            base_url: Base URL to resolve relative URLs in the HTML
            options: Optional rendering options
            text_direction: Text direction for the PDF (ltr or rtl)
            
        Returns:
            Path to the converted PDF file
            
        Raises:
            ValueError: If input file is not a supported format
            FileNotFoundError: If input file doesn't exist
            OSError: If there's an issue writing the output file
            RuntimeError: If WeasyPrint is not available
        """
        # Check if WeasyPrint is available
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "WeasyPrint is not available. Please install all required dependencies for WeasyPrint to use this feature."
            )
            
        # Validate input file
        valid, error_msg = FileHandler.validate_file(
            input_path, 
            HtmlToPdfConverter.SUPPORTED_INPUT_FORMATS
        )
        if not valid:
            raise ValueError(error_msg)
        
        # Generate output path if not provided
        if not output_path:
            output_dir = FileHandler.get_directory(input_path)
            output_path = FileHandler.generate_output_path(input_path, output_dir, "pdf")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        FileHandler.ensure_directory_exists(output_dir)
        
        # Set base URL if not provided
        if not base_url:
            # Set base URL to the directory containing the HTML file
            base_url = f"file://{os.path.abspath(os.path.dirname(input_path))}"
        
        # Set options
        render_options = HtmlToPdfConverter.DEFAULT_OPTIONS.copy()
        if options:
            render_options.update(options)
        
        # Load CSS if provided
        css_list = []
        if stylesheet:
            if isinstance(stylesheet, str):
                css_list = [weasyprint.CSS(filename=stylesheet)]
            else:
                css_list = [weasyprint.CSS(filename=css_file) for css_file in stylesheet]
        
        # Apply text direction if specified
        if text_direction:
            # Create a CSS object with the direction property
            direction_css = weasyprint.CSS(string=f"html, body {{ direction: {text_direction}; }}")
            css_list.append(direction_css)
            
        # Load HTML and write to PDF
        html = weasyprint.HTML(filename=input_path, base_url=base_url)
        html.write_pdf(output_path, stylesheets=css_list if css_list else None, **render_options)
        
        logging.info(f"Converted {input_path} to {output_path}")
        return output_path
    
    @ErrorHandler.handle_exception
    def convert_html_string_to_pdf(
        self,
        html_string: str,
        output_path: str,
        stylesheet: Optional[Union[str, List[str]]] = None,
        base_url: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        text_direction: Optional[str] = None
    ) -> str:
        """
        Convert HTML string to PDF.
        
        Args:
            html_string: HTML content as a string
            output_path: Path to save the output PDF file
            stylesheet: Optional CSS stylesheets to apply (file path or list of paths)
            base_url: Base URL to resolve relative URLs in the HTML
            options: Optional rendering options
            text_direction: Text direction for the PDF (ltr or rtl)
            
        Returns:
            Path to the converted PDF file
            
        Raises:
            RuntimeError: If WeasyPrint is not available
        """
        # Check if WeasyPrint is available
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "WeasyPrint is not available. Please install all required dependencies for WeasyPrint to use this feature."
            )
            
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        FileHandler.ensure_directory_exists(output_dir)
        
        # Set options
        render_options = HtmlToPdfConverter.DEFAULT_OPTIONS.copy()
        if options:
            render_options.update(options)
        
        # Load CSS if provided
        css_list = []
        if stylesheet:
            if isinstance(stylesheet, str):
                css_list = [weasyprint.CSS(filename=stylesheet)]
            else:
                css_list = [weasyprint.CSS(filename=css_file) for css_file in stylesheet]
        
        # Apply text direction if specified
        if text_direction:
            # Create a CSS object with the direction property
            direction_css = weasyprint.CSS(string=f"html, body {{ direction: {text_direction}; }}")
            css_list.append(direction_css)
            
        # Create temporary file for HTML content
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', encoding='utf-8', delete=False) as f:
            f.write(html_string)
            temp_html_path = f.name
        
        try:
            # Set base URL if not provided
            if not base_url:
                # Set base URL to the current working directory
                base_url = f"file://{os.path.abspath(os.getcwd())}"
            
            # Load HTML and write to PDF
            html = weasyprint.HTML(filename=temp_html_path, base_url=base_url)
            html.write_pdf(output_path, stylesheets=css_list if css_list else None, **render_options)
            
            logging.info(f"Converted HTML string to {output_path}")
            return output_path
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_html_path):
                os.unlink(temp_html_path)
    
    @ErrorHandler.handle_exception
    def batch_convert(
        self,
        input_files: List[str],
        output_dir: str,
        stylesheet: Optional[Union[str, List[str]]] = None,
        text_direction: Optional[str] = None
    ) -> List[str]:
        """
        Convert multiple HTML files to PDF.
        
        Args:
            input_files: List of paths to input HTML files
            output_dir: Directory to save converted PDF files
            stylesheet: Optional CSS stylesheet(s) to apply
            text_direction: Text direction for the PDF (ltr or rtl)
            
        Returns:
            List of paths to the converted PDF files
            
        Raises:
            RuntimeError: If WeasyPrint is not available
        """
        # Check if WeasyPrint is available
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "WeasyPrint is not available. Please install all required dependencies for WeasyPrint to use this feature."
            )
            
        FileHandler.ensure_directory_exists(output_dir)
        
        converted_files = []
        for input_file in input_files:
            # Generate output path
            filename = FileHandler.get_filename(input_file)
            output_path = os.path.join(output_dir, f"{filename}.pdf")
            
            # Convert the HTML file
            converted_path = self.convert_html_to_pdf(
                input_file, 
                output_path,
                stylesheet=stylesheet,
                text_direction=text_direction
            )
            
            if converted_path:
                converted_files.append(converted_path)
            else:
                logging.error(f"Failed to convert {input_file}")
        
        return converted_files 