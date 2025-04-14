from src.Controllers.AfDialogController import AfDialogController
from src.Controllers.DocumentController import DocumentController
from src.Controllers.MutexDialogController import MutexDialogController
from src.Models.AfDialogModel import AfDialogModel
from src.Models.DocumentModel import DocumentModel
from src.Models.MutexDialogModel import MutexDialogModel
from src.Views.AfDialogView import AfDialogView
from src.Views.DocumentListView import DocumentListView
from src.Views.MutexDialogView import MutexDialogView


class TabFactory:
    """
    Factory class to create tab components (model, view, controller) for different tab types.
    This centralizes tab creation logic and makes it easy to add new tab types.
    """

    @staticmethod
    def create_tab(tab_type, config_file=None, spice_file=None):
        """
        Create a complete tab with model, view, and controllers for both document and dialog.

        Args:
            tab_type (str): Type of tab to create (e.g., "af", "mutex")
            config_file (str): Path to the configuration file
            spice_file (str): Path to the spice file

        Returns:
            dict: Dictionary with document and dialog components
        """
        if tab_type.lower() == "af":
            # Create AF (Activity Factor) tab components
            doc_model = DocumentModel(config_file, spice_file)
            doc_view = DocumentListView()
            doc_controller = DocumentController(doc_model, doc_view)

            dialog_model = AfDialogModel()
            dialog_view = AfDialogView()
            dialog_controller = AfDialogController(dialog_model, dialog_view)

        elif tab_type.lower() == "mutex":
            # Create Mutex tab components
            doc_model = DocumentModel(config_file, spice_file)
            doc_view = DocumentListView()
            doc_controller = DocumentController(doc_model, doc_view)

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
            'title': tab_type.upper()  # Tab title
        }