import os
import logging
import tempfile
from typing import Optional, List, Dict, Any, Union
from project.utils.error_handler import ErrorHandler
from project.utils.file_handler import FileHandler
from project.converters.md_to_html import MarkdownToHtmlConverter
from project.converters.html_to_pdf import HtmlToPdfConverter


class MarkdownToPdfConverter:
    """
    Converts Markdown files to PDF format by first converting to HTML,
    then converting the HTML to PDF.
    """
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = ["md", "markdown"]
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = ["pdf"]
    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """Return dictionary of supported input and output formats."""
        return {
            "input": MarkdownToPdfConverter.SUPPORTED_INPUT_FORMATS,
            "output": MarkdownToPdfConverter.SUPPORTED_OUTPUT_FORMATS
        }
    
    @staticmethod
    def is_available() -> bool:
        """Check if Markdown to PDF conversion is available."""
        # This converter depends on HtmlToPdfConverter
        return HtmlToPdfConverter.is_available()
    
    def __init__(self):
        """Initialize the converters needed for the conversion pipeline."""
        self.md_to_html = MarkdownToHtmlConverter()
        self.html_to_pdf = HtmlToPdfConverter()
    
    @ErrorHandler.handle_exception
    def convert_md_to_pdf(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        title: Optional[str] = None,
        use_default_css: bool = True,
        custom_css: Optional[str] = None,
        keep_html: bool = False,
        html_path: Optional[str] = None,
        pdf_options: Optional[Dict[str, Any]] = None,
        text_direction: Optional[str] = None
    ) -> str:
        """
        Convert Markdown file to PDF.
        
        Args:
            input_path: Path to the input Markdown file
            output_path: Path to save the output PDF file (if None, will be generated)
            title: HTML document title (if None, uses filename)
            use_default_css: Whether to include default CSS styles
            custom_css: Optional custom CSS styles to include
            keep_html: Whether to keep the intermediate HTML file
            html_path: Path to save the intermediate HTML file (if keep_html is True)
            pdf_options: Optional rendering options for PDF conversion
            text_direction: Text direction for the document (ltr or rtl)
            
        Returns:
            Path to the converted PDF file
            
        Raises:
            ValueError: If input file is not a supported format
            FileNotFoundError: If input file doesn't exist
            OSError: If there's an issue writing the output file
            RuntimeError: If HTML to PDF conversion is not available
        """
        # Check if HTML to PDF conversion is available
        if not HtmlToPdfConverter.is_available():
            raise RuntimeError(
                "HTML to PDF conversion is not available. Please install all required dependencies for WeasyPrint to use this feature."
            )
            
        # Validate input file
        valid, error_msg = FileHandler.validate_file(
            input_path, 
            MarkdownToPdfConverter.SUPPORTED_INPUT_FORMATS
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
        
        # Generate HTML path if keeping HTML and path not provided
        if keep_html and not html_path:
            html_path = FileHandler.generate_output_path(input_path, output_dir, "html")
        
        # If not keeping HTML, use a temporary file
        if not keep_html:
            # Create temporary file for HTML content
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
                html_path = f.name
        
        try:
            # Step 1: Convert Markdown to HTML
            html_result = self.md_to_html.convert_md_to_html(
                input_path, 
                html_path,
                title=title,
                use_default_css=use_default_css,
                custom_css=custom_css,
                text_direction=text_direction
            )
            
            # Step 2: Convert HTML to PDF
            # For the PDF conversion, we use the custom CSS if enabled in the GUI
            # since the HTML already has the styles from the first conversion step
            pdf_result = self.html_to_pdf.convert_html_to_pdf(
                html_path, 
                output_path,
                options=pdf_options,
                text_direction=text_direction,
                use_custom_css=False  # Don't apply it twice
            )
            
            logging.info(f"Converted {input_path} to {output_path}")
            return pdf_result
        
        finally:
            # Clean up temporary HTML file if we're not keeping it
            if not keep_html and html_path and os.path.exists(html_path):
                os.unlink(html_path)
    
    @ErrorHandler.handle_exception
    def batch_convert(
        self,
        input_files: List[str],
        output_dir: str,
        use_default_css: bool = True,
        custom_css: Optional[str] = None,
        keep_html: bool = False,
        text_direction: Optional[str] = None
    ) -> List[str]:
        """
        Convert multiple Markdown files to PDF.
        
        Args:
            input_files: List of paths to input Markdown files
            output_dir: Directory to save converted PDF files
            use_default_css: Whether to include default CSS styles
            custom_css: Optional custom CSS to include
            keep_html: Whether to keep intermediate HTML files
            text_direction: Text direction for the documents (ltr or rtl)
            
        Returns:
            List of paths to the converted PDF files
            
        Raises:
            RuntimeError: If HTML to PDF conversion is not available
        """
        # Check if HTML to PDF conversion is available
        if not HtmlToPdfConverter.is_available():
            raise RuntimeError(
                "HTML to PDF conversion is not available. Please install all required dependencies for WeasyPrint to use this feature."
            )
            
        FileHandler.ensure_directory_exists(output_dir)
        
        converted_files = []
        for input_file in input_files:
            # Generate output paths
            filename = FileHandler.get_filename(input_file)
            pdf_path = os.path.join(output_dir, f"{filename}.pdf")
            html_path = os.path.join(output_dir, f"{filename}.html") if keep_html else None
            
            try:
                # Convert the Markdown file to PDF
                result = self.convert_md_to_pdf(
                    input_file, 
                    pdf_path,
                    use_default_css=use_default_css,
                    custom_css=custom_css,
                    keep_html=keep_html,
                    html_path=html_path,
                    text_direction=text_direction
                )
                
                converted_files.append(result)
            except Exception as e:
                logging.error(f"Failed to convert {input_file}: {str(e)}")
        
        return converted_files 