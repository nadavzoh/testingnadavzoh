from PyQt5.QtWidgets import QApplication
from src.Services.LotusConfig import LotusConfig

class LotusThemeManager:
    def __init__(self, dark_mode=False):
        self.dark_mode = dark_mode
        self.apply_theme(dark_mode)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme(self.dark_mode)

    def apply_theme(self, dark_mode):
        """Apply the theme to the application."""
        stylesheet_name = "DARK_MODE" if dark_mode else "LIGHT_MODE"
        stylesheet_path = LotusConfig.get_stylesheet(stylesheet_name)
        app = QApplication.instance()

        try:
            with open(stylesheet_path, "r") as stylesheet_file:
                app.setStyleSheet(stylesheet_file.read())
        except Exception as e:
            print(f"Failed to load stylesheet: {e}")
            # fallback to default stylesheet
            if dark_mode:
                app.setStyleSheet("QWidget { background-color: #2d2d2d; color: f0f0f0; }")
            else:
                app.setStyleSheet("")