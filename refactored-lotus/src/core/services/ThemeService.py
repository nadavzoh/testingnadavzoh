import os
import re
from typing import Dict, Optional, Any
from PyQt5.QtGui import QColor
from src.core.exceptions import ConfigError

# TODO: handle paths better, need repo root, assets, etc.
# best place to get it from is the config service ?
# or file service ?

class ThemeService:
    """
    Service for managing application theming, styling, and appearance.
    
    This service handles theme switching between light and dark modes,
    applying stylesheets to the entire application, managing font sizes,
    and providing access to application icons.
    
    It follows the service layer pattern and can be registered with the
    ServiceLocator for application-wide access.
    """
    
    # Theme modes
    LIGHT_MODE = "light"
    DARK_MODE = "dark"
    # we are in test-lotus-refactored/src/core/services/ThemeService.py
    # create a variable that holds the root of the project

    def __init__(self, config_service=None, file_service=None):
        """
        Initialize the theme service.
        
        Args:
            config_service: Service for accessing configuration
            file_service: Service for file operations
        """
        self._config_service = config_service
        self._file_service = file_service
        self.project_root = config_service.PROJECT_ROOT if config_service else None
        # Theme state
        self._dark_mode = False
        self._font_size_adjustment = 0
        
        # Stylesheet paths and content
        self._stylesheet_paths = {
            self.LIGHT_MODE: None,
            self.DARK_MODE: None
        }
        self._base_stylesheets = {
            self.LIGHT_MODE: "",
            self.DARK_MODE: ""
        }
        self._active_stylesheets = {
            self.LIGHT_MODE: "",
            self.DARK_MODE: ""
        }
        
        # Font size information
        self._base_font_sizes = {
            self.LIGHT_MODE: {},
            self.DARK_MODE: {}
        }
        
        # Icon paths
        self._icon_paths = {}
        
        # QApplication instance (will be set when initializing)
        self._app = None
    
    def initialize(self, app=None):
        """
        Initialize the theme service with application settings.
        
        This loads stylesheets, captures base font sizes, and applies
        the initial theme to the application.
        
        Args:
            app: The QApplication instance
            
        Returns:
            bool: True if initialization was successful, False otherwise
            
        Raises:
            ConfigError: If required configuration is missing
        """
        self._app = app
        
        # Load configuration if available
        if self._config_service:
            self._dark_mode = self._config_service.get_config('dark_mode', False)
            self._font_size_adjustment = self._config_service.get_config('font_size_adjustment', 0)
        
        # Initialize stylesheet paths
        self._initialize_stylesheet_paths()
        
        # Load stylesheet content
        self._load_stylesheets()
        
        # Capture base font sizes
        self._capture_base_font_sizes()
        
        # Apply font size adjustment
        if self._font_size_adjustment != 0:
            self._apply_font_adjustment()
        
        # Initialize icon paths
        self._initialize_icon_paths()
        
        # Apply the theme to the application
        return self._apply_theme()
    
    def _initialize_stylesheet_paths(self):
        """
        Initialize the paths to stylesheet files.
        
        This uses the config_service to get stylesheet paths if available,
        otherwise falls back to default paths.
        """
        if self._config_service:
            self._stylesheet_paths[self.LIGHT_MODE] = self._config_service.get_config(
                'light_stylesheet', f'{self.project_root}/assets/stylesheets/light.qss')
            self._stylesheet_paths[self.DARK_MODE] = self._config_service.get_config(
                'dark_stylesheet', f'{self.project_root}/assets/stylesheets/dark.qss')
        else:
            # Default paths if no config service
            self._stylesheet_paths[self.LIGHT_MODE] = f'{self.project_root}/assets/stylesheets/light.qss'
            self._stylesheet_paths[self.DARK_MODE] = f'{self.project_root}/assets/stylesheets/dark.qss'
    
    def _load_stylesheets(self):
        """
        Load stylesheet content from files.
        
        Uses the file_service if available, otherwise falls back to
        direct file access.
        """
        for mode in [self.LIGHT_MODE, self.DARK_MODE]:
            path = self._stylesheet_paths[mode]
            
            if self._file_service and path:
                try:
                    content = self._file_service.read_file(path)
                    if content:
                        self._base_stylesheets[mode] = content
                        self._active_stylesheets[mode] = content
                except Exception as e:
                    print(f"Error loading stylesheet {path}: {e}")
            elif path and os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        self._base_stylesheets[mode] = content
                        self._active_stylesheets[mode] = content
                except Exception as e:
                    print(f"Error loading stylesheet {path}: {e}")
    
    def _capture_base_font_sizes(self):
        """
        Extract and store the original font sizes from stylesheets.
        
        This captures font sizes from the stylesheet content for later
        font size adjustments.
        """
        for mode in [self.LIGHT_MODE, self.DARK_MODE]:
            self._base_font_sizes[mode] = self._extract_font_sizes(self._base_stylesheets[mode])
    
    def _extract_font_sizes(self, css: str) -> Dict[str, int]:
        """
        Extract font sizes from CSS content.
        
        Args:
            css: The CSS content to parse
            
        Returns:
            Dict[str, int]: A dictionary mapping widget names to their font sizes
        """
        sizes = {}
        
        # Find all font-size declarations
        patterns = [
            r'(\w+)\s+{[^}]*font-size:\s*(\d+)px',  # QWidget { font-size: 14px; }
            r'(\w+)::(\w+)\s+{[^}]*font-size:\s*(\d+)px',  # QWidget::part { font-size: 14px; }
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, css)
            for match in matches:
                if len(match.groups()) == 2:
                    widget, size = match.groups()
                    sizes[widget] = int(size)
                elif len(match.groups()) == 3:
                    widget, part, size = match.groups()
                    sizes[f"{widget}::{part}"] = int(size)
        
        return sizes
    
    def _initialize_icon_paths(self):
        """
        Initialize paths to application icons.
        
        This sets up the mapping of icon names to file paths for both
        light and dark themes.
        """
        # Default icon directory
        icon_dir = f"f{self.project_root}/assets/icons"
        
        # Common icons
        self._icon_paths = {
            'app_icon': f"{icon_dir}/lotus.png",
            'open': f"{icon_dir}/open.png",
            'save': f"{icon_dir}/save.png",
            'save_as': f"{icon_dir}/save_as.png",
            'undo': f"{icon_dir}/undo.png",
            'redo': f"{icon_dir}/redo.png",
            'cut': f"{icon_dir}/cut.png",
            'copy': f"{icon_dir}/copy.png",
            'paste': f"{icon_dir}/paste.png",
            'font_increase': f"{icon_dir}/font_increase.png",
            'font_decrease': f"{icon_dir}/font_decrease.png",
            'font_reset': f"{icon_dir}/font_reset.png",
            'theme_toggle': f"{icon_dir}/theme_toggle.png",
        }
        
        # Theme-specific icons
        self._theme_icon_paths = {
            self.LIGHT_MODE: {
                # Light theme specific icons
            },
            self.DARK_MODE: {
                # Dark theme specific icons
            }
        }
    
    def is_dark_mode(self) -> bool:
        """
        Check if dark mode is currently active.
        
        Returns:
            bool: True if dark mode is active, False otherwise
        """
        return self._dark_mode
    
    def toggle_theme(self) -> bool:
        """
        Toggle between light and dark themes.
        
        This changes the current theme to the opposite of what is currently
        active and applies the new theme to the application.
        
        Returns:
            bool: The new dark_mode state after toggling
        """
        self._dark_mode = not self._dark_mode
        
        # Save the preference if config service is available
        if self._config_service:
            self._config_service.set_config('dark_mode', self._dark_mode)
        
        # Apply the theme
        self._apply_theme()
        
        return self._dark_mode
    
    def set_theme(self, dark_mode: bool) -> None:
        """
        Set the theme to light or dark mode.
        
        Args:
            dark_mode: True to set dark mode, False for light mode
        """
        if self._dark_mode != dark_mode:
            self._dark_mode = dark_mode
            
            # Save the preference if config service is available
            if self._config_service:
                self._config_service.set_config('dark_mode', self._dark_mode)
            
            # Apply the theme
            self._apply_theme()
    
    def _apply_theme(self) -> bool:
        """
        Apply the currently active theme to the application.
        
        Returns:
            bool: True if the theme was applied successfully, False otherwise
        """
        if not self._app:
            return False
        
        theme = self._active_stylesheets[self.DARK_MODE if self._dark_mode else self.LIGHT_MODE]
        
        try:
            self._app.setStyleSheet(theme)
            return True
        except Exception as e:
            print(f"Failed to apply stylesheet: {e}")
            # Fallback to default stylesheet
            if self._dark_mode:
                self._app.setStyleSheet("QWidget { background-color: #2d2d2d; color: #f0f0f0; }")
            else:
                self._app.setStyleSheet("")
            return False
    
    def increase_font_size(self) -> None:
        """
        Increase font size by 1 point.
        
        The adjustment is limited to +8 points to keep text readable.
        """
        # Don't go above 8 points adjustment to keep text readable
        if self._font_size_adjustment < 8:
            self._font_size_adjustment += 1
            self._apply_font_adjustment()
            
            # Save the preference if config service is available
            if self._config_service:
                self._config_service.set_config('font_size_adjustment', self._font_size_adjustment)
    
    def decrease_font_size(self) -> None:
        """
        Decrease font size by 1 point, with a minimum limit.
        
        The adjustment is limited to -4 points to keep text readable.
        """
        # Don't go below -4 points adjustment to keep text readable
        if self._font_size_adjustment > -4:
            self._font_size_adjustment -= 1
            self._apply_font_adjustment()
            
            # Save the preference if config service is available
            if self._config_service:
                self._config_service.set_config('font_size_adjustment', self._font_size_adjustment)
    
    def reset_font_size(self) -> None:
        """
        Reset font size to original values.
        """
        if self._font_size_adjustment != 0:
            self._font_size_adjustment = 0
            self._apply_font_adjustment()
            
            # Save the preference if config service is available
            if self._config_service:
                self._config_service.set_config('font_size_adjustment', self._font_size_adjustment)
    
    def _apply_font_adjustment(self) -> None:
        """
        Apply the current font size adjustment to the application.
        
        This modifies the active stylesheets based on the current
        font size adjustment and reapplies the theme.
        """
        for mode in [self.LIGHT_MODE, self.DARK_MODE]:
            css = self._base_stylesheets[mode]
            
            for widget, size in self._base_font_sizes[mode].items():
                adjusted_size = max(8, size + self._font_size_adjustment)
                
                css = re.sub(
                    f"({widget}[^}}]*font-size:)\\s*\\d+px", 
                    f"\\1 {adjusted_size}px", 
                    css
                )
            
            self._active_stylesheets[mode] = css
        
        # Apply the updated theme
        self._apply_theme()
    
    def get_icon_path(self, icon_name: str) -> Optional[str]:
        """
        Get the path to an icon.
        
        Args:
            icon_name: The name of the icon
            
        Returns:
            Optional[str]: The path to the icon, or None if not found
        """
        # Check for theme-specific icon first
        theme = self.DARK_MODE if self._dark_mode else self.LIGHT_MODE
        if icon_name in self._theme_icon_paths[theme]:
            return self._theme_icon_paths[theme][icon_name]
        
        # Fall back to common icons
        return self._icon_paths.get(icon_name)
    
    def get_stylesheet_content(self, mode: Optional[str] = None) -> str:
        """
        Get the content of the active stylesheet.
        
        Args:
            mode: The theme mode to get (LIGHT_MODE or DARK_MODE),
                 or None for the currently active theme
                 
        Returns:
            str: The stylesheet content
        """
        if mode is None:
            mode = self.DARK_MODE if self._dark_mode else self.LIGHT_MODE
            
        return self._active_stylesheets.get(mode, "")
    
    def set_config_service(self, config_service) -> None:
        """
        Set the config service.
        
        Args:
            config_service: The config service to use
        """
        self._config_service = config_service
    
    def set_file_service(self, file_service) -> None:
        """
        Set the file service.
        
        Args:
            file_service: The file service to use
        """
        self._file_service = file_service
    
    def get_font_size_adjustment(self) -> int:
        """
        Get the current font size adjustment.
        
        Returns:
            int: The current font size adjustment
        """
        return self._font_size_adjustment
    
    def get_status_color(self, status: int) -> str:
        """
        Get the color for a line status.
        
        Args:
            status: The line status (e.g., VALID, INVALID, WARNING)
            
        Returns:
            str: The color as a hex string
        """
        if self._dark_mode:
            status_colors = {
                0: "#000000",  # VALID - Black
                1: "#F44336",  # INVALID - Red
                2: "#FFC107",  # WARNING - Yellow
                3: "#78909C",  # COMMENT - Blue-gray
            }
        else:
            status_colors = {
                0: "#000000",  # VALID - Black
                1: "#C62828",  # INVALID - Darker Red
                2: "#F57F17",  # WARNING - Darker Yellow
                3: "#546E7A",  # COMMENT - Darker Blue-gray
            }
        
        return status_colors.get(status, "#000000")

    # def get_line_selected_color(self) -> QColor:
    #     """
    #     Get the color for selected lines.
        
    #     Returns:
    #         str: The color as a hex string
    #     """
    #     if self._dark_mode:
    #         return QColor("#37474F")
    #     else:
    #         return QColor("#E0E0E0")
