import os
import logging
from typing import Optional, List, Dict, Any, Tuple
from pdf2docx import Converter
from project.utils.error_handler import ErrorHandler
from project.utils.file_handler import FileHandler


class PdfToWordConverter:
    """
    Converts PDF files to Word (DOCX) format,
    preserving formatting and layout as much as possible.
    """
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = ["pdf"]
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = ["docx"]
    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """Return dictionary of supported input and output formats."""
        return {
            "input": PdfToWordConverter.SUPPORTED_INPUT_FORMATS,
            "output": PdfToWordConverter.SUPPORTED_OUTPUT_FORMATS
        }
    
    @ErrorHandler.handle_exception
    def convert_pdf_to_word(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        start_page: int = 0,
        end_page: Optional[int] = None,
        pages: Optional[List[int]] = None
    ) -> str:
        """
        Convert PDF to Word document (DOCX format).
        
        Args:
            input_path: Path to the input PDF file
            output_path: Path to save the output DOCX file (if None, will be generated)
            start_page: First page to convert (0-based indexing)
            end_page: Last page to convert (None means convert to the end)
            pages: Specific page numbers to convert (overrides start_page/end_page if provided)
            
        Returns:
            Path to the converted Word document
            
        Raises:
            ValueError: If input file is not a supported format
            FileNotFoundError: If input file doesn't exist
            OSError: If there's an issue writing the output file
        """
        # Validate input file
        valid, error_msg = FileHandler.validate_file(
            input_path, 
            PdfToWordConverter.SUPPORTED_INPUT_FORMATS
        )
        if not valid:
            raise ValueError(error_msg)
        
        # Generate output path if not provided
        if not output_path:
            output_dir = FileHandler.get_directory(input_path)
            output_path = FileHandler.generate_output_path(input_path, output_dir, "docx")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        FileHandler.ensure_directory_exists(output_dir)
        
        # Configure page range
        if pages:
            # Convert to a list of 0-based indices
            page_indices = [p - 1 if p > 0 else 0 for p in pages]
        else:
            # Use start_page and end_page (end_page is exclusive)
            page_indices = None
        
        # Create PDF to DOCX converter
        cv = Converter(input_path)
        
        try:
            # Convert PDF to DOCX
            if pages:
                # Convert specific pages
                cv.convert(output_path, pages=page_indices)
            else:
                # Convert page range
                cv.convert(output_path, start=start_page, end=end_page)
            
            logging.info(f"Converted {input_path} to {output_path}")
            return output_path
        
        finally:
            # Always close the converter
            cv.close()
    
    @ErrorHandler.handle_exception
    def batch_convert(
        self,
        input_files: List[str],
        output_dir: str
    ) -> List[str]:
        """
        Convert multiple PDF files to Word documents.
        
        Args:
            input_files: List of paths to input PDF files
            output_dir: Directory to save converted documents
            
        Returns:
            List of paths to the converted documents
        """
        FileHandler.ensure_directory_exists(output_dir)
        
        converted_files = []
        for input_file in input_files:
            # Generate output path
            filename = FileHandler.get_filename(input_file)
            output_path = os.path.join(output_dir, f"{filename}.docx")
            
            # Convert the PDF
            success, result = self.convert_pdf_to_word(input_file, output_path)
            
            if success:
                converted_files.append(result)
            else:
                logging.error(f"Failed to convert {input_file}: {result}")
        
        return converted_files 