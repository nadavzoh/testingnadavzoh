from typing import Optional, List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from src.ui.views.DocumentListView import DocumentListView
from src.presenters.DocumentPresenter import DocumentPresenter


class ActionManager(QObject):
    """
    Manages application-level actions.
    
    This class is responsible for coordinating actions between different parts
    of the application, such as handling undo/redo operations, moving lines,
    and other document editing operations.
    
    Signals:
        actionCompleted: Emitted when an action is completed
        actionFailed: Emitted when an action fails
    """
    
    # Signals
    actionCompleted = pyqtSignal(str)  # Message about the completed action
    actionFailed = pyqtSignal(str)     # Error message about the failed action
    
    def __init__(self):
        """Initialize the action manager."""
        super().__init__()
        self._document_views: Dict[int, DocumentListView] = {}
        self._document_presenters: Dict[int, DocumentPresenter] = {}
        
    def register_document(self, index: int, document_view: DocumentListView, document_presenter: DocumentPresenter):
        """
        Register a document with the action manager.
        
        Args:
            index: The index of the document tab
            document_view: The document view to register
            document_presenter: The document presenter to register
        """
        self._document_views[index] = document_view
        self._document_presenters[index] = document_presenter
        
        # Connect signals
        document_view.contentRefreshRequested.connect(document_presenter.handle_content_refresh_request)
        document_presenter.contentChanged.connect(lambda content: document_view.set_content(content))
        document_presenter.selectionChanged.connect(document_view.set_selected_index)
        
        # Connect insert/edit/delete signals
        document_view.insertRequested.connect(lambda: self._handle_insert_requested(index))
        document_view.editRequested.connect(lambda: self._handle_edit_requested(index))
        document_view.deleteRequested.connect(lambda: self._handle_delete_requested(index))
        
    def unregister_document(self, index: int):
        """
        Unregister a document from the action manager.
        
        Args:
            index: The index of the document tab to unregister
        """
        if index in self._document_views:
            del self._document_views[index]
            
        if index in self._document_presenters:
            del self._document_presenters[index]
    
    def get_active_document_presenter(self, active_tab_index: int) -> Optional[DocumentPresenter]:
        """
        Get the active document presenter.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            Optional[DocumentPresenter]: The active document presenter, or None if not found
        """
        return self._document_presenters.get(active_tab_index)
        
    def get_active_document_view(self, active_tab_index: int) -> Optional[DocumentListView]:
        """
        Get the active document view.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            Optional[DocumentListView]: The active document view, or None if not found
        """
        return self._document_views.get(active_tab_index)
    
    # Helper methods for handling view signals
    def _handle_insert_requested(self, index: int):
        """
        Handle insert request from a view.
        
        Args:
            index: The tab index of the view
        """
        document_presenter = self.get_active_document_presenter(index)
        document_view = self.get_active_document_view(index)
        
        if document_presenter and document_view:
            selected_index = document_view.get_selected_index()
            # Use -1 to add at the end if no selection
            document_presenter.add_line("", selected_index if selected_index >= 0 else -1)
            
    def _handle_edit_requested(self, index: int):
        """
        Handle edit request from a view.
        
        Args:
            index: The tab index of the view
        """
        # This would be connected to an edit dialog or panel
        # For now, this is a placeholder
        pass
            
    def _handle_delete_requested(self, index: int):
        """
        Handle delete request from a view.
        
        Args:
            index: The tab index of the view
        """
        document_presenter = self.get_active_document_presenter(index)
        document_view = self.get_active_document_view(index)
        
        if document_presenter and document_view:
            selected_index = document_view.get_selected_index()
            if selected_index >= 0:
                document_presenter.remove_line(selected_index)

    
    # Undo/Redo actions
    @pyqtSlot()
    def undo(self, active_tab_index: int) -> bool:
        """
        Undo the last action in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if an action was undone, False otherwise
        """
        document_presenter = self.get_active_document_presenter(active_tab_index)
        
        if document_presenter and document_presenter.undo():
            self.actionCompleted.emit("Undo")
            return True
        else:
            self.actionFailed.emit("Nothing to undo")
            return False
    
    @pyqtSlot()
    def redo(self, active_tab_index: int) -> bool:
        """
        Redo the last undone action in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if an action was redone, False otherwise
        """
        document_presenter = self.get_active_document_presenter(active_tab_index)
        
        if document_presenter and document_presenter.redo():
            self.actionCompleted.emit("Redo")
            return True
        else:
            self.actionFailed.emit("Nothing to redo")
            return False
    
    # Line movement actions
    @pyqtSlot()
    def move_line_up(self, active_tab_index: int) -> bool:
        """
        Move the selected line up in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if the line was moved up, False otherwise
        """
        document_presenter = self.get_active_document_presenter(active_tab_index)
        document_view = self.get_active_document_view(active_tab_index)
        
        if not document_presenter or not document_view:
            self.actionFailed.emit("No active document")
            return False
            
        selected_index = document_view.get_selected_index()
        if selected_index < 0:
            self.actionFailed.emit("No line selected")
            return False
            
        if document_presenter.move_line_up(selected_index):
            self.actionCompleted.emit("Moved line up")
            return True
        else:
            self.actionFailed.emit("Cannot move line up")
            return False
    
    @pyqtSlot()
    def move_line_down(self, active_tab_index: int) -> bool:
        """
        Move the selected line down in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if the line was moved down, False otherwise
        """
        document_presenter = self.get_active_document_presenter(active_tab_index)
        document_view = self.get_active_document_view(active_tab_index)
        
        if not document_presenter or not document_view:
            self.actionFailed.emit("No active document")
            return False
            
        selected_index = document_view.get_selected_index()
        if selected_index < 0:
            self.actionFailed.emit("No line selected")
            return False
            
        if document_presenter.move_line_down(selected_index):
            self.actionCompleted.emit("Moved line down")
            return True
        else:
            self.actionFailed.emit("Cannot move line down")
            return False
    
    # Line editing actions
    @pyqtSlot()
    def insert_line(self, active_tab_index: int) -> bool:
        """
        Insert a new line in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if a line was inserted, False otherwise
        """
        document_view = self.get_active_document_view(active_tab_index)
        
        if document_view:
            # The actual insertion is handled by the document view's insert dialog
            document_view.insertRequested.emit()
            return True
        else:
            self.actionFailed.emit("No active document")
            return False
    
    @pyqtSlot()
    def edit_line(self, active_tab_index: int) -> bool:
        """
        Edit the selected line in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if a line was edited, False otherwise
        """
        document_view = self.get_active_document_view(active_tab_index)
        
        if document_view:
            # The actual editing is handled by the document view's edit dialog
            document_view.editRequested.emit()
            return True
        else:
            self.actionFailed.emit("No active document")
            return False
    
    @pyqtSlot()
    def delete_line(self, active_tab_index: int) -> bool:
        """
        Delete the selected line in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if a line was deleted, False otherwise
        """
        document_view = self.get_active_document_view(active_tab_index)
        
        if document_view:
            # The actual deletion is handled by the document view's delete functionality
            document_view.deleteRequested.emit()
            return True
        else:
            self.actionFailed.emit("No active document")
            return False
    
    @pyqtSlot()
    def toggle_comment(self, active_tab_index: int) -> bool:
        """
        Toggle comment on the selected line in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if the comment was toggled, False otherwise
        """
        document_presenter = self.get_active_document_presenter(active_tab_index)
        document_view = self.get_active_document_view(active_tab_index)
        
        if not document_presenter or not document_view:
            self.actionFailed.emit("No active document")
            return False
            
        selected_index = document_view.get_selected_index()
        if selected_index < 0:
            self.actionFailed.emit("No line selected")
            return False
            
        if document_presenter.toggle_comment(selected_index):
            self.actionCompleted.emit("Toggled comment")
            return True
        else:
            self.actionFailed.emit("Cannot toggle comment")
            return False
    
    @pyqtSlot()
    def duplicate_line(self, active_tab_index: int) -> bool:
        """
        Duplicate the selected line in the active document.
        
        Args:
            active_tab_index: The index of the active tab
            
        Returns:
            bool: True if the line was duplicated, False otherwise
        """
        document_presenter = self.get_active_document_presenter(active_tab_index)
        document_view = self.get_active_document_view(active_tab_index)
        
        if not document_presenter or not document_view:
            self.actionFailed.emit("No active document")
            return False
            
        selected_index = document_view.get_selected_index()
        if selected_index < 0:
            self.actionFailed.emit("No line selected")
            return False
            
        if document_presenter.duplicate_line(selected_index):
            self.actionCompleted.emit("Duplicated line")
            return True
        else:
            self.actionFailed.emit("Cannot duplicate line")
            return False