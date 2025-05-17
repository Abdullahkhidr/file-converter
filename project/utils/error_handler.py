import logging
import traceback
import sys
from typing import Callable, Optional, Dict, Any, Tuple
from enum import Enum
import os


class ErrorLevel(Enum):
    """Error severity levels."""
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


class ErrorHandler:
    """
    Centralized error handling for the application.
    Provides consistent error handling, logging, and user-friendly messages.
    """
    
    # Dictionary to map exceptions to user-friendly messages
    ERROR_MESSAGES: Dict[type, str] = {
        FileNotFoundError: "The specified file could not be found.",
        PermissionError: "You don't have permission to access this file.",
        OSError: "A system error occurred. Please check your file access permissions.",
        ValueError: "Invalid value provided for the operation.",
        TypeError: "Incorrect type of data provided for the operation.",
        Exception: "An unexpected error occurred."
    }
    
    # Setup logging
    @staticmethod
    def setup_logging(log_file: Optional[str] = None) -> None:
        """
        Configure the logging system.
        
        Args:
            log_file: Path to log file. If None, logs to a default location.
        """
        if log_file is None:
            # Default log file in user's home directory
            log_dir = os.path.join(os.path.expanduser("~"), ".fileconverter")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "fileconverter.log")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    @staticmethod
    def get_error_message(exception: Exception) -> str:
        """
        Get a user-friendly error message for the given exception.
        
        Args:
            exception: The exception to convert to a message
            
        Returns:
            A user-friendly error message
        """
        # First look for an exact type match
        if type(exception) in ErrorHandler.ERROR_MESSAGES:
            message = ErrorHandler.ERROR_MESSAGES[type(exception)]
        else:
            # Look for parent classes
            for exc_type, msg in ErrorHandler.ERROR_MESSAGES.items():
                if isinstance(exception, exc_type):
                    message = msg
                    break
            else:
                message = ErrorHandler.ERROR_MESSAGES[Exception]
        
        # Add specific error details if available
        if str(exception):
            message = f"{message} Details: {str(exception)}"
            
        return message
    
    @staticmethod
    def log_exception(exception: Exception, context: str = "") -> str:
        """
        Log an exception with context and return a user-friendly message.
        
        Args:
            exception: The exception to log
            context: Additional context about where the error occurred
            
        Returns:
            A user-friendly error message
        """
        if context:
            logging.error(f"Error in {context}: {str(exception)}")
        else:
            logging.error(f"Error: {str(exception)}")
            
        # Log the stack trace
        logging.debug(traceback.format_exc())
        
        return ErrorHandler.get_error_message(exception)
    
    @staticmethod
    def handle_exception(func: Callable) -> Callable:
        """
        Decorator for handling exceptions in functions.
        Logs exceptions and returns a tuple (success, result/error_message).
        
        Args:
            func: The function to wrap with error handling
            
        Returns:
            Wrapped function that catches exceptions
        """
        def wrapper(*args, **kwargs) -> Tuple[bool, Any]:
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                error_msg = ErrorHandler.log_exception(e, func.__name__)
                return False, error_msg
        
        return wrapper
    
    @staticmethod
    def validate_input(condition: bool, error_message: str) -> Tuple[bool, str]:
        """
        Validate a condition and return a standardized result tuple.
        
        Args:
            condition: Boolean condition to check
            error_message: Message to return if condition is False
            
        Returns:
            Tuple of (success, error_message_if_any)
        """
        if condition:
            return True, ""
        return False, error_message 