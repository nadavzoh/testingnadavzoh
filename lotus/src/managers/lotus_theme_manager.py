from PyQt5.QtWidgets import QApplication
from services.lotus_config import LotusConfig
import re

class LotusThemeManager:
    """
    Manager for application theming and appearance.

    This class handles theme switching between light and dark modes,
    applying stylesheets to the entire application, and providing fallback
    styling when needed.

    Attributes:
        dark_mode (bool): Whether dark mode is currently active
    """

    def __init__(self, dark_mode=False):
        """
        Initialize the theme manager with a default theme.

        Args:
            dark_mode (bool, optional): Whether to start in dark mode. Defaults to False.
        """
        self.dark_mode = dark_mode

        self._light_mode_path = self._get_stylesheet_path("light")
        self._dark_mode_path = self._get_stylesheet_path("dark")

        self._base_stylesheets = {
            "light": self._get_stylesheet_content(self._light_mode_path),
            "dark": self._get_stylesheet_content(self._dark_mode_path)
        }
        self._active_stylesheets = self._base_stylesheets.copy()

        self._base_font_sizes = self._capture_base_font_sizes()
        self._font_size_adjustment = 0
        self._apply_theme()

    def toggle_theme(self):
        """
        Toggle between light and dark themes.

        Changes the current theme to the opposite of what is currently active
        and applies the new theme to the application.

        Returns:
            bool: The new dark_mode state after toggling
        """
        self.dark_mode = not self.dark_mode
        self._apply_theme()
        return self.dark_mode

    def _apply_theme(self):
        """
        Apply the currently active theme to the application.
        
        Returns:
            bool: True if the theme was applied successfully, False otherwise
        """
        theme = self._active_stylesheets['dark' if self.dark_mode else 'light']
        app = QApplication.instance()
        if app:
            try:
                app.setStyleSheet(theme)
                return True
            except Exception as e:
                print(f"Failed to load stylesheet: {e}")
                # Fallback to default stylesheet
                if self.dark_mode:
                    app.setStyleSheet("QWidget { background-color: #2d2d2d; color: f0f0f0; }")
                else:
                    app.setStyleSheet("")
                return False

    def _get_stylesheet_content(self, path):
        """Read the content of a stylesheet file"""
        try:
            with open(path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Error reading stylesheet: {e}")
            return ""
        
    def _get_stylesheet_path(self, mode):
        """Get the path of the stylesheet based on the mode"""
        if mode == 'dark':
            return LotusConfig.get_stylesheet("DARK_MODE")
        else:
            return LotusConfig.get_stylesheet("LIGHT_MODE")

    def _capture_base_font_sizes(self):
        """Capture the original font sizes from stylesheets for later adjustments"""
        base_sizes = {}
        base_sizes['light'] = self._extract_font_sizes(self._base_stylesheets['light'])
        base_sizes['dark'] = self._extract_font_sizes(self._base_stylesheets['dark'])
        
        return base_sizes
    
    def _extract_font_sizes(self, css):
        """
        Extract font sizes from CSS content
        Returns:
            dict: A dictionary mapping widget names to their font sizes
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
    
    def increase_font_size(self):
        """Increase font size by 1 point"""
        # Don't go above 8 points adjustment to keep text readable
        if self._font_size_adjustment < 8:
            self._font_size_adjustment += 1
            self._apply_font_adjustment()
        
    def decrease_font_size(self):
        """Decrease font size by 1 point, with a minimum limit"""
        # Don't go below -4 points adjustment to keep text readable
        if self._font_size_adjustment > -4:
            self._font_size_adjustment -= 1
            self._apply_font_adjustment()
    
    def reset_font_size(self):
        """Reset font size to original values"""
        self._font_size_adjustment = 0
        self._apply_font_adjustment()
        
    
    def _apply_font_adjustment(self):
        """Apply the current font size adjustment to the application"""
        css_light = self._active_stylesheets['light']
        css_dark = self._active_stylesheets['dark']

        for widget, size in self._base_font_sizes['light'].items():
            adjusted_size = max(8, size + self._font_size_adjustment)
            
            css_light = re.sub(
                f"({widget}[^}}]*font-size:)\\s*\\d+px", 
                f"\\1 {adjusted_size}px", 
                css_light
            )
        for widget, size in self._base_font_sizes['dark'].items():
            adjusted_size = max(8, size + self._font_size_adjustment)

            css_dark = re.sub(
                f"({widget}[^}}]*font-size:)\\s*\\d+px", 
                f"\\1 {adjusted_size}px", 
                css_dark
            )
        
        self._active_stylesheets['light'] = css_light
        self._active_stylesheets['dark'] = css_dark

        self._apply_theme()