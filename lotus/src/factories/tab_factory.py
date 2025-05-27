from controllers.af_dialog_controller import AfDialogController
from controllers.document_controller import DocumentController
from controllers.mutex_dialog_controller import MutexDialogController
from models.af_dialog_model import AfDialogModel
from models.document_model import DocumentModel
from models.mutex_dialog_model import MutexDialogModel
from views.af_dialog_view import AfDialogView
from views.document_list_view import DocumentListView
from views.mutex_dialog_view import MutexDialogView


class TabFactory:
    """
    Factory class for creating tab components.
    This class is responsible for creating the model, view, and controller components
    for different types of tabs in the application.
    It provides a static method `create_tab` that takes a tab type and returns a dictionary
    containing the instantiated model, view, and controller for both the document and dialog
    associated with that tab type.

    The factory pattern used here makes it easy to extend the application with new tab types
    while maintaining a consistent creation process for all tabs.

    [FOR DEVELOPERS]
    To create a new tab, implement its corresponding model, view, and controller classes,
    and then add a new condition in the create_tab method.
    Don't forget to also update lotus_tab_manager.py to handle the new tab type.
    """

    @staticmethod
    def create_tab(tab_type, config_file=None, spice_file=None):
        """
        Create a complete tab with model, view, and controllers for both document and dialog.

        This method instantiates all necessary components for a specific tab type,
        configures their relationships, and returns them as a structured dictionary.

        Args:
            tab_type (str): Type of tab to create (e.g., "af", "mutex")
            config_file (str, optional): Path to the configuration file. Defaults to None.
            spice_file (str, optional): Path to the spice file. Defaults to None.

        Returns:
            dict: Dictionary with the following structure:
                {
                    'document': {
                        'model': DocumentModel instance,
                        'view': DocumentListView instance,
                        'controller': DocumentController instance
                    },
                    'dialog': {
                        'model': DialogModel instance for the specific tab type,
                        'view': DialogView instance for the specific tab type,
                        'controller': DialogController instance for the specific tab type
                    },
                    'title': Tab title string
                }

        Raises:
            ValueError: If the specified tab type is not supported
        """
        # Common document components used by all tab types
        doc_model = DocumentModel(config_file, spice_file)
        doc_view = DocumentListView()
        doc_controller = DocumentController(doc_model, doc_view)

        # Create tab-specific dialog components based on tab_type
        if tab_type.lower() == "af":
            dialog_model = AfDialogModel()
            dialog_view = AfDialogView()
            dialog_controller = AfDialogController(dialog_model, dialog_view)

        elif tab_type.lower() == "mutex":
            dialog_model = MutexDialogModel(['foo', 'bar', 'test', 'net', 'template'])
            dialog_view = MutexDialogView()
            dialog_controller = MutexDialogController(dialog_model, dialog_view)

        else:
            raise ValueError(f"Unknown tab type: {tab_type}")

        # Link document and dialog controllers
        doc_controller.set_dialog_controller(dialog_controller)

        return {
            'document': {
                'model': doc_model,
                'view': doc_view,
                'controller': doc_controller
            },
            'dialog': {
                'model': dialog_model,
                'view': dialog_view,
                'controller': dialog_controller
            },
            'title': tab_type.upper()
        }