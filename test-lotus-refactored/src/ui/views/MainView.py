from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

from src.ui.views.IView import IView
from src.core.services.ThemeService import ThemeService
from src.ui.views.DocumentListView import DocumentListView


class MainView(QMainWindow, IView):
    """
    Main application view with split layout.
    
    This class represents the main window of the application with a
    split layout containing left and right panels. The left panel
    contains a tab widget for documents and action buttons.
    
    Signals:
        documentTabChanged: Emitted when the current document tab changes
        exitRequested: Emitted when exit is requested
    """
    
    # Signals
    documentTabChanged = pyqtSignal(int)
    exitRequested = pyqtSignal()
    
    def __init__(self, theme_service: ThemeService, parent=None):
        """
        Initialize the main view.
        
        Args:
            theme_service: Service for theme colors
            parent: Parent widget
        """
        super().__init__(parent)
        self._theme_service = theme_service
        self._document_views = {}  # Dictionary of document views by tab index
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the UI components."""
        # Set window properties
        self.setWindowTitle("Lotus")
        self.resize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create main splitter (vertical)
        self._main_splitter = QSplitter(Qt.Vertical)
        
        # Create top widget (to be filled later)
        self._top_widget = QWidget()
        self._top_layout = QHBoxLayout(self._top_widget)
        
        # Create top left widget (smaller, to be filled later)
        self._top_left_widget = QWidget()
        self._top_left_layout = QVBoxLayout(self._top_left_widget)
        self._top_left_widget.setLayout(self._top_left_layout)
        
        # Create right panel (to be filled later)
        self._right_panel = QWidget()
        self._right_layout = QVBoxLayout(self._right_panel)
        self._right_panel.setLayout(self._right_layout)
        
        # Create bottom left widget with tab widget
        self._bottom_left_widget = QWidget()
        self._bottom_left_layout = QVBoxLayout(self._bottom_left_widget)
        
        # Create document tabs
        self._document_tabs = QTabWidget()
        self._document_tabs.setTabsClosable(False)  # Tabs cannot be closed by the user
        self._document_tabs.setMovable(False)      # Tabs cannot be reordered
        
        # Add tabs to bottom left layout
        self._bottom_left_layout.addWidget(self._document_tabs)
        
        # Add top widgets to top layout
        self._top_layout.addWidget(self._top_left_widget, 1)  # Top left (smaller)
        self._top_layout.addWidget(self._right_panel, 2)     # Right panel
        
        # Add widgets to main splitter
        self._main_splitter.addWidget(self._top_widget)
        self._main_splitter.addWidget(self._bottom_left_widget)
        
        # Set initial splitter sizes (30% top, 70% bottom)
        self._main_splitter.setSizes([300, 700])
        
        # Add main splitter to main layout
        main_layout.addWidget(self._main_splitter)
    
    def _connect_signals(self):
        """Connect widget signals."""
        # Connect tab widget signals
        self._document_tabs.currentChanged.connect(self._on_tab_changed)
    
    def _on_tab_changed(self, index: int):
        """
        Handle tab change.
        
        Args:
            index: The index of the new tab
        """
        self.documentTabChanged.emit(index)
    
    def add_document_tab(self, title: str, document_view: DocumentListView) -> int:
        """
        Add a document tab.
        
        Args:
            title: The title for the tab
            document_view: The document view to add
            
        Returns:
            int: The index of the added tab
        """
        index = self._document_tabs.addTab(document_view, title)
        self._document_views[index] = document_view
        return index
    
    def get_document_view(self, index: int) -> Optional[DocumentListView]:
        """
        Get a document view by tab index.
        
        Args:
            index: The tab index
            
        Returns:
            Optional[DocumentListView]: The document view, or None if not found
        """
        return self._document_views.get(index)
    
    def get_current_document_view(self) -> Optional[DocumentListView]:
        """
        Get the currently active document view.
        
        Returns:
            Optional[DocumentListView]: The current document view, or None if none is active
        """
        current_index = self._document_tabs.currentIndex()
        if current_index >= 0:
            return self._document_views.get(current_index)
        return None
    
    def set_current_tab(self, index: int) -> None:
        """
        Set the current tab.
        
        Args:
            index: The tab index to select
        """
        if 0 <= index < self._document_tabs.count():
            self._document_tabs.setCurrentIndex(index)
    
    def get_tab_count(self) -> int:
        """
        Get the number of tabs.
        
        Returns:
            int: The number of tabs
        """
        return self._document_tabs.count()
    
    def get_current_tab_index(self) -> int:
        """
        Get the index of the current tab.
        
        Returns:
            int: The index of the current tab, or -1 if no tab is selected
        """
        return self._document_tabs.currentIndex()
    
    def clear_tabs(self) -> None:
        """Clear all tabs."""
        self._document_tabs.clear()
        self._document_views.clear()
    
    def set_tab_title(self, index: int, title: str) -> None:
        """
        Set the title of a tab.
        
        Args:
            index: The tab index
            title: The new title
        """
        if 0 <= index < self._document_tabs.count():
            self._document_tabs.setTabText(index, title)
    
    def set_right_panel(self, widget: QWidget) -> None:
        """
        Set the widget in the right panel.
        
        Args:
            widget: The widget to set
        """
        # Clear existing widgets
        while self._right_layout.count():
            item = self._right_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Add the new widget
        self._right_layout.addWidget(widget)
    
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
        self.setWindowTitle(title)
    
    def closeEvent(self, event):
        """
        Handle close event.
        
        Args:
            event: The close event
        """
        self.exitRequested.emit()
        event.ignore()  # Let the presenter decide whether to close
