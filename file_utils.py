# file_utils.py
"""
Utility functions for safe file operations with cross-platform locking support.
"""
import time
import os
import sys
from pathlib import Path
from typing import Callable, Any

# Try to import fcntl for Unix-like systems
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False
    
# Try to import msvcrt for Windows
try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


class FileLockError(Exception):
    """Custom exception for file locking errors."""
    pass


def _lock_file_unix(file_handle):
    """Lock file on Unix-like systems."""
    fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file_unix(file_handle):
    """Unlock file on Unix-like systems."""
    fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)


def _lock_file_windows(file_handle):
    """Lock file on Windows."""
    msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)


def _unlock_file_windows(file_handle):
    """Unlock file on Windows."""
    msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)


def safe_excel_operation(file_path: Path, operation: Callable, max_retries: int = 3, retry_delay: float = 0.5) -> Any:
    """
    Safely perform operations on Excel files with file locking.
    
    Args:
        file_path: Path to the Excel file
        operation: Function to execute (should take file_path as argument)
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Result from the operation function
        
    Raises:
        FileLockError: If file cannot be locked after all retries
        
    Example:
        def write_data(file_path):
            df = pd.DataFrame({'A': [1, 2, 3]})
            df.to_excel(file_path, index=False)
            
        safe_excel_operation(Path('data.xlsx'), write_data)
    """
    file_path = Path(file_path)
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Execute the operation
            result = operation(file_path)
            return result
            
        except PermissionError as e:
            # File is locked by another process
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                raise FileLockError(
                    f"Could not access file after {max_retries} attempts. "
                    f"File may be open in Excel or another application: {file_path}"
                ) from e
                
        except Exception as e:
            # Other errors - don't retry
            raise
    
    # If we get here, all retries failed
    raise FileLockError(
        f"Failed to perform operation after {max_retries} attempts: {last_error}"
    )


def create_file_if_not_exists(file_path: Path, create_func: Callable):
    """
    Create a file if it doesn't exist, with proper error handling.
    
    Args:
        file_path: Path to the file
        create_func: Function to create the file (should take file_path as argument)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the file
        try:
            create_func(file_path)
        except Exception as e:
            raise IOError(f"Failed to create file {file_path}: {e}") from e


def backup_file(file_path: Path, backup_dir: Path = None) -> Path:
    """
    Create a backup copy of a file.
    
    Args:
        file_path: Path to the file to backup
        backup_dir: Directory to store backup (default: same directory as original)
        
    Returns:
        Path to the backup file
    """
    import shutil
    from datetime import datetime
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")
    
    # Determine backup location
    if backup_dir is None:
        backup_dir = file_path.parent / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    # Copy file
    shutil.copy2(file_path, backup_path)
    
    return backup_path
