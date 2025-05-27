from PyQt5.QtWidgets import QApplication
import sys

from src.ui.views.MainView import MainView
from src.ui.presenters.ApplicationPresenter import ApplicationPresenter
from src.core.services.ThemeService import ThemeService
from src.core.models.DocumentModelFactory import DocumentModelFactory
from src.core.models.LineModelFactory import LineModelRegistry
from src.core.models.BasicLineModelFactory import BasicLineModelFactory
from src.core.models.AfLineModelFactory import AfLineModelFactory


class LotusApplication:
    """
    Main application class for Lotus.
    
    This class initializes the application components and starts the application.
    """
    
    def __init__(self):
        """Initialize the application."""
        self._app = QApplication(sys.argv)
        
        # Create services
        self._theme_service = ThemeService()
        
        # Set up model factories
        self._line_model_registry = LineModelRegistry()
        self._line_model_registry.register_factory('text', BasicLineModelFactory())
        self._line_model_registry.register_factory('af', AfLineModelFactory())
        
        self._document_model_factory = DocumentModelFactory(self._line_model_registry)
        
        # Create main view
        self._main_view = MainView(self._theme_service)
        
        # Create application presenter
        self._application_presenter = ApplicationPresenter(
            self._main_view, 
            self._document_model_factory,
            self._theme_service
        )
        
        # Connect exit signal
        self._application_presenter.applicationExit.connect(self._app.quit)
    
    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            int: Application exit code
        """
        self._main_view.show()
        return self._app.exec_()
    
    def load_document(self, file_path: str, file_type: str = None) -> bool:
        """
        Load a document.
        
        Args:
            file_path: Path to the document
            file_type: Type of the document
            
        Returns:
            bool: True if the document was loaded successfully
        """
        return self._application_presenter.load_document(file_path, file_type)


def main():
    """Application entry point."""
    app = LotusApplication()
    
    # Process command line arguments here if needed
    # For demonstration, we could load a document
    # import os
    # if len(sys.argv) > 1:
    #     app.load_document(sys.argv[1])
    
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
