import os
from pathlib import Path

class CustomStyleManager:
    """
    Manages custom styles for HTML and PDF conversion.
    """
    
    @staticmethod
    def get_custom_css_path():
        """
        Returns the path to the custom CSS file.
        """
        # Get the path to the utils directory where this file is located
        utils_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Get the path to the custom styles CSS file
        css_path = utils_dir / "custom_styles.css"
        
        return str(css_path)
    
    @staticmethod
    def get_custom_css_content():
        """
        Returns the content of the custom CSS file.
        """
        css_path = CustomStyleManager.get_custom_css_path()
        
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, IOError) as e:
            # Return empty string if the file doesn't exist or can't be read
            return "" 