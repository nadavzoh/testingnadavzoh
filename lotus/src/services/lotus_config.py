from PyQt5.QtGui import QIcon

import pathlib


class LotusConfig:
    """
    Configuration class for Lotus application settings and resources.

    This class provides static access to application resources like icons and
    stylesheets, and manages path resolution for these resources. It follows
    a static utility pattern for easy access from anywhere in the application.

    Attributes:
        this_file_path (pathlib.Path): Absolute path to this file
        package_root_dir (pathlib.Path): Root directory of the lotus package
        lotus_root_dir (pathlib.Path): Base path of the application
        icons_path (pathlib.Path): Path to icons directory
        stylesheets_path (pathlib.Path): Path to stylesheets directory
        _icons (dict): Mapping of icon names to file paths
        _stylesheets (dict): Mapping of stylesheet names to file paths
    """
    # Use pathlib for more modern path handling
    this_file_path = pathlib.Path(__file__).resolve()
    package_root_dir = this_file_path.parent.parent
    lotus_root_dir = package_root_dir.parent
    
    icons_path = lotus_root_dir / "assets" / "icons"
    stylesheets_path = lotus_root_dir / "assets" / "stylesheets"

    _icons = {
        "LOTUS": str(icons_path / "icons8-lotus-16.png"),
        "SPLASHSCREEN": str(icons_path / "lotus_splash_screen.png"),
        "INSERT_LINE": str(icons_path / "icons8-add-16.png"),
        "ENABLE_EDIT": str(icons_path / "icons8-edit-file-16.png"),
        "ERASE": str(icons_path / "icons8-delete-16.png"),
        "UNDO": str(icons_path / "icons8-undo-16.png"),
        "REDO": str(icons_path / "icons8-redo-16.png"),
        "SAVE": str(icons_path / "icons8-save-16.png"),
        "YES": str(icons_path / "icons8-yes-button-16.png"),
        "CANCEL": str(icons_path / "icons8-cancel-16.png"),
        "TOGGLE_THEME": str(icons_path / "icons8-night-16.png"),
    }
    
    _stylesheets = {
        "DARK_MODE": str(stylesheets_path / "DARK_MODE.css"),
        "LIGHT_MODE": str(stylesheets_path / "LIGHT_MODE.css")
    }

    def __init__(self):
        """
        Initialize the LotusConfig instance.

        Note: This class is primarily used through its static methods
        and doesn't require instantiation for normal use.
        """
        pass

    @staticmethod
    def get_icon(icon_name):
        """
        Get a QIcon by its name from the configuration.

        Args:
            icon_name (str): Name of the icon as defined in _icons dictionary

        Returns:
            QIcon: The requested icon for use in UI elements

        Raises:
            KeyError: If the requested icon name is not found
        """
        return QIcon(LotusConfig._icons[icon_name])

    @staticmethod
    def get_icon_path(icon_name):
        """
        Get the path of an icon by its name.

        Args:
            icon_name (str): Name of the icon as defined in _icons dictionary

        Returns:
            str: The path to the requested icon file

        Raises:
            KeyError: If the requested icon name is not found
        """
        return LotusConfig._icons[icon_name]

    @staticmethod
    def get_stylesheet(stylesheet_name):
        """
        Get a stylesheet path by its name from the configuration.

        Args:
            stylesheet_name (str): Name of the stylesheet as defined in _stylesheets dictionary

        Returns:
            str: The path to the requested stylesheet file

        Raises:
            KeyError: If the requested stylesheet name is not found
        """
        return LotusConfig._stylesheets[stylesheet_name]