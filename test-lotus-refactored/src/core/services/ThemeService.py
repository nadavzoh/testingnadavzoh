from typing import Dict
from PyQt5.QtGui import QColor

class ThemeService:
    """
    Service for managing theme colors and styles.
    
    This class provides colors and styles for the application,
    including colors for different validation states of lines.
    It supports light and dark themes with appropriate colors for each.
    """
    
    # Theme types
    LIGHT_THEME = "light"
    DARK_THEME = "dark"
    
    # Color mapping keys for validation states
    VALID_COLOR = "valid"
    INVALID_COLOR = "invalid"
    WARNING_COLOR = "warning"
    COMMENT_COLOR = "comment"
    SELECTED_BG_COLOR = "selected_bg"
    
    def __init__(self, theme_type: str = LIGHT_THEME):
        """
        Initialize the theme service with a specified theme.
        
        Args:
            theme_type: The theme type to use (light or dark)
        """
        self._theme_type = theme_type
        self._initialize_colors()
    
    def _initialize_colors(self) -> None:
        """
        Initialize color maps for light and dark themes.
        """
        # Define colors for light theme
        self._light_theme_colors = {
            self.VALID_COLOR: QColor(0, 0, 0),           # Black for valid lines
            self.INVALID_COLOR: QColor(255, 0, 0),       # Red for invalid lines
            self.WARNING_COLOR: QColor(255, 165, 0),     # Orange for warning lines
            self.COMMENT_COLOR: QColor(0, 128, 0),       # Green for comment lines
            self.SELECTED_BG_COLOR: QColor(173, 216, 230) # Light blue for selection
        }
        
        # Define colors for dark theme
        self._dark_theme_colors = {
            self.VALID_COLOR: QColor(220, 220, 220),     # Light gray for valid lines
            self.INVALID_COLOR: QColor(255, 99, 71),     # Tomato red for invalid lines
            self.WARNING_COLOR: QColor(255, 165, 0),     # Orange for warning lines
            self.COMMENT_COLOR: QColor(144, 238, 144),   # Light green for comment lines
            self.SELECTED_BG_COLOR: QColor(70, 130, 180) # Steel blue for selection
        }
    
    def get_color(self, color_key: str) -> QColor:
        """
        Get a color by key based on the current theme.
        
        Args:
            color_key: The key for the color to get
            
        Returns:
            QColor: The color corresponding to the key in the current theme
        """
        if self._theme_type == self.DARK_THEME:
            return self._dark_theme_colors.get(color_key, QColor(0, 0, 0))
        else:
            return self._light_theme_colors.get(color_key, QColor(0, 0, 0))
    
    def get_validation_color(self, validation_status: int) -> QColor:
        """
        Get the color for a validation status.
        
        Args:
            validation_status: The validation status (0=valid, 1=invalid, 2=warning, 3=comment)
            
        Returns:
            QColor: The color corresponding to the validation status
        """
        if validation_status == 0:  # Valid
            return self.get_color(self.VALID_COLOR)
        elif validation_status == 1:  # Invalid
            return self.get_color(self.INVALID_COLOR)
        elif validation_status == 2:  # Warning
            return self.get_color(self.WARNING_COLOR)
        elif validation_status == 3:  # Comment
            return self.get_color(self.COMMENT_COLOR)
        else:
            return self.get_color(self.VALID_COLOR)  # Default to valid color
    
    def set_theme(self, theme_type: str) -> None:
        """
        Set the current theme.
        
        Args:
            theme_type: The theme type to use (light or dark)
        """
        if theme_type in [self.LIGHT_THEME, self.DARK_THEME]:
            self._theme_type = theme_type
    
    def get_theme(self) -> str:
        """
        Get the current theme type.
        
        Returns:
            str: The current theme type
        """
        return self._theme_type
