import os
import logging
import markdown
from typing import Optional, List, Dict, Any, Tuple
from project.utils.error_handler import ErrorHandler
from project.utils.file_handler import FileHandler
from project.utils.style_manager import CustomStyleManager


class MarkdownToHtmlConverter:
    """
    Converts Markdown files to HTML format with customizable
    styling and extension support.
    """
    
    # Supported input formats
    SUPPORTED_INPUT_FORMATS = ["md", "markdown"]
    
    # Supported output formats
    SUPPORTED_OUTPUT_FORMATS = ["html"]
    
    # Text direction options
    TEXT_DIRECTION_LTR = "ltr"
    TEXT_DIRECTION_RTL = "rtl"
    
    # Default Markdown extensions to use
    DEFAULT_EXTENSIONS = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.sane_lists',
        'markdown.extensions.nl2br'
    ]
    
    # Default CSS styles for HTML output - kept for backward compatibility
    DEFAULT_CSS = """
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 900px;
        margin: 0 auto;
        padding: 2em;
    }
    h1, h2, h3, h4, h5, h6 { 
        font-weight: 600;
        margin-top: 24px;
        margin-bottom: 16px;
    }
    h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
    h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
    code {
        font-family: SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace;
        background-color: rgba(27, 31, 35, 0.05);
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-size: 85%;
    }
    pre {
        background-color: #f6f8fa;
        border-radius: 3px;
        padding: 16px;
        overflow: auto;
    }
    pre code {
        background-color: transparent;
        padding: 0;
    }
    blockquote {
        margin: 0;
        padding: 0 1em;
        color: #6a737d;
        border-left: 0.25em solid #dfe2e5;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 16px;
    }
    table th, table td {
        padding: 6px 13px;
        border: 1px solid #dfe2e5;
    }
    table tr:nth-child(2n) {
        background-color: #f6f8fa;
    }
    img {
        max-width: 100%;
    }
    hr {
        height: 0.25em;
        padding: 0;
        margin: 24px 0;
        background-color: #e1e4e8;
        border: 0;
    }
    """
    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """Return dictionary of supported input and output formats."""
        return {
            "input": MarkdownToHtmlConverter.SUPPORTED_INPUT_FORMATS,
            "output": MarkdownToHtmlConverter.SUPPORTED_OUTPUT_FORMATS
        }
    
    @ErrorHandler.handle_exception
    def convert_md_to_html(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        title: Optional[str] = None,
        use_default_css: bool = True,
        custom_css: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        text_direction: Optional[str] = None
    ) -> str:
        """
        Convert Markdown file to HTML.
        
        Args:
            input_path: Path to the input Markdown file
            output_path: Path to save the output HTML file (if None, will be generated)
            title: HTML document title (if None, uses filename)
            use_default_css: Whether to include default CSS styles
            custom_css: Optional custom CSS styles to include
            extensions: Optional list of Markdown extensions to use
            text_direction: Text direction for the HTML (ltr or rtl)
            
        Returns:
            Path to the converted HTML file
            
        Raises:
            ValueError: If input file is not a supported format
            FileNotFoundError: If input file doesn't exist
            OSError: If there's an issue writing the output file
        """
        # Validate input file
        valid, error_msg = FileHandler.validate_file(
            input_path, 
            MarkdownToHtmlConverter.SUPPORTED_INPUT_FORMATS
        )
        if not valid:
            raise ValueError(error_msg)
        
        # Generate output path if not provided
        if not output_path:
            output_dir = FileHandler.get_directory(input_path)
            output_path = FileHandler.generate_output_path(input_path, output_dir, "html")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        FileHandler.ensure_directory_exists(output_dir)
        
        # Determine document title
        if not title:
            title = FileHandler.get_filename(input_path)
        
        # Use default or provided extensions
        md_extensions = extensions if extensions else MarkdownToHtmlConverter.DEFAULT_EXTENSIONS
        
        # Read markdown content
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_body = markdown.markdown(md_content, extensions=md_extensions)
        
        # Create complete HTML document
        css = ""
        # Use custom styles from CustomStyleManager instead of default CSS
        if use_default_css:
            custom_css_content = CustomStyleManager.get_custom_css_content()
            if custom_css_content:
                css += f"<style>{custom_css_content}</style>"
            else:
                # Fallback to DEFAULT_CSS if custom styles not available
                css += f"<style>{MarkdownToHtmlConverter.DEFAULT_CSS}</style>"
                
        # Add any additional custom CSS
        if custom_css:
            css += f"<style>{custom_css}</style>"
            
        # Add direction CSS if specified
        direction_attr = ""
        direction_css = ""
        if text_direction:
            direction_attr = f' dir="{text_direction}"'
            direction_css = f"<style>html, body {{ direction: {text_direction}; }}</style>"
            css += direction_css
        
        html_content = f"""<!DOCTYPE html>
<html lang="en"{direction_attr}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {css}
</head>
<body{direction_attr}>
{html_body}
</body>
</html>
"""
        
        # Write HTML to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logging.info(f"Converted {input_path} to {output_path}")
        return output_path
    
    @ErrorHandler.handle_exception
    def batch_convert(
        self,
        input_files: List[str],
        output_dir: str,
        use_default_css: bool = True,
        custom_css: Optional[str] = None,
        text_direction: Optional[str] = None
    ) -> List[str]:
        """
        Convert multiple Markdown files to HTML.
        
        Args:
            input_files: List of paths to input Markdown files
            output_dir: Directory to save converted HTML files
            use_default_css: Whether to include default CSS styles
            custom_css: Optional custom CSS to include
            text_direction: Text direction for the HTML (ltr or rtl)
            
        Returns:
            List of paths to the converted HTML files
        """
        FileHandler.ensure_directory_exists(output_dir)
        
        converted_files = []
        for input_file in input_files:
            # Generate output path
            filename = FileHandler.get_filename(input_file)
            output_path = os.path.join(output_dir, f"{filename}.html")
            
            # Convert the Markdown file
            try:
                result = self.convert_md_to_html(
                    input_file, 
                    output_path,
                    use_default_css=use_default_css,
                    custom_css=custom_css,
                    text_direction=text_direction
                )
                
                converted_files.append(result)
            except Exception as e:
                logging.error(f"Failed to convert {input_file}: {str(e)}")
        
        return converted_files 