from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QSplashScreen

from services.lotus_config import LotusConfig


def parse_af_line(line):
    """
    Parse a configuration line into structured fields.

    Extracts template, net, AF value and flags from a configuration line.

    Args:
        line (str): The line text to parse

    Returns:
        dict: Dictionary with parsed fields or None if parsing failed

    Fields in returned dictionary:
        - template: Template name or None if not specified
        - net: Net name
        - af: AF value
        - template_regex: Boolean indicating if template is a regex pattern
        - net_regex: Boolean indicating if net is a regex pattern
        - em: Boolean indicating if EM flag is set
        - sh: Boolean indicating if SH flag is set
    """
    if not line or line.startswith('#'):
        return None

    try:
        fields = {}
        parts = line.strip().split()
        if len(parts) < 2:
            return None

        # Parse template and net from first part
        pattern_part = parts[0].strip("{}")
        if ":" in pattern_part:
            fields['template'], fields['net'] = pattern_part.split(":", 1)
        else:
            fields['template'] = None
            fields['net'] = pattern_part.strip()

        # Parse AF value
        fields['af'] = parts[1]

        # Parse flags
        if len(parts) > 2:
            flags = parts[2]
            fields['template_regex'] = "template-regexp" in flags
            fields['net_regex'] = "net-regexp" in flags
            fields['em'] = "_em" in flags
            fields['sh'] = "_sh" in flags

            # outdated format - stays for backward compatibility
            if "template-regexp" not in flags and "net-regexp" not in flags:
                if "regexp" in flags:
                    fields['net_regex'] = True
        else:
            # if no flags are provided, set defaults
            fields['template_regex'] = False
            fields['net_regex'] = False
            fields['em'] = True
            fields['sh'] = True
        return fields
    except Exception as e:
        print(f"Error parsing line: {line}. Error: {e}")
        return None


def create_splash_screen(app):
    """
    Create a high-quality splash screen that works well on different displays.

    Args:
        app: QApplication instance

    Returns:
        QSplashScreen: Configured splash screen object
    """
    # Load high-resolution image file (recommended size: 1200x800 px)
    splash_pixmap = QPixmap(LotusConfig.get_icon_path("SPLASHSCREEN"))

    # Scale the pixmap based on screen DPI for better appearance
    screen = app.primaryScreen()
    screen_size = screen.size()
    dpi_scale = screen.logicalDotsPerInch() / 96.0  # 96 DPI is standard

    # Target size based on available space (70% of screen width)
    target_width = int(min(1200, screen_size.width() * 0.7))
    scaled_size = QSize(target_width, int(target_width * (splash_pixmap.height() / splash_pixmap.width())))

    # Scale with high-quality transformation
    if dpi_scale > 1 or target_width < splash_pixmap.width():
        splash_pixmap = splash_pixmap.scaled(
            scaled_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pixmap.mask())  # For transparent images

    font = QFont("Open Sans ExtraBold", 24)
    font.setBold(True)
    font.setItalic(True)
    splash.setFont(font)

    splash.setEnabled(False)
    splash.show()
    splash.showMessage("Loading Lotus...", alignment=Qt.AlignCenter, color=Qt.white)
    return splash