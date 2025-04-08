# DocumentListView.py
from PyQt5.QtWidgets import QListView
from PyQt5.QtCore import QStringListModel, pyqtSignal


class DocumentListView(QListView):
    lineSelected = pyqtSignal(int)  # When user selects a pattern
    lineDoubleClicked = pyqtSignal(int)  # When user double-clicks a pattern

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.list_model = QStringListModel()
        self.setModel(self.list_model)
        self.setEditTriggers(QListView.NoEditTriggers)
        self.setSelectionMode(QListView.SingleSelection)
        self.clicked.connect(lambda idx: self.lineSelected.emit(idx.row()))
        self.doubleClicked.connect(lambda idx: self.lineDoubleClicked.emit(idx.row()))

    def update_displayed_input(self, updated_lines):
        """Update the displayed input file list."""
        if updated_lines is None:
            raise ValueError("Updated lines cannot be None.")
        self.list_model.setStringList(updated_lines)


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