from typing import Optional, List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from src.core.models.DocumentModel import DocumentModel
from src.core.models.LineModelInterface import LineModelInterface
from src.ui.delegates.LineItemDelegate import LineItemDelegate
from src.ui.views.DocumentListView import DocumentListView

class DocumentPresenter(QObject):
    """
    Presenter for document view components.
    
    This class acts as a mediator between the document model and the view,
    translating model updates into view updates and vice versa.
    It uses Qt's signals and slots mechanism for communication.
    
    Signals:
        documentLoaded: Emitted when a document is loaded
        documentSaved: Emitted when a document is saved
        lineSelected: Emitted when a line is selected, with the line content
        lineAdded: Emitted when a line is added
        lineRemoved: Emitted when a line is removed
        lineUpdated: Emitted when a line is updated
        contentChanged: Emitted when the document content changes (e.g., after undo/redo)
        selectionChanged: Emitted when the selection in the document changes
    """
    
    # Signals for view updates
    documentLoaded = pyqtSignal(str)    # Emits file path
    documentSaved = pyqtSignal(str)     # Emits file path
    lineSelected = pyqtSignal(str)      # Emits line content
    lineAdded = pyqtSignal()
    lineRemoved = pyqtSignal()
    lineUpdated = pyqtSignal(int)       # Emits line index
    contentChanged = pyqtSignal(list)   # Emits list of lines
    selectionChanged = pyqtSignal(int)  # Emits selected index
    
    def __init__(self, document_model: Optional[DocumentModel] = None, document_view: Optional[DocumentListView] = None):
        """
        Initialize the presenter with a document model and view.
        
        Args:
            document_model: The document model to present
            document_view: The view to update
        """
        super().__init__()
        self._document_model = document_model
        self._document_view = document_view
        self._list_model = QStandardItemModel()
        
        # Connect to view if provided
        if document_view:
            self.set_document_view(document_view)
    
    def set_document_model(self, document_model: DocumentModel) -> None:
        """
        Set the document model.
        
        Args:
            document_model: The document model to present
        """
        self._document_model = document_model
        self._update_list_model()
        
        if document_model.get_file_path():
            self.documentLoaded.emit(document_model.get_file_path())
    
    def set_document_view(self, document_view: DocumentListView) -> None:
        """
        Set the document view and connect signals.
        
        Args:
            document_view: The document view to update
        """
        self._document_view = document_view
        
        # Connect view signals to presenter methods
        if self._document_view:
            self._document_view.lineSelected.connect(self.handle_line_selection)
            self._document_view.contentRefreshRequested.connect(self.handle_content_refresh_request)
            self._document_view.insertRequested.connect(self.handle_insert_request)
            self._document_view.editRequested.connect(self.handle_edit_request)
            self._document_view.deleteRequested.connect(self.handle_delete_request)
            ## CONTINUE ADDING HANDLERS, but remember to delete it from ActionManager
            # self._document_view.moveUpRequested.connect(self.move_line_up)
            # self._document_view.moveDownRequested.connect(self.move_line_down)
            # self._document_view.duplicateRequested.connect(self.duplicate_line)
            # self._document_view.toggleCommentRequested.connect(self.toggle_comment)
            #... continue with other actions

            
            # Connect presenter signals to view methods
            self.contentChanged.connect(self._document_view.set_content)
            self.selectionChanged.connect(self._document_view.set_selected_index)
            
            # Set the list model on the view
            self._document_view.set_model(self._list_model)
    
    def get_list_model(self) -> QStandardItemModel:
        """
        Get the list model for the view.
        
        Returns:
            QStandardItemModel: The list model
        """
        return self._list_model
    
    def _update_list_model(self) -> None:
        """
        Update the list model with data from the document model.
        """
        if not self._document_model:
            return
        
        self._list_model.clear()
        
        for i, line in enumerate(self._document_model.get_all_lines()):
            item = QStandardItem(line)
            
            # Get validation status from line model if available
            line_model = self._document_model.get_line_model(i)
            validation_status = LineModelInterface.VALID
            
            if line_model:
                validation_status = line_model.get_status()
            
            # Set validation status for styling by the delegate
            LineItemDelegate.set_validation_status(item, validation_status)
            
            self._list_model.appendRow(item)
    
    def handle_line_selection(self, index: int) -> None:
        """
        Handle line selection in the view.
        
        Args:
            index: The index of the selected line
        """
        if not self._document_model:
            return
        
        self._document_model.set_selected_index(index)
        line = self._document_model.get_line(index)
        
        if line:
            self.lineSelected.emit(line)
    
    def add_line(self, content: str, index: int = -1) -> None:
        """
        Add a line to the document.
        
        Args:
            content: The content of the new line
            index: The index to insert at (-1 for end)
        """
        if not self._document_model:
            return
        
        self._document_model.insert_line(content, index)
        self._update_list_model()
        self.lineAdded.emit()
    
    def remove_line(self, index: int) -> None:
        """
        Remove a line from the document.
        
        Args:
            index: The index of the line to remove
        """
        if not self._document_model:
            return
        
        self._document_model.delete_line(index)
        self._update_list_model()
        self.lineRemoved.emit()
    
    def update_line(self, content: str, index: int) -> None:
        """
        Update a line in the document.
        
        Args:
            content: The new content for the line
            index: The index of the line to update
        """
        if not self._document_model:
            return
        
        self._document_model.edit_line(content, index)
        
        # Update the item in the list model
        item = self._list_model.item(index)
        if item:
            item.setText(content)
            
            # Update validation status
            line_model = self._document_model.get_line_model(index)
            if line_model:
                LineItemDelegate.set_validation_status(item, line_model.get_status())
        
        self.lineUpdated.emit(index)
    
    def toggle_comment(self, index: int) -> bool:
        """
        Toggle comment status on a line.
        
        Args:
            index: The index of the line to toggle
        """
        if not self._document_model:
            return False
        
        success = self._document_model.toggle_comment(index)
        if not success:
            return False
        
        # Update the item in the list model
        item = self._list_model.item(index)
        if item:
            line = self._document_model.get_line(index)
            item.setText(line)
            
            # Update validation status
            line_model = self._document_model.get_line_model(index)
            if line_model:
                LineItemDelegate.set_validation_status(item, line_model.get_status())
        
        self.lineUpdated.emit(index)
        return success
    def move_line_up(self, index: int = None) -> bool:
        """
        Move a line up one position.
        
        Args:
            index: The index of the line to move, or None to use selected index
            
        Returns:
            bool: True if the line was moved, False otherwise
        """
        if not self._document_model:
            return False
        
        # Use selected index if none provided
        if index is None:
            index = self._document_model.get_selected_index()
            if index < 0:
                return False
        
        result = self._document_model.move_line_up(index)
        if result:
            self._update_list_model()
            self.contentChanged.emit(self._document_model.get_content())
            self.selectionChanged.emit(index - 1)
            
        return result
    
    def move_line_down(self, index: int = None) -> bool:
        """
        Move a line down one position.
        
        Args:
            index: The index of the line to move, or None to use selected index
            
        Returns:
            bool: True if the line was moved, False otherwise
        """
        if not self._document_model:
            return False
        
        # Use selected index if none provided
        if index is None:
            index = self._document_model.get_selected_index()
            if index < 0:
                return False
        
        result = self._document_model.move_line_down(index)
        if result:
            self._update_list_model()
            self.contentChanged.emit(self._document_model.get_content())
            self.selectionChanged.emit(index + 1)
            
        return result
    
    def duplicate_line(self, index: int = None) -> bool:
        """
        Duplicate a line.
        
        Args:
            index: The index of the line to duplicate, or None to use selected index
            
        Returns:
            bool: True if the line was duplicated, False otherwise
        """
        if not self._document_model:
            return False
        
        # Use selected index if none provided
        if index is None:
            index = self._document_model.get_selected_index()
            if index < 0:
                return False
        
        result = self._document_model.duplicate_line(index)
        if result:
            self._update_list_model()
            self.contentChanged.emit(self._document_model.get_content())
            self.selectionChanged.emit(index + 1)
            
        return result
    
    def load_document(self, file_path: str) -> bool:
        """
        Load a document from a file.
        
        Args:
            file_path: The path to the file to load
            
        Returns:
            bool: True if the document was loaded successfully
        """
        if not self._document_model:
            return False
        
        if self._document_model.load_file(file_path):
            self._update_list_model()
            self.documentLoaded.emit(file_path)
            return True
        return False
    
    def save_document(self, file_path: Optional[str] = None) -> bool:
        """
        Save the document to a file.
        
        Args:
            file_path: The path to save to. If None, use current path.
            
        Returns:
            bool: True if the document was saved successfully
        """
        if not self._document_model:
            return False
        
        if self._document_model.save_file(file_path):
            path = file_path if file_path else self._document_model.get_file_path()
            self.documentSaved.emit(path)
            return True
        return False
    
    def has_unsaved_changes(self) -> bool:
        """
        Check if the document has unsaved changes.
        
        Returns:
            bool: True if there are unsaved changes
        """
        if not self._document_model:
            return False
        
        return self._document_model.has_unsaved_changes()
    
    def can_undo(self) -> bool:
        """
        Check if undo is available.
        
        Returns:
            bool: True if undo is available
        """
        if not self._document_model:
            return False
        
        return self._document_model.can_undo()
    
    def can_redo(self) -> bool:
        """
        Check if redo is available.
        
        Returns:
            bool: True if redo is available
        """
        if not self._document_model:
            return False
        
        return self._document_model.can_redo()
    
    def undo(self) -> bool:
        """
        Undo the last action.
        
        Returns:
            bool: True if an action was undone, False otherwise
        """
        if not self._document_model:
            return False
            
        result = self._document_model.undo()
        if result:
            self._update_list_model()
            self.contentChanged.emit(self._document_model.get_content())
            
            # Update selection
            selected_index = self._document_model.get_selected_index()
            if selected_index >= 0:
                self.selectionChanged.emit(selected_index)
                
        return result
    
    def redo(self) -> bool:
        """
        Redo the last undone action.
        
        Returns:
            bool: True if an action was redone, False otherwise
        """
        if not self._document_model:
            return False
            
        result = self._document_model.redo()
        if result:
            self._update_list_model()
            self.contentChanged.emit(self._document_model.get_content())
            
            # Update selection
            selected_index = self._document_model.get_selected_index()
            if selected_index >= 0:
                self.selectionChanged.emit(selected_index)
                
        return result
        
    def handle_content_refresh_request(self):
        """
        Handle request to refresh content from the view.
        
        This updates the view with the current state of the document model.
        """
        if not self._document_model:
            return
            
        self._update_list_model()
        self.contentChanged.emit(self._document_model.get_content())
        
        # Update selection
        selected_index = self._document_model.get_selected_index()
        if selected_index >= 0:
            self.selectionChanged.emit(selected_index)
