import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import logging


class FileHandler:
    """Utility class for handling file operations across the application."""
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Return the file extension without the dot."""
        return os.path.splitext(file_path)[1][1:].lower()
    
    @staticmethod
    def get_filename(file_path: str) -> str:
        """Return the filename without extension."""
        return os.path.splitext(os.path.basename(file_path))[0]
    
    @staticmethod
    def get_directory(file_path: str) -> str:
        """Return the directory containing the file."""
        return os.path.dirname(file_path)
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        """Create directory if it doesn't exist."""
        os.makedirs(directory_path, exist_ok=True)
    
    @staticmethod
    def generate_output_path(input_path: str, output_dir: Optional[str], new_extension: str) -> str:
        """Generate output file path with new extension in the specified directory."""
        filename = FileHandler.get_filename(input_path)
        
        # If no output directory specified, use the same as input
        if not output_dir:
            output_dir = FileHandler.get_directory(input_path)
        
        # Ensure output directory exists
        FileHandler.ensure_directory_exists(output_dir)
        
        return os.path.join(output_dir, f"{filename}.{new_extension}")
    
    @staticmethod
    def copy_file(source: str, destination: str) -> None:
        """Copy a file from source to destination."""
        shutil.copy2(source, destination)
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file and return True if successful."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {str(e)}")
            return False
        return False
    
    @staticmethod
    def get_files_with_extensions(directory: str, extensions: List[str]) -> List[str]:
        """Get all files in a directory with specified extensions."""
        files = []
        for ext in extensions:
            # Normalize extension format (with or without dot)
            clean_ext = ext.lower().lstrip(".")
            pattern = f"*.{clean_ext}"
            
            # Find and add matching files
            path = Path(directory)
            files.extend([str(f) for f in path.glob(pattern)])
        
        return files
    
    @staticmethod
    def validate_file(file_path: str, allowed_extensions: List[str]) -> Tuple[bool, str]:
        """
        Validate if a file exists and has an allowed extension.
        Returns a tuple (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
            
        if not os.path.isfile(file_path):
            return False, f"Not a file: {file_path}"
            
        ext = FileHandler.get_file_extension(file_path)
        if allowed_extensions and ext not in [e.lower().lstrip(".") for e in allowed_extensions]:
            return False, f"Unsupported file extension: {ext}. Allowed: {', '.join(allowed_extensions)}"
            
        return True, ""
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Return file size in bytes."""
        return os.path.getsize(file_path)
    
    @staticmethod
    def save_user_preferences(prefs_dict: dict, file_path: str = None) -> None:
        """Save user preferences to a file."""
        import json
        
        if file_path is None:
            # Default to user's home directory
            file_path = os.path.join(os.path.expanduser("~"), ".fileconverter_prefs.json")
            
        try:
            with open(file_path, 'w') as f:
                json.dump(prefs_dict, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving preferences: {str(e)}")
    
    @staticmethod
    def load_user_preferences(file_path: str = None) -> dict:
        """Load user preferences from a file."""
        import json
        
        if file_path is None:
            # Default to user's home directory
            file_path = os.path.join(os.path.expanduser("~"), ".fileconverter_prefs.json")
            
        if not os.path.exists(file_path):
            return {}
            
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading preferences: {str(e)}")
            return {} 