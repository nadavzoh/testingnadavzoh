import os


class LotusFileManager:
    """
    Singleton class to manage Lotus files and directories.

    This class provides access to critical file paths used throughout the application,
    including root directory, FUB information, and configuration files.
    It follows the Singleton pattern to ensure only ONE instance exists across the application.

    Attributes:
        _instance (LotusFileManager): Class variable holding the singleton instance
        _ward (str): Root directory path from environment variable
        _fub (str): Functional Unit Block name from environment variable
        _spice_file (str): Path to spice file
        _af_dcfg_file (str): Path to af configuration file
        _mutex_dcfg_file (str): Path to mutex configuration file
        _initialized (bool): Flag indicating if instance has been initialized
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ to implement the Singleton pattern.

        Returns:
            LotusFileManager: The singleton instance of this class
        """
        if cls._instance is None:
            cls._instance = super(LotusFileManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initialize the LotusFileManager with paths from environment variables.

        Sets up paths to all required configuration and data files.
        Only runs initialization once due to Singleton pattern.
        """
        if not hasattr(self, '_initialized'):
            self._ward = os.environ['LOTUS_USER_WARD']
            self._fub = os.environ['LOTUS_FUB']
            self._spice_file = os.environ.get('LOTUS_SPICE_FILE') or f'{self._ward}/netlists/spice/{self._fub}.sp'
            # if a config file is not found, an empty editor will be created in the specified tab
            self._af_dcfg_file = os.environ.get(
                'LOTUS_AF_DCFG_FILE') or f'{self._ward}/drive/cfg/{self._fub}.af.dcfg'
            self._mutex_dcfg_file = os.environ.get(
                'LOTUS_MUTEX_DCFG_FILE') or f'{self._ward}/drive/cfg/{self._fub}.mutex.dcfg'
            self._initialized = True

    def get_ward(self):
        """
        Get the work_area_root_dir path.

        Returns:
            str: The work_area_root_dir path
        """
        return self._ward

    def get_fub(self):
        """
        Get the FUB (Functional Unit Block) name.

        Returns:
            str: The FUB name
        """
        return self._fub

    def get_spice_file(self):
        """
        Get the path to the spice file.

        Returns:
            str: Path to the spice file
        """
        return self._spice_file

    def get_af_dcfg_file(self):
        """
        Get the path to the AF configuration file.

        Returns:
            str: Path to the AF configuration file
        """
        return self._af_dcfg_file

    def get_mutex_dcfg_file(self):
        """
        Get the path to the mutex configuration file.

        Returns:
            str: Path to the mutex configuration file
        """
        return self._mutex_dcfg_file

    
