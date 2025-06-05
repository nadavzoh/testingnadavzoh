from typing import List, Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from src.ui.views.MainView import MainView
from src.ui.views.DocumentListView import DocumentListView
from src.presenters.DocumentPresenter import DocumentPresenter
from src.core.services.ThemeService import ThemeService
from src.core.models.DocumentModel import DocumentModel
from src.core.models.DocumentModelFactory import DocumentModelFactory
from src.core.models.LineModelFactory import LineModelRegistry
from src.ui.managers.ActionManager import ActionManager


class ApplicationPresenter(QObject):
    """
    Main application presenter.
    
    This presenter coordinates between the main view and document presenters,
    managing the overall application state and user interactions.
    
    Signals:
        applicationExit: Emitted when the application is about to exit
    """
    
    # Signals
    applicationExit = pyqtSignal()
    
    def __init__(self, main_view: MainView, document_model_factory: DocumentModelFactory, 
                 theme_service: ThemeService):
        """
        Initialize the application presenter.
        
        Args:
            main_view: The main application view
            document_model_factory: Factory for creating document models
            theme_service: Service for theme colors
        """
        super().__init__()
        self._main_view = main_view
        self._document_model_factory = document_model_factory
        self._theme_service = theme_service
        
        # Create action manager
        self._action_manager = ActionManager()
        
        # Store document presenters by tab index
        self._document_presenters = {}
        
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect view signals to presenter methods."""
        # Connect main view signals
        self._main_view.documentTabChanged.connect(self._on_tab_changed)
        self._main_view.exitRequested.connect(self._on_exit_requested)
        
        # Connect document action signals
        self._main_view.undoRequested.connect(self._on_undo_requested)
        self._main_view.redoRequested.connect(self._on_redo_requested)
        self._main_view.moveLineUpRequested.connect(self._on_move_line_up_requested)
        self._main_view.moveLineDownRequested.connect(self._on_move_line_down_requested)
        self._main_view.insertLineRequested.connect(self._on_insert_line_requested)
        self._main_view.editLineRequested.connect(self._on_edit_line_requested)
        self._main_view.deleteLineRequested.connect(self._on_delete_line_requested)
        self._main_view.toggleCommentRequested.connect(self._on_toggle_comment_requested)
        self._main_view.duplicateLineRequested.connect(self._on_duplicate_line_requested)
        
        # Connect action manager signals
        self._action_manager.actionCompleted.connect(self._on_action_completed)
        self._action_manager.actionFailed.connect(self._on_action_failed)
    
    # Tab management handlers
    def _on_tab_changed(self, index: int):
        """
        Handle tab change.
        
        Args:
            index: The index of the new tab
        """
        # The tab has been changed, but the ActionManager already has the document registered
        # So no additional action is needed here
        pass
    
    def _on_exit_requested(self):
        """Handle exit request."""
        # Check for unsaved changes
        unsaved_changes = False
        for presenter in self._document_presenters.values():
            if presenter.has_unsaved_changes():
                unsaved_changes = True
                break
        
        if unsaved_changes:
            reply = QMessageBox.question(
                self._main_view,
                "Unsaved Changes",
                "There are unsaved changes. Do you want to exit anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # Emit exit signal
        self.applicationExit.emit()
    
    # Action result handlers
    def _on_action_completed(self, message: str):
        """
        Handle action completed.
        
        Args:
            message: The success message
        """
        # Update status bar (not implemented yet)
        pass
    
    def _on_action_failed(self, message: str):
        """
        Handle action failed.
        
        Args:
            message: The error message
        """
        # Show error message
        QMessageBox.warning(self._main_view, "Action Failed", message)
    
    # Document action handlers
    def _on_undo_requested(self):
        """Handle undo request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.undo(current_index)
    
    def _on_redo_requested(self):
        """Handle redo request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.redo(current_index)
    
    def _on_move_line_up_requested(self):
        """Handle move line up request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.move_line_up(current_index)
    
    def _on_move_line_down_requested(self):
        """Handle move line down request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.move_line_down(current_index)
    
    def _on_insert_line_requested(self):
        """Handle insert line request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.insert_line(current_index)
    
    def _on_edit_line_requested(self):
        """Handle edit line request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.edit_line(current_index)
    
    def _on_delete_line_requested(self):
        """Handle delete line request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.delete_line(current_index)
    
    def _on_toggle_comment_requested(self):
        """Handle toggle comment request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.toggle_comment(current_index)
    
    def _on_duplicate_line_requested(self):
        """Handle duplicate line request."""
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            self._action_manager.duplicate_line(current_index)
        
        for presenter in self._document_presenters.values():
            if presenter.has_unsaved_changes():
                unsaved_changes = True
                break
        
        if unsaved_changes:
            reply = QMessageBox.question(
                self._main_view,
                "Unsaved Changes",
                "There are unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                # Save all documents
                self._save_all_documents()
                self.applicationExit.emit()
            elif reply == QMessageBox.Discard:
                self.applicationExit.emit()
            # If Cancel, do nothing
        else:
            # No unsaved changes, exit
            self.applicationExit.emit()
    
    def _save_all_documents(self):
        """Save all documents with unsaved changes."""
        for presenter in self._document_presenters.values():
            if presenter.has_unsaved_changes():
                presenter.save_document()
    
    def _connect_document_view_signals(self, document_view: DocumentListView, 
                                     document_presenter: DocumentPresenter):
        """
        Connect signals between a document view and its presenter.
        
        Args:
            document_view: The document view
            document_presenter: The document presenter
        """
        # Connect view signals to presenter
        document_view.lineSelected.connect(document_presenter.handle_line_selection)
        
        # Connect presenter signals to view that aren't already connected in ActionManager
        document_presenter.lineUpdated.connect(
            lambda index: document_view.set_selected_index(index))
        document_presenter.documentLoaded.connect(
            lambda path: self._main_view.set_status_message(f"Loaded: {path}"))
        document_presenter.documentSaved.connect(
            lambda path: self._main_view.set_status_message(f"Saved: {path}"))
    
    def _on_insert_requested(self, presenter: DocumentPresenter):
        """
        Handle insert request.
        
        Args:
            presenter: The document presenter
        """
        document_view = self._main_view.get_current_document_view()
        if document_view:
            index = document_view.get_selected_index()
            # Insert empty line at selected index or at the end
            presenter.add_line("", index if index >= 0 else -1)
    
    def _on_edit_requested(self, presenter: DocumentPresenter):
        """
        Handle edit request.
        
        Args:
            presenter: The document presenter
        """
        # This would be connected to the right panel for editing
        # For now, we'll leave it empty as requested
        pass
    
    def _on_delete_requested(self, presenter: DocumentPresenter):
        """
        Handle delete request.
        
        Args:
            presenter: The document presenter
        """
        document_view = self._main_view.get_current_document_view()
        if document_view:
            index = document_view.get_selected_index()
            if index >= 0:
                presenter.remove_line(index)
    
    def load_document(self, file_path: str, file_type: Optional[str] = None) -> bool:
        """
        Load a document into a new tab.
        
        Args:
            file_path: Path to the document file
            file_type: Type of the file (e.g., 'af', 'mutex')
            
        Returns:
            bool: True if the document was loaded successfully
        """
        # Create document model based on file type
        document_model = self._document_model_factory.create_document_model(file_type)
        
        # Create document presenter
        document_presenter = DocumentPresenter(document_model)
        
        # Load the document
        if not document_presenter.load_document(file_path):
            return False
        
        # Create document view
        document_view = DocumentListView(self._theme_service)
        
        # Set view model from presenter
        document_view.set_model(document_presenter.get_list_model())
        
        # Get file name for tab title
        import os
        file_name = os.path.basename(file_path)
        
        # Add tab and store presenter
        tab_index = self._main_view.add_document_tab(file_name, document_view)
        self._document_presenters[tab_index] = document_presenter
        
        # Register document with action manager
        self._action_manager.register_document(tab_index, document_view, document_presenter)
        
        # Connect signals
        self._connect_document_view_signals(document_view, document_presenter)
        
        # Select the new tab
        self._main_view.set_current_tab(tab_index)
        
        return True
    
    def get_current_document_presenter(self) -> Optional[DocumentPresenter]:
        """
        Get the presenter for the current document.
        
        Returns:
            Optional[DocumentPresenter]: The current document presenter,
                                        or None if no document is open
        """
        current_index = self._main_view.get_current_tab_index()
        if current_index >= 0:
            return self._document_presenters.get(current_index)
        return None
