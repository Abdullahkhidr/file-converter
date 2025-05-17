from PIL import Image
import os
import logging
from typing import List, Tuple, Optional, Dict
from project.utils.error_handler import ErrorHandler
from project.utils.file_handler import FileHandler


class ImageConverter:
    """
    Handles conversions between different image formats including
    PNG, JPEG, BMP, GIF, and TIFF.
    """
    
    # Supported formats
    SUPPORTED_FORMATS = ["png", "jpg", "jpeg", "bmp", "gif", "tiff", "tif"]
    
    # Format-specific options
    FORMAT_OPTIONS: Dict[str, Dict] = {
        "png": {"optimize": True},
        "jpg": {"quality": 95, "optimize": True},
        "jpeg": {"quality": 95, "optimize": True},
        "bmp": {},
        "gif": {},
        "tiff": {"compression": "tiff_lzw"},
        "tif": {"compression": "tiff_lzw"}
    }
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Return list of supported formats."""
        return ImageConverter.SUPPORTED_FORMATS
    
    @ErrorHandler.handle_exception
    def convert_image(
        self, 
        input_path: str, 
        output_path: Optional[str] = None,
        output_format: Optional[str] = None,
        quality: Optional[int] = None
    ) -> str:
        """
        Convert an image from one format to another.
        
        Args:
            input_path: Path to the input image file
            output_path: Path to save the output image file (if None, will be generated)
            output_format: Desired output format (if None, derived from output_path)
            quality: Quality for lossy formats (0-100, where 100 is best)
            
        Returns:
            Path to the converted image
        
        Raises:
            ValueError: If input file is not a supported image format
            FileNotFoundError: If input file doesn't exist
            OSError: If there's an issue writing the output file
        """
        # Validate input file
        valid, error_msg = FileHandler.validate_file(
            input_path, 
            ImageConverter.SUPPORTED_FORMATS
        )
        if not valid:
            raise ValueError(error_msg)
        
        # Get input format
        input_format = FileHandler.get_file_extension(input_path).lower()
        
        # Determine output format
        if output_format:
            output_format = output_format.lower().lstrip(".")
        elif output_path:
            output_format = FileHandler.get_file_extension(output_path).lower()
        else:
            raise ValueError("Either output_path or output_format must be specified")
        
        # Validate output format
        if output_format not in ImageConverter.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported output format: {output_format}. "
                            f"Supported formats are: {', '.join(ImageConverter.SUPPORTED_FORMATS)}")
        
        # Generate output path if not provided
        if not output_path:
            output_dir = FileHandler.get_directory(input_path)
            output_path = FileHandler.generate_output_path(input_path, output_dir, output_format)
        
        # Open the image
        img = Image.open(input_path)
        
        # Handle transparency for JPEG conversion
        if output_format in ["jpg", "jpeg"] and img.mode in ["RGBA", "LA"]:
            # JPEG doesn't support transparency, convert to RGB with white background
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else img.split()[1])
            img = background
        
        # Prepare save options
        save_options = ImageConverter.FORMAT_OPTIONS.get(output_format, {}).copy()
        
        # Override quality if specified
        if quality is not None and output_format in ["jpg", "jpeg"]:
            save_options["quality"] = max(1, min(100, quality))
        
        # Save the image
        img.save(output_path, **save_options)
        logging.info(f"Converted {input_path} to {output_path}")
        
        return output_path
    
    @ErrorHandler.handle_exception
    def batch_convert(
        self, 
        input_files: List[str], 
        output_dir: str,
        output_format: str,
        quality: Optional[int] = None
    ) -> List[str]:
        """
        Convert multiple images to the specified format.
        
        Args:
            input_files: List of paths to input image files
            output_dir: Directory to save converted images
            output_format: Format to convert images to
            quality: Quality for lossy formats (0-100)
            
        Returns:
            List of paths to the converted images
        """
        FileHandler.ensure_directory_exists(output_dir)
        
        converted_files = []
        for input_file in input_files:
            # Generate output path
            filename = FileHandler.get_filename(input_file)
            output_path = os.path.join(output_dir, f"{filename}.{output_format}")
            
            # Convert the image
            _, result = self.convert_image(input_file, output_path, quality=quality)
            
            if isinstance(result, str):  # Success case
                converted_files.append(result)
            else:
                logging.error(f"Failed to convert {input_file}: {result}")
        
        return converted_files
    
    @ErrorHandler.handle_exception
    def resize_image(
        self, 
        input_path: str, 
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect_ratio: bool = True
    ) -> str:
        """
        Resize an image while optionally maintaining aspect ratio.
        
        Args:
            input_path: Path to the input image
            output_path: Path to save the resized image
            width: Target width in pixels (if None, calculated from height)
            height: Target height in pixels (if None, calculated from width)
            maintain_aspect_ratio: Whether to maintain the original aspect ratio
            
        Returns:
            Path to the resized image
        """
        if not width and not height:
            raise ValueError("At least one of width or height must be specified")
        
        # Validate input file
        valid, error_msg = FileHandler.validate_file(
            input_path, 
            ImageConverter.SUPPORTED_FORMATS
        )
        if not valid:
            raise ValueError(error_msg)
        
        # Open the image
        img = Image.open(input_path)
        original_width, original_height = img.size
        
        # Calculate new dimensions
        if maintain_aspect_ratio:
            if width and height:
                # Use the smallest scale factor to fit within the requested dimensions
                width_ratio = width / original_width
                height_ratio = height / original_height
                ratio = min(width_ratio, height_ratio)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
            elif width:
                # Calculate height to maintain aspect ratio
                ratio = width / original_width
                new_width = width
                new_height = int(original_height * ratio)
            else:  # height is specified
                # Calculate width to maintain aspect ratio
                ratio = height / original_height
                new_height = height
                new_width = int(original_width * ratio)
        else:
            # Use specified dimensions, or original if not specified
            new_width = width if width else original_width
            new_height = height if height else original_height
        
        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Determine output format based on extension
        output_format = FileHandler.get_file_extension(output_path).lower()
        save_options = ImageConverter.FORMAT_OPTIONS.get(output_format, {})
        
        # Handle transparency for JPEG
        if output_format in ["jpg", "jpeg"] and resized_img.mode in ["RGBA", "LA"]:
            background = Image.new("RGB", resized_img.size, (255, 255, 255))
            background.paste(resized_img, mask=resized_img.split()[3] if resized_img.mode == "RGBA" else resized_img.split()[1])
            resized_img = background
        
        # Save the resized image
        resized_img.save(output_path, **save_options)
        
        return output_path 