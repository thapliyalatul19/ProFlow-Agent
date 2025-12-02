"""
Error handling utilities for ProFlow Agent.

Provides centralized error handling with recovery strategies.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Type, Callable
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger("proflow")


class ErrorHandler:
    """
    Centralized error handler with recovery strategies.
    
    Tracks error frequencies and provides recovery mechanisms
    for common error types.
    """
    
    def __init__(self):
        """Initialize ErrorHandler."""
        self.error_counts: Dict[str, int] = {}
        self.recovery_strategies: Dict[Type[Exception], Callable] = {
            FileNotFoundError: self._recover_file_not_found,
            json.JSONDecodeError: self._recover_json_error,
            IOError: self._recover_io_error,
            PermissionError: self._recover_permission_error,
            ValueError: self._recover_value_error,
        }
        
        # Also handle JSONDecodeError via ValueError recovery if needed
        self._json_error_recovery = self._recover_json_error
    
    def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None,
        recovery_strategy: Optional[Callable] = None,
        reraise: bool = False
    ) -> Optional[Any]:
        """
        Handle an error with logging and optional recovery.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            recovery_strategy: Optional custom recovery function
            reraise: Whether to re-raise the error after handling
        
        Returns:
            Recovery result if recovery was successful, None otherwise
        """
        error_type = type(error).__name__
        error_key = f"{error_type}:{str(error)[:50]}"
        
        # Track error frequency
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log error with full context
        logger.error(f"Error occurred: {error_type}")
        logger.error(f"Error message: {str(error)}")
        
        if context:
            logger.error(f"Context: {context}")
        
        # Log full traceback
        logger.debug(f"Full traceback:\n{traceback.format_exc()}")
        
        # Try recovery
        recovery_result = None
        
        if recovery_strategy:
            # Use custom recovery strategy
            try:
                logger.info(f"Attempting custom recovery strategy...")
                recovery_result = recovery_strategy(error, context)
                if recovery_result is not None:
                    logger.info(f"✓ Recovery successful: {recovery_result}")
            except Exception as recovery_error:
                logger.error(f"✗ Recovery strategy failed: {recovery_error}")
        
        elif type(error) in self.recovery_strategies:
            # Use built-in recovery strategy
            try:
                logger.info(f"Attempting built-in recovery for {error_type}...")
                recovery_func = self.recovery_strategies[type(error)]
                recovery_result = recovery_func(error, context)
                if recovery_result is not None:
                    logger.info(f"✓ Recovery successful: {recovery_result}")
            except Exception as recovery_error:
                logger.error(f"✗ Recovery strategy failed: {recovery_error}")
        else:
            logger.warning(f"No recovery strategy available for {error_type}")
        
        # Re-raise if requested
        if reraise:
            raise
        
        return recovery_result
    
    def _recover_file_not_found(self, error: FileNotFoundError, context: Dict = None) -> Optional[Path]:
        """
        Recover from FileNotFoundError by creating default files.
        
        Args:
            error: FileNotFoundError exception
            context: Context dictionary (should contain 'file_path' and optionally 'default_content')
        
        Returns:
            Path to created file if successful, None otherwise
        """
        if context is None:
            context = {}
        
        file_path = context.get('file_path')
        if file_path is None:
            # Try to extract path from error message
            error_msg = str(error)
            if "No such file or directory" in error_msg or "cannot find the file" in error_msg:
                # Can't recover without knowing the file path
                logger.warning("Cannot recover FileNotFoundError: file path unknown")
                return None
        
        file_path = Path(file_path)
        default_content = context.get('default_content')
        file_type = context.get('file_type', 'unknown')
        
        logger.info(f"Attempting to create missing file: {file_path}")
        
        try:
            # Create directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file with default content
            if default_content is not None:
                if file_path.suffix == '.json':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(default_content, f, indent=2, ensure_ascii=False)
                elif file_path.suffix == '.csv':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(default_content)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(default_content))
                
                logger.info(f"✓ Created {file_type} file with default content: {file_path}")
            else:
                # Create empty file
                file_path.touch()
                logger.info(f"✓ Created empty file: {file_path}")
            
            return file_path
        
        except Exception as e:
            logger.error(f"✗ Failed to create file {file_path}: {e}")
            return None
    
    def _recover_json_error(self, error: json.JSONDecodeError, context: Dict = None) -> Optional[Dict]:
        """
        Recover from JSONDecodeError by using default data.
        
        Args:
            error: JSONDecodeError exception
            context: Context dictionary (should contain 'file_path' and 'default_data')
        
        Returns:
            Default data dictionary if provided, None otherwise
        """
        if context is None:
            context = {}
        
        file_path = context.get('file_path', 'unknown')
        default_data = context.get('default_data')
        
        logger.warning(f"JSON decode error in {file_path}: {error}")
        
        if default_data is not None:
            logger.info(f"Using default data for {file_path}")
            return default_data
        else:
            logger.error(f"No default data provided for {file_path}")
            return None
    
    def _recover_io_error(self, error: IOError, context: Dict = None) -> Optional[bool]:
        """
        Recover from IOError by retrying or using alternatives.
        
        Args:
            error: IOError exception
            context: Context dictionary
        
        Returns:
            True if recovery attempted, None otherwise
        """
        logger.warning(f"IOError occurred: {error}")
        logger.info("IOError recovery: Check file permissions and disk space")
        return None
    
    def _recover_permission_error(self, error: PermissionError, context: Dict = None) -> Optional[bool]:
        """
        Recover from PermissionError.
        
        Args:
            error: PermissionError exception
            context: Context dictionary
        
        Returns:
            True if recovery attempted, None otherwise
        """
        logger.warning(f"PermissionError occurred: {error}")
        logger.info("PermissionError recovery: Check file/directory permissions")
        return None
    
    def _recover_value_error(self, error: ValueError, context: Dict = None) -> Optional[Any]:
        """
        Recover from ValueError by using default values.
        
        Also handles JSON-related ValueErrors by checking error message.
        
        Args:
            error: ValueError exception
            context: Context dictionary (should contain 'default_value' or 'default_data')
        
        Returns:
            Default value if provided, None otherwise
        """
        if context is None:
            context = {}
        
        # Check if this is a JSON-related error
        error_msg = str(error).lower()
        if 'json' in error_msg or 'invalid json' in error_msg:
            # Try JSON recovery
            default_data = context.get('default_data') or context.get('default_value')
            if default_data is not None:
                logger.info(f"Using default data for JSON ValueError")
                return default_data
        
        # Regular ValueError recovery
        default_value = context.get('default_value') or context.get('default_data')
        
        if default_value is not None:
            logger.info(f"Using default value for ValueError: {default_value}")
            return default_value
        else:
            logger.warning(f"ValueError occurred: {error}")
            return None
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get statistics about handled errors.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            'total_unique_errors': len(self.error_counts),
            'error_counts': self.error_counts.copy(),
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None
        }
    
    def reset_error_counts(self):
        """Reset error count statistics."""
        self.error_counts.clear()
        logger.info("Error counts reset")


# Global error handler instance
_error_handler = None


def get_error_handler() -> ErrorHandler:
    """
    Get the global error handler instance.
    
    Returns:
        ErrorHandler instance
    """
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


# Example usage
if __name__ == "__main__":
    # Setup logging
    from .logger import setup_logging
    logger = setup_logging()
    
    print("Testing ErrorHandler...")
    
    handler = ErrorHandler()
    
    # Test FileNotFoundError recovery
    print("\n1. Testing FileNotFoundError recovery...")
    try:
        with open("nonexistent_file.txt", 'r') as f:
            content = f.read()
    except FileNotFoundError as e:
        handler.handle_error(
            e,
            context={
                'file_path': 'nonexistent_file.txt',
                'default_content': 'Default content\n',
                'file_type': 'text'
            }
        )
    
    # Test JSONDecodeError recovery
    print("\n2. Testing JSONDecodeError recovery...")
    try:
        json.loads('{"invalid": json}')
    except json.JSONDecodeError as e:
        result = handler.handle_error(
            e,
            context={
                'file_path': 'test.json',
                'default_data': {'default': 'data'}
            }
        )
        print(f"   Recovery result: {result}")
    
    # Test error stats
    print("\n3. Error statistics:")
    stats = handler.get_error_stats()
    print(f"   Total unique errors: {stats['total_unique_errors']}")
    print(f"   Error counts: {stats['error_counts']}")
    
    print("\n✅ ErrorHandler test complete!")

