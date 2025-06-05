import os
from typing import List, Optional, TextIO, Any, Dict
from pathlib import Path
from src.core.services.ServiceLocator import ServiceLocator
from src.core.exceptions import FileNotFoundError as LotusFileNotFoundError
from src.core.exceptions import FileAccessError, FileFormatError

class FileService:
    """
    Service for handling file operations.
    
    This service provides methods for reading and writing files,
    resolving paths relative to the work area root and FUB directories.
    It works with the ConfigService to properly resolve file paths
    and track important application files.
    """
    
    def __init__(self, config_service=None):
        """
        Initialize the file service.
        
        Args:
            config_service: ConfigService instance for resolving paths
        """
        self._config_service = config_service
    
    def set_config_service(self, config_service):
        """Set the config service for this file service."""
        self._config_service = config_service
    
    def resolve_path(self, path: str, relative_to_fub: bool = False) -> str:
        """
        Resolve a path relative to the work area or FUB directory.
        
        Args:
            path: Relative path
            relative_to_fub: Whether the path is relative to the FUB directory
            
        Returns:
            Absolute path
        """
        if self._config_service is None:
            return path
            
        if relative_to_fub:
            return self._config_service.get_fub_path(path)
        else:
            return self._config_service.get_path(path)
    
    def read_file(self, file_path: str, relative_to_fub: bool = False) -> Optional[str]:
        """
        Read the contents of a file.
        
        Args:
            file_path: Path to the file (relative to work area or FUB)
            relative_to_fub: Whether the path is relative to the FUB directory
            
        Returns:
            File contents as a string or None if file not found
            
        Raises:
            LotusFileNotFoundError: If the file does not exist
            FileAccessError: If the file cannot be accessed
        """
        abs_path = self.resolve_path(file_path, relative_to_fub)
        try:
            with open(abs_path, 'r') as file:
                return file.read()
        except (OSError, IOError) as e:
            if isinstance(e, FileNotFoundError):
                raise LotusFileNotFoundError(f"File not found: {abs_path}")
            else:
                raise FileAccessError(f"Cannot access file {abs_path}: {str(e)}")
    
    def write_file(self, file_path: str, content: str, relative_to_fub: bool = False) -> None:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file (relative to work area or FUB)
            content: Content to write
            relative_to_fub: Whether the path is relative to the FUB directory
            
        Raises:
            FileAccessError: If the file cannot be written
        """
        abs_path = self.resolve_path(file_path, relative_to_fub)
        
        # Create directory if it doesn't exist
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        except OSError as e:
            raise FileAccessError(f"Cannot create directory for {abs_path}: {str(e)}")
        
        try:
            with open(abs_path, 'w') as file:
                file.write(content)
        except (OSError, IOError) as e:
            raise FileAccessError(f"Cannot write to file {abs_path}: {str(e)}")
    
    def file_exists(self, path: str, relative_to_fub: bool = False) -> bool:
        """
        Check if a file exists.
        
        Args:
            path: Path to the file (relative to work area or FUB)
            relative_to_fub: Whether the path is relative to the FUB directory
            
        Returns:
            True if the file exists, False otherwise
        """
        abs_path = self.resolve_path(path, relative_to_fub)
        return os.path.isfile(abs_path)
    
    def list_files(self, directory: str, relative_to_fub: bool = False) -> List[str]:
        """
        List files in a directory.
        
        Args:
            directory: Directory path (relative to work area or FUB)
            relative_to_fub: Whether the path is relative to the FUB directory
            
        Returns:
            List of file names in the directory
        """
        abs_path = self.resolve_path(directory, relative_to_fub)
        
        if not os.path.isdir(abs_path):
            return []
            
        return os.listdir(abs_path)
    
    def get_file_extension(self, file_path: str) -> str:
        """
        Get the extension of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File extension (including the dot)
        """
        return os.path.splitext(file_path)[1]
    
    def join_paths(self, *paths) -> str:
        """
        Join multiple path components.
        
        Args:
            *paths: Path components to join
            
        Returns:
            Joined path
        """
        return os.path.join(*paths)
    
    def get_basename(self, path: str) -> str:
        """
        Get the base name of a file path.
        
        Args:
            path: File path
            
        Returns:
            Base name (file name with extension)
        """
        return os.path.basename(path)
    
    def get_dirname(self, path: str) -> str:
        """
        Get the directory name of a file path.
        
        Args:
            path: File path
            
        Returns:
            Directory name
        """
        return os.path.dirname(path)
    
    def get_absolute_path(self, path: str) -> str:
        """
        Get the absolute path.
        
        Args:
            path: Path to convert
            
        Returns:
            Absolute path
        """
        return os.path.abspath(path)
    
    def ensure_directory(self, directory: str, relative_to_fub: bool = False) -> None:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Directory path (relative to work area or FUB)
            relative_to_fub: Whether the path is relative to the FUB directory
        """
        abs_path = self.resolve_path(directory, relative_to_fub)
        os.makedirs(abs_path, exist_ok=True)
    
    def get_tracked_file_path(self, file_key: str) -> Optional[str]:
        """
        Get a tracked file path from the config service.
        
        This is a convenience method for accessing files that are
        tracked by the ConfigService, which is useful for UI components
        that need to display or manipulate these paths.
        
        Args:
            file_key: Key for the file path (e.g., 'spice_file', 'config_file')
            
        Returns:
            The file path or None if not found or config service not available
        """
        if self._config_service is None:
            return None
            
        return self._config_service.get_file_path(file_key)
    
    def set_tracked_file_path(self, file_key: str, file_path: str) -> None:
        """
        Set a tracked file path in the config service.
        
        This is a convenience method for updating files that are
        tracked by the ConfigService, such as when a user performs
        a "Save As" operation.
        
        Args:
            file_key: Key for the file path
            file_path: New file path
        """
        if self._config_service is None:
            return
            
        self._config_service.set_file_path(file_key, file_path)
    
    def get_all_tracked_file_paths(self) -> Dict[str, str]:
        """
        Get all tracked file paths from the config service.
        
        Returns:
            Dictionary of all tracked file paths or empty dict if no config service
        """
        if self._config_service is None:
            return {}
            
        return self._config_service.get_all_file_paths()
    
    def read_tracked_file(self, file_key: str) -> Optional[str]:
        """
        Read the contents of a tracked file.
        
        This is a convenience method for reading files that are
        tracked by the ConfigService.
        
        Args:
            file_key: Key for the file path (e.g., 'spice_file', 'config_file')
            
        Returns:
            File contents as a string or None if file not found
            
        Raises:
            LotusFileNotFoundError: If the file path is not tracked or does not exist
            FileAccessError: If the file cannot be accessed
        """
        file_path = self.get_tracked_file_path(file_key)
        if not file_path:
            raise LotusFileNotFoundError(f"No tracked file path for key: {file_key}")
            
        try:
            return self.read_file(file_path, relative_to_fub=False)
        except LotusFileNotFoundError as e:
            raise LotusFileNotFoundError(f"Tracked file not found: {file_path}\n{str(e)}")
        except FileAccessError as e:
            raise FileAccessError(f"Cannot access tracked file {file_path}: {str(e)}")
    
    def write_tracked_file(self, file_key: str, content: str) -> None:
        """
        Write content to a tracked file.
        
        This is a convenience method for writing to files that are
        tracked by the ConfigService.
        
        Args:
            file_key: Key for the file path
            content: Content to write
            
        Raises:
            LotusFileNotFoundError: If the file path is not tracked
            FileAccessError: If the file cannot be written
        """
        file_path = self.get_tracked_file_path(file_key)
        if not file_path:
            raise LotusFileNotFoundError(f"No tracked file path for key: {file_key}")
            
        try:
            self.write_file(file_path, content, relative_to_fub=False)
        except LotusFileNotFoundError as e:
            raise LotusFileNotFoundError(f"Tracked file not found: {file_path}\n{str(e)}")    
        except FileAccessError as e:
            raise FileAccessError(f"Cannot write to tracked file {file_path}: {str(e)}")
    def tracked_file_exists(self, file_key: str) -> bool:
        """
        Check if a tracked file exists.
        
        Args:
            file_key: Key for the file path
            
        Returns:
            True if the file exists, False otherwise
        """
        file_path = self.get_tracked_file_path(file_key)
        if not file_path:
            return False
            
        return os.path.isfile(file_path)