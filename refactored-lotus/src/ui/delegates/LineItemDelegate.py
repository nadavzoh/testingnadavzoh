from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QRect, QSize

from src.core.services.ThemeService import ThemeService
from src.core.models.LineModelInterface import LineModelInterface


class LineItemDelegate(QStyledItemDelegate):
    """
    Custom delegate for rendering line items with validation status-based colors.
    
    This delegate renders items in a list view with colors that correspond to
    their validation status. It also handles proper indentation, selection highlighting,
    and ellipsis for long text.
    """
    
    # Custom role for storing validation status
    ValidationStatusRole = Qt.UserRole + 1
    
    def __init__(self, theme_service: ThemeService, parent=None):
        """
        Initialize the delegate with a theme service.
        
        Args:
            theme_service: Service for getting theme colors
            parent: Parent object
        """
        super().__init__(parent)
        self._theme_service = theme_service
        self._default_font = QFont("Monospace", 10)
        self._margin = 4
    
    def paint(self, painter: QPainter, option, index):
        """
        Paint the item.
        
        Args:
            painter: The painter to use for drawing
            option: The style options to use
            index: The model index to paint
        """
        # Get the validation status from the model
        validation_status = index.data(self.ValidationStatusRole)
        if validation_status is None:
            validation_status = LineModelInterface.VALID  # Default to valid
        
        # Prepare the painter
        painter.save()
        painter.setFont(self._default_font)
        
        # Handle selection highlighting
        if option.state & QStyle.State_Selected:
            # light blue background for selected items
            # TODO: get from theme service, depends on the theme
            painter.fillRect(option.rect, QColor("#ADD8E6"))
        
        # Get text color based on validation status
        text_color = self._theme_service.get_status_color(validation_status)
        # this returns a string but we need a QColor
        if isinstance(text_color, str):
            text_color = QColor(text_color)
        elif not isinstance(text_color, QColor):
            raise TypeError("Expected QColor or string for text color")
        
        painter.setPen(text_color)
        
        # Draw the text with appropriate margin
        text_rect = option.rect.adjusted(self._margin, 0, -self._margin, 0)
        text = index.data(Qt.DisplayRole)
        if text:
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)
        
        painter.restore()
    
    def sizeHint(self, option, index):
        """
        Get the size hint for an item.
        
        Args:
            option: The style options to use
            index: The model index
            
        Returns:
            QSize: The recommended size for the item
        """
        text = index.data(Qt.DisplayRole)
        font_metrics = option.fontMetrics
        
        # Calculate width based on text
        text_width = font_metrics.horizontalAdvance(text) if text else 0
        width = text_width + 2 * self._margin
        
        # Calculate height based on font
        height = font_metrics.height() + 2
        
        return QSize(width, height)
    
    @staticmethod
    def set_validation_status(item, status: int) -> None:
        """
        Set the validation status for an item.
        
        Args:
            item: The item to set the status for (QStandardItem)
            status: The validation status
        """
        item.setData(status, LineItemDelegate.ValidationStatusRole)
