import os
import pytest
import tempfile
from pathlib import Path
from PIL import Image
from project.converters.image_converter import ImageConverter


class TestImageConverter:
    """Tests for the ImageConverter class."""
    
    @pytest.fixture
    def converter(self):
        """Create an ImageConverter instance for tests."""
        return ImageConverter()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield tmpdirname
    
    @pytest.fixture
    def test_image_file(self, temp_dir):
        """Create a test image file."""
        # Create a simple test image
        img_path = os.path.join(temp_dir, "test_image.png")
        img = Image.new('RGB', (100, 100), color='red')
        img.save(img_path)
        yield img_path
    
    def test_supported_formats(self, converter):
        """Test that the converter has the expected supported formats."""
        formats = converter.get_supported_formats()
        assert isinstance(formats, list)
        assert "png" in formats
        assert "jpg" in formats
        assert "jpeg" in formats
        assert "bmp" in formats
        assert "gif" in formats
        assert "tiff" in formats
    
    def test_convert_png_to_jpg(self, converter, test_image_file, temp_dir):
        """Test converting a PNG to JPG."""
        output_path = os.path.join(temp_dir, "test_output.jpg")
        
        # Convert the image
        success, result = converter.convert_image(test_image_file, output_path)
        
        # Check results
        assert success is True
        assert os.path.exists(result)
        assert result == output_path
        
        # Verify the output is a valid JPG
        img = Image.open(result)
        assert img.format == "JPEG"
    
    def test_convert_with_auto_output_path(self, converter, test_image_file, temp_dir):
        """Test converting with auto-generated output path."""
        # Convert the image
        success, result = converter.convert_image(
            test_image_file, 
            output_format="jpg"
        )
        
        # Check results
        assert success is True
        assert os.path.exists(result)
        assert result.endswith(".jpg")
        
        # Verify the output is a valid JPG
        img = Image.open(result)
        assert img.format == "JPEG"
    
    def test_batch_convert(self, converter, test_image_file, temp_dir):
        """Test batch conversion of images."""
        # Create a second test image
        img_path2 = os.path.join(temp_dir, "test_image2.png")
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(img_path2)
        
        # Batch convert
        success, result = converter.batch_convert(
            [test_image_file, img_path2],
            temp_dir,
            "jpg"
        )
        
        # Check results
        assert success is True
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Verify output files exist and are valid
        for output_path in result:
            assert os.path.exists(output_path)
            assert output_path.endswith(".jpg")
            img = Image.open(output_path)
            assert img.format == "JPEG"
    
    def test_resize_image(self, converter, test_image_file, temp_dir):
        """Test resizing an image."""
        output_path = os.path.join(temp_dir, "test_resized.png")
        
        # Resize the image
        success, result = converter.resize_image(
            test_image_file,
            output_path,
            width=50,
            height=50
        )
        
        # Check results
        assert success is True
        assert os.path.exists(result)
        
        # Verify dimensions
        img = Image.open(result)
        assert img.width == 50
        assert img.height == 50
    
    def test_invalid_input_file(self, converter, temp_dir):
        """Test handling of invalid input files."""
        non_existent_file = os.path.join(temp_dir, "nonexistent.png")
        
        # Try to convert non-existent file
        success, result = converter.convert_image(
            non_existent_file,
            os.path.join(temp_dir, "output.jpg")
        )
        
        # Check results
        assert success is False
        assert "not exist" in result.lower()
    
    def test_invalid_output_format(self, converter, test_image_file, temp_dir):
        """Test handling of invalid output formats."""
        # Try to convert to invalid format
        success, result = converter.convert_image(
            test_image_file,
            output_format="invalid"
        )
        
        # Check results
        assert success is False
        assert "unsupported" in result.lower() 