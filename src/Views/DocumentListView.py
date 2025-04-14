from PyQt5.QtWidgets import QListView, QShortcut
from PyQt5.QtCore import Qt, QStringListModel, pyqtSignal
from PyQt5.QtGui import QKeyEvent


class DocumentListView(QListView):
    lineSelected = pyqtSignal(int)  # When user selects a pattern
    lineDoubleClicked = pyqtSignal(int)  # When user double-clicks a pattern
    cancelSelection = pyqtSignal()  # When user cancels the selection
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.list_model = QStringListModel()
        self.setModel(self.list_model)
        self.setEditTriggers(QListView.NoEditTriggers)
        self.setSelectionMode(QListView.SingleSelection)
        self.clicked.connect(lambda idx: self.lineSelected.emit(idx.row()))
        self.doubleClicked.connect(lambda idx: self.lineDoubleClicked.emit(idx.row()))
        # set shortcut when pressing 'ESC' - the current item selection will is unselected, emit a signal to controller

    def update_content(self, data):
        """Update the displayed input file list."""
        if data is None:
            raise ValueError("Updated data cannot be None.")
        self.list_model.setStringList(data)

    def get_selected_item(self):
        """Get the currently selected item."""
        indexes = self.selectedIndexes()
        if indexes:
            index = indexes[0].row()
            return index, self.list_model.data(indexes[0])
        return -1, None

    def get_selected_index(self):
        """Get the currently selected index."""
        indexes = self.selectedIndexes()
        if indexes:
            return indexes[0].row()
        return -1

    def select_line(self, index):
        """Select a specific line by index."""
        if 0 <= index < self.list_model.rowCount():
            self.setCurrentIndex(self.list_model.index(index, 0))

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.clearSelection()
            self.selectionModel().clear()
            self.lineSelected.emit(-1)
            self.cancelSelection.emit()

