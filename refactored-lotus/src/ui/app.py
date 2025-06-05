from PyQt5.QtWidgets import QApplication
import sys

from src.ui.views.MainView import MainView
from src.presenters.ApplicationPresenter import ApplicationPresenter
from src.core.services.ThemeService import ThemeService
from src.core.models.DocumentModelFactory import DocumentModelFactory
from src.core.models.LineModelFactory import LineModelRegistry
from src.core.models.BasicLineModelFactory import BasicLineModelFactory
from src.core.models.AfLineModelFactory import AfLineModelFactory
from src.core.services.ServiceLocator import ServiceLocator
from src.core.services.FileService import FileService
from src.core.services.ConfigService import ConfigService
from src.core.services.PatternMatchingService import PatternMatchingService
from src.core.services.PatternMatcher import PatternMatcher
from src.ui.managers.MenuManager import MenuManager
from src.ui.managers.ActionManager import ActionManager

from fly.fly_netlist import FlyNetlistBuilder


class LotusApplication:
    """
    Main application class for Lotus.
    
    This class initializes the application components and starts the application.
    """
    
    def __init__(self):
        """Initialize the application."""
        self._app = QApplication(sys.argv)
        
        # Create services
        self._config_service = ConfigService()
        self._file_service = FileService(self._config_service)
        self._theme_service = ThemeService(self._config_service, self._file_service)
        self._fly_netlist_builder = FlyNetlistBuilder()
        self._pattern_matching_service = PatternMatchingService(
            PatternMatcher(self._config_service, self._fly_netlist_builder))
        ServiceLocator.register('config_service', self._config_service)
        ServiceLocator.register('file_service', self._file_service)
        ServiceLocator.register('theme_service', self._theme_service)
        ServiceLocator.register('pattern_matching_service', self._pattern_matching_service)
        ServiceLocator.register('fly_netlist_builder', self._fly_netlist_builder)


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
    if len(sys.argv) > 1:
        app.load_document(app._config_service.get_file_path("af_file"), "af")
    
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
