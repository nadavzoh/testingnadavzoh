import os

class LotusFilesManager:
    """
    Singleton class to manage Lotus files and directories.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LotusFilesManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._root_dir = os.environ['LOTUS_ROOT_DIR']
            self._fub = os.environ['LOTUS_FUB']
            self._spice_file = os.environ.get('LOTUS_SPICE_FILE') or f'{self._root_dir}/drive/cfg/{self._fub}.sp'
            self._spice_data = self.load_spice_data()  # TODO: in case future tabs need it, might not be needed if mutex tab also utilizes fly
            self._af_dcfg_file = os.environ.get('LOTUS_AF_DCFG_FILE') or f'{self._root_dir}/drive/cfg/{self._fub}.af.dcfg'
            self._mutex_dcfg_file = os.environ.get('LOTUS_MUTEX_DCFG_FILE') or f'{self._root_dir}/drive/cfg/{self._fub}.mutex.dcfg'
            self._initialized = True

    def get_root_dir(self):
        return self._root_dir

    def get_fub(self):
        return self._fub

    def get_spice_file(self):
        return self._spice_file

    def get_af_dcfg_file(self):
        return self._af_dcfg_file

    def get_mutex_dcfg_file(self):
        return self._mutex_dcfg_file

    def load_spice_data(self):
        with open(self._spice_file, 'r') as f:
            self._spice_data = f.read()
        return self._spice_data