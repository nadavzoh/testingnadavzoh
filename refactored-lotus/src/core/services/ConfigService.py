import os
import argparse
from typing import Dict, Any, Optional, List
from src.core.exceptions import WorkAreaNotFoundError, FubNotFoundError, InvalidConfigurationError

class ConfigService:
    """
    Service for managing application configuration.
    
    This service handles command line arguments, environment variables,
    and provides a unified interface for accessing configuration values.
    It also tracks important file paths that may need to be displayed
    in the UI or used throughout the application.
    """
    
    SERVICES_ROOT = os.path.dirname(os.path.abspath(__file__))
    CORE_ROOT = os.path.dirname(SERVICES_ROOT)
    SRC_ROOT = os.path.dirname(CORE_ROOT)
    PROJECT_ROOT = os.path.dirname(SRC_ROOT)

    def __init__(self, argv=None):
        """Initialize the configuration service."""
        self._args = None
        self._env_vars = {}
        self._config = {}
        self._file_paths = {}  # Track important file paths
        self.initialize(argv)
        
    def initialize(self, argv=None):
        """
        Initialize configuration from command line arguments and environment variables.
        
        Args:
            argv: Command line arguments (optional, uses sys.argv if None)
        """
        # Parse command line arguments
        self._parse_args(argv)
        
        # Read environment variables
        self._read_env_vars()
        
        # Build configuration
        try:
            self._build_config()
        except Exception as e:
            print(f"Setup error: {e}")
            exit(1)
        
        # Initialize tracked file paths
        self._initialize_file_paths()
    
    def _parse_args(self, argv):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description='Lotus Application')
        
        # Add command line arguments
        parser.add_argument('-fub', dest='fub', help='FUB name')
        parser.add_argument('-work_area', dest='work_area', help='Work area root directory')
        parser.add_argument('-spice', dest='spice', help='Spice file path')
        parser.add_argument('-af', dest='af', help='AF configuration file path')
        parser.add_argument('-mutex', dest='mutex', help='Mutex configuration file path')
        parser.add_argument('-config', dest='config', help='Configuration file path')
        
        self._args = parser.parse_args(argv)
    
    def _read_env_vars(self):
        """Read relevant environment variables."""
        # Read environment variables
        self._env_vars = {
            'WORK_AREA_ROOT_DIR': os.environ.get('WORK_AREA_ROOT_DIR'),
            'DBB': os.environ.get('DBB'),
            'SPICE_FILE': os.environ.get('SPICE_FILE'),
            # Add more environment variables as needed
        }
    
    def _build_config(self):
        """Build configuration from arguments and environment variables."""
        # Start with environment variables
        self._config = {
            'work_area_root_dir': self._env_vars.get('WORK_AREA_ROOT_DIR'),
            'fub': self._env_vars.get('DBB'),
            'spice_file': self._env_vars.get('SPICE_FILE'),
        }
        
        # Override with command line arguments if provided
        if self._args:
            if self._args.work_area:
                self._config['work_area_root_dir'] = self._args.work_area
                
            if self._args.fub:
                self._config['fub'] = self._args.fub
                
            if self._args.spice:
                self._config['spice_file'] = self._args.spice
                
            if self._args.config:
                self._config['config_file'] = self._args.config

        # If config file is specified, load it
        # if self._config.get('config_file'):
        #     self.load_configuration(self._config['config_file'])
        
        # Validate required configuration
        if not self._config.get('work_area_root_dir'):
            raise WorkAreaNotFoundError("Work area root directory not specified. "
                                        "Use -work_area argument or set WORK_AREA_ROOT_DIR environment variable.")
        if not self._config.get('fub'):
            raise FubNotFoundError("FUB not specified. Use -fub argument or set DBB environment variable.")
    
    def _initialize_file_paths(self):
        """Initialize tracked file paths based on configuration."""
        work_area = self.get_config('work_area_root_dir')
        fub = self.get_config('fub')
        print("IN HERE, work_area:", work_area, "fub:", fub)
        if work_area and fub:
            # Common file paths used by the application
            self._file_paths = {
                # 'fub_dir': os.path.join(work_area),
                'spice_file': self.get_config('spice_file') or os.path.join(work_area, 'netlists', 'spice', f'{fub}.sp'),
                # 'config_file': self.get_config('config_file') or os.path.join(work_area, 'cfg', f'{fub}.lotus_cfg'),
                'af_file': os.path.join(work_area, 'drive', 'cfg', f'{fub}.af.dcfg'),
                'mutex_file': os.path.join(work_area, 'drive', 'cfg', f'{fub}.mutex.dcfg'),
            }
        print("File paths initialized:", self._file_paths)
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        
        # Update tracked file paths if relevant
        if key in ['work_area_root_dir', 'fub', 'spice_file', 'config_file']:
            self._initialize_file_paths()
    
    def get_path(self, relative_path: str) -> str:
        """
        Get an absolute path relative to the work area root directory.
        
        Args:
            relative_path: Path relative to work area root
            
        Returns:
            Absolute path
            
        Raises:
            WorkAreaNotFoundError: If work area root directory is not specified
        """
        work_area = self.get_config('work_area_root_dir')
        if not work_area:
            raise WorkAreaNotFoundError("Work area root directory not specified")
            
        return os.path.join(work_area, relative_path)
    
    # TODO: probably wrong and can be removed. get_path already does this
    # because work_area_root_dir is always the same as fub..
    def get_fub_path(self, relative_path: str) -> str:
        """
        Get an absolute path relative to the FUB directory.
        
        Args:
            relative_path: Path relative to FUB directory
            
        Returns:
            Absolute path
            
        Raises:
            FubNotFoundError: If FUB is not specified
        """
        fub = self.get_config('fub')
        if not fub:
            raise FubNotFoundError("FUB not specified. Use -fub argument or set DBB environment variable.")
            
        fub_dir = os.path.join(self.get_config('work_area_root_dir'), fub)
        return os.path.join(fub_dir, relative_path)
    
    def get_file_path(self, file_key: str) -> Optional[str]:
        """
        Get a tracked file path by key.
        
        This method is useful for UI components that need to display
        or work with important file paths.
        
        Args:
            file_key: Key for the file path (e.g., 'spice_file', 'config_file')
            
        Returns:
            The file path or None if not found
        """
        return self._file_paths.get(file_key)
    
    def set_file_path(self, file_key: str, file_path: str) -> None:
        """
        Set a tracked file path.
        
        This method is useful when the user changes a file location,
        e.g., through "Save As" functionality.
        
        Args:
            file_key: Key for the file path
            file_path: New file path
        """
        self._file_paths[file_key] = file_path
        
        # Also update related config if applicable
        if file_key == 'spice_file':
            self._config['spice_file'] = file_path
        elif file_key == 'config_file':
            self._config['config_file'] = file_path
        elif file_key == 'af_file':
            self._config['af_file'] = file_path
        elif file_key == 'mutex_file':
            self._config['mutex_file'] = file_path
    
    def get_all_file_paths(self) -> Dict[str, str]:
        """
        Get all tracked file paths.
        
        Returns:
            Dictionary of all tracked file paths
        """
        return self._file_paths.copy()
