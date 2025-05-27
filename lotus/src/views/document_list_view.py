from PyQt5.QtWidgets import QListView, QShortcut, QStyle, QStyleOptionViewItem, QStyledItemDelegate
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex
from PyQt5.QtGui import QKeyEvent, QKeySequence, QPainter
from models.af_line_list_model import AfLineListModel


class LineItemDelegate(QStyledItemDelegate):
    """
    Custom delegate for styling line items in the DocumentListView.

    This delegate handles custom color rendering for line items, including
    maintaining proper colors during selection states.
    """

    def paint(self, painter, option, index):
        """
        Paint the line item with custom colors if available.

        Args:
            painter (QPainter): The painter used to draw the item
            option (QStyleOptionViewItem): Style options for the item
            index (QModelIndex): Model index for the item being painted
        """
        color = index.data(AfLineListModel.ColorRole)

        options = QStyleOptionViewItem(option)

        # If item is selected, preserve the text color but use selection background
        if option.state & QStyle.State_Selected:
            # Keep the text color but use selection background
            options.palette.setColor(options.palette.HighlightedText,
                                     color if color is not None else options.palette.text().color())

        elif color is not None:
            options.palette.setColor(options.palette.Text, color)

        super().paint(painter, options, index)


class DocumentListView(QListView):
    """
    A specialized list view for displaying document lines with color coding and interactive features.

    This component serves as the main interface for displaying and interacting with document lines,
    supporting selection, double-clicking, commenting, and duplicating operations. It uses
    a custom LineItemDelegate to render items with appropriate colors.

    Signals:
        lineSelected (int): Emitted when a line is selected, with the line index
        lineDoubleClicked (int): Emitted when a line is double-clicked, with the line index
        cancelSelection: Emitted when the selection is cancelled (e.g., via Escape key)
        toggleCommentRequested: Emitted when a line comment toggle is requested
        duplicateLineRequested: Emitted when a line duplication is requested
        moveLineUpRequested: Emitted when a line move up is requested
        moveLineDownRequested: Emitted when a line move down is requested
    """

    lineSelected = pyqtSignal(int)  # When user selects a pattern
    lineDoubleClicked = pyqtSignal(int)  # When user double-clicks a pattern
    cancelSelection = pyqtSignal()  # When user cancels the selection
    toggleCommentRequested = pyqtSignal()  # When user toggles comment on a line
    duplicateLineRequested = pyqtSignal()  # When user duplicates a line
    moveLineUpRequested = pyqtSignal()  # When user moves a line up
    moveLineDownRequested = pyqtSignal()  # When user moves a line down

    def __init__(self, parent=None):
        """
        Initialize the DocumentListView.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        self._model = AfLineListModel(self)
        self.setModel(self._model)

        # Set our custom delegate for rendering items
        self.setItemDelegate(LineItemDelegate())

        self.setAlternatingRowColors(True)
        self.setUniformItemSizes(True)

        self.clicked.connect(self._on_item_selected)
        self.doubleClicked.connect(self._on_item_double_clicked)

        # Keyboard shortcuts
        esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc_shortcut.activated.connect(self._on_escape_key)

        comment_shortcut = QShortcut(QKeySequence("Ctrl+/"), self)
        comment_shortcut.activated.connect(self.toggleCommentRequested)

        duplicate_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        duplicate_shortcut.activated.connect(self.duplicateLineRequested)

    def _on_item_selected(self, index):
        """Handle item selection"""
        if index.isValid():
            self.lineSelected.emit(index.row())

    def _on_item_double_clicked(self, index):
        """Handle item double-click"""
        if index.isValid():
            self.lineDoubleClicked.emit(index.row())

    def _on_escape_key(self):
        """Handle escape key press"""
        self.clearSelection()
        self.cancelSelection.emit()

    def keyPressEvent(self, event):
        """
        Handle keyboard events in the list view.

        Implements custom behavior for:
        - Arrow keys (Up, Down, Home, End, PageUp, PageDown) for navigation
        - Enter key to simulate double-click on the selected item
        - Delete key handling (deferred to controller)

        Args:
            event (QKeyEvent): The key event to process
        """
        key = event.key()
        modifiers = event.modifiers()

        # Handle Enter key to simulate double-click
        if key in (Qt.Key_Return, Qt.Key_Enter):
            current_index = self.currentIndex()
            if current_index.isValid():
                self.lineDoubleClicked.emit(current_index.row())

        # Handle Ctrl+Up and Ctrl+Down for moving selection
        elif key == Qt.Key_Up and modifiers == Qt.AltModifier:
            self.moveLineUpRequested.emit()

        elif key == Qt.Key_Down and modifiers == Qt.AltModifier:
            self.moveLineDownRequested.emit()

        # Handle keyboard navigation with arrow keys
        elif key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown):
            super().keyPressEvent(event)

            current_index = self.currentIndex()
            if current_index.isValid():
                self.lineSelected.emit(current_index.row())

        elif event.key() == Qt.Key_Delete and self.get_selected_index() >= 0:
            # Let the controller handle the delete action
            # The view will be updated through the model
            pass  # Leave the actual handling to the controller
        else:
            super().keyPressEvent(event)

    def get_selected_index(self):
        """Get the currently selected row index"""
        indexes = self.selectedIndexes()
        if indexes:
            return indexes[0].row()
        return -1

    def select_line(self, row):
        """Select a specific line by row index"""
        if 0 <= row < self._model.rowCount():
            index = self._model.index(row, 0)
            self.setCurrentIndex(index)
            self.scrollTo(index)
            return True
        return False

    def update_content(self, content):
        """Update the content of the view with new lines"""
        if isinstance(content, list):
            self._model.setContentFromStringList(content)

    def reset_colors(self):
        """Reset all line colors"""
        self._model.updateAllColors()

    def set_line_color(self, row, color):
        """Set the color for a specific line"""
        if 0 <= row < self._model.rowCount():
            index = self._model.index(row, 0)
            self._model.setData(index, color, AfLineListModel.ColorRole)

    def get_model(self):
        """Get the underlying AfLineListModel"""
        return self._model