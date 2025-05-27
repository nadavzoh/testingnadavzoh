from typing import Optional, List, Any, Callable
from PyQt5.QtWidgets import (QWidget, QListView, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from src.ui.views.IDocumentView import IDocumentView
from src.ui.delegates.LineItemDelegate import LineItemDelegate
from src.core.services.ThemeService import ThemeService


class DocumentListView(QWidget, IDocumentView):
    """
    Document list view that displays and allows editing of a document.
    
    This widget displays document content as a list of lines with color
    coding based on validation status. It provides buttons for basic
    operations (insert, edit, delete).
    
    Signals:
        lineSelected: Emitted when a line is selected
        lineDoubleClicked: Emitted when a line is double-clicked
        insertRequested: Emitted when the insert button is clicked
        editRequested: Emitted when the edit button is clicked
        deleteRequested: Emitted when the delete button is clicked
    """
    
    # Signals
    lineSelected = pyqtSignal(int)
    lineDoubleClicked = pyqtSignal(int)
    insertRequested = pyqtSignal()
    editRequested = pyqtSignal()
    deleteRequested = pyqtSignal()
    
    def __init__(self, theme_service: ThemeService, parent=None):
        """
        Initialize the document list view.
        
        Args:
            theme_service: Service for theme colors
            parent: Parent widget
        """
        super().__init__(parent)
        self._theme_service = theme_service
        self._list_view = None
        self._model = None
        self._delegate = None
        self._title = ""
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)
        
        # Create list view
        self._list_view = QListView()
        self._list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self._list_view.setAlternatingRowColors(True)
        
        # Create delegate for rendering items
        self._delegate = LineItemDelegate(self._theme_service)
        self._list_view.setItemDelegate(self._delegate)
        
        # Create default model
        self._model = QStandardItemModel()
        self._list_view.setModel(self._model)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self._insert_button = QPushButton("Insert")
        self._edit_button = QPushButton("Edit")
        self._delete_button = QPushButton("Delete")
        
        # Add buttons to layout
        button_layout.addWidget(self._insert_button)
        button_layout.addWidget(self._edit_button)
        button_layout.addWidget(self._delete_button)
        
        # Add widgets to main layout
        main_layout.addWidget(self._list_view)
        main_layout.addLayout(button_layout)
        
        # Set focus policy
        self.setFocusPolicy(Qt.StrongFocus)
    
    def _connect_signals(self):
        """Connect widget signals."""
        # Connect list view signals
        self._list_view.clicked.connect(self._on_line_clicked)
        self._list_view.doubleClicked.connect(self._on_line_double_clicked)
        
        # Connect button signals
        self._insert_button.clicked.connect(self.insertRequested)
        self._edit_button.clicked.connect(self.editRequested)
        self._delete_button.clicked.connect(self.deleteRequested)
    
    def _on_line_clicked(self, index: QModelIndex):
        """
        Handle line click.
        
        Args:
            index: The model index that was clicked
        """
        self.lineSelected.emit(index.row())
    
    def _on_line_double_clicked(self, index: QModelIndex):
        """
        Handle line double-click.
        
        Args:
            index: The model index that was double-clicked
        """
        self.lineDoubleClicked.emit(index.row())
    
    def set_model(self, model: QStandardItemModel):
        """
        Set the data model.
        
        Args:
            model: The model to use
        """
        self._model = model
        self._list_view.setModel(model)
    
    def get_model(self) -> QStandardItemModel:
        """
        Get the data model.
        
        Returns:
            QStandardItemModel: The data model
        """
        return self._model
    
    # IView implementation
    def show(self) -> None:
        """Show the view."""
        super().show()
    
    def hide(self) -> None:
        """Hide the view."""
        super().hide()
    
    def set_title(self, title: str) -> None:
        """
        Set the title of the view.
        
        Args:
            title: The title to set
        """
        self._title = title
    
    # IDocumentView implementation
    def set_content(self, content: List[str]) -> None:
        """
        Set the content of the view.
        
        Args:
            content: The content as a list of strings
        """
        self._model.clear()
        for line in content:
            self._model.appendRow(QStandardItem(line))
    
    def get_selected_index(self) -> int:
        """
        Get the index of the currently selected line.
        
        Returns:
            int: The index of the selected line, or -1 if no line is selected
        """
        selected_indexes = self._list_view.selectedIndexes()
        if selected_indexes:
            return selected_indexes[0].row()
        return -1
    
    def set_selected_index(self, index: int) -> None:
        """
        Set the index of the selected line.
        
        Args:
            index: The index to select
        """
        if 0 <= index < self._model.rowCount():
            model_index = self._model.index(index, 0)
            self._list_view.setCurrentIndex(model_index)
            self._list_view.scrollTo(model_index)
    
    def update_line(self, index: int, content: str) -> None:
        """
        Update a line in the view.
        
        Args:
            index: The index of the line to update
            content: The new content for the line
        """
        if 0 <= index < self._model.rowCount():
            self._model.setData(self._model.index(index, 0), content, Qt.DisplayRole)
