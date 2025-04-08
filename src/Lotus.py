from PyQt5.QtWidgets import (QMainWindow, QMessageBox)

from src.Controllers.AfDialogController import AfDialogController
from src.Controllers.MutexDialogController import MutexDialogController
from src.Controllers.DocumentController import DocumentController
from src.Managers.LotusFilesManager import LotusFilesManager
from src.Managers.LotusThemeManager import LotusThemeManager
from src.Managers.LotusUIManager import LotusUIManager
from src.Models.AfDialogModel import AfDialogModel
from src.Models.MutexDialogModel import MutexDialogModel
from src.Models.DocumentModel import DocumentModel
from src.Services.LotusConfig import LotusConfig
from src.Views.BaseDialogView import BaseDialogView
from src.Views.DocumentListView import DocumentListView


class Lotus(QMainWindow):
     def __init__(self):
         super().__init__()
         # File paths from command line
         # Initialize managers
         #TODO : 1. FileManager - currently reading spice file multiple times..
         #       2. TabManager ? this will probably be the main coordinator..
         self._files_manager = LotusFilesManager()
         self._fub = self._files_manager.get_fub()
         self._spice_file = self._files_manager.get_spice_file()
         self._af_dcfg_file = self._files_manager.get_af_dcfg_file()
         self._mutex_file = self._files_manager.get_mutex_dcfg_file()
         self._theme_manager = LotusThemeManager()
         self._ui_manager = LotusUIManager(self)
         self.controllers = []
         # Setup UI and MVC
         self._setup_ui()
         self._setup_mvc()
         self._connect_signals()

     def _setup_ui(self):
         # Setup main window properties
         self._ui_manager.setup_main_window(
             self.__class__.__name__,
             LotusConfig.get_icon("LOTUS"),
             (100, 100, 1400, 800)
         )
         # Create main layout with panels
         self._ui_manager.create_main_layout(self._af_dcfg_file, self._mutex_file)

     def _setup_mvc(self):
         ############### Right panel ###############
         # AF Dialog
         self.af_dialog_model = AfDialogModel()
         self.af_dialog_view = BaseDialogView()
         self.af_dialog_controller = AfDialogController(self.af_dialog_model, self.af_dialog_view)
         # Mutex Dialog - placeholder for now, will change model and controller later
         # self.mutex_dialog_model = AfDialogModel()
         # self.mutex_dialog_view = BaseDialogView(tab_type="mutex")  # Replace with actual view
         # self.mutex_dialog_controller = AfDialogController(self.mutex_dialog_model, self.mutex_dialog_view)
         self.mutex_diaog_model = MutexDialogModel(['foo', 'bar', 'test', 'net', 'template'])
         self.mutex_dialog_view = BaseDialogView(tab_type="mutex")
         self.mutex_dialog_controller = MutexDialogController(self.mutex_diaog_model, self.mutex_dialog_view)

         # Add content to right panel
         self._ui_manager.add_right_panel_content(self.af_dialog_view)
         self._ui_manager.add_right_panel_content(self.mutex_dialog_view)
         ############### Left panel ###############
         # Activity Factor Tab
         self._af_doc_model = DocumentModel(self._af_dcfg_file, self._spice_file)
         self._af_doc_view = DocumentListView()
         self._af_doc_controller = DocumentController(
             self._af_doc_model,
             self._af_doc_view
         )
         self._af_doc_controller.set_dialog_controller(self.af_dialog_controller)
         self.controllers.append(self._af_doc_controller)
         self._ui_manager.add_tab(self._af_doc_view, "AF")
         # Mutex Tab
         self._mutex_doc_model = DocumentModel(self._mutex_file, self._spice_file)
         self._mutex_doc_view = DocumentListView()
         self._mutex_doc_controller = DocumentController(
             self._mutex_doc_model,
             self._mutex_doc_view
         )
         # self._mutex_doc_controller.set_dialog_controller(self.mutex_dialog_controller)
         self.controllers.append(self._mutex_doc_controller)
         self._ui_manager.add_tab(self._mutex_doc_view, "Mutex")


     def _connect_signals(self):
         # Connect UI manager signals to handlers
         self._ui_manager.insertRequested.connect(self._on_insert_new_requested)
         self._ui_manager.editRequested.connect(self._on_edit_requested)
         self._ui_manager.deleteRequested.connect(self._delete_selected_line)
         self._ui_manager.undoRequested.connect(self._undo_last_action)
         self._ui_manager.redoRequested.connect(self._redo_last_action)
         self._ui_manager.saveRequested.connect(self._save_changes)
         self._ui_manager.exitRequested.connect(self.close)
         self._ui_manager.saveAllRequested.connect(self._on_save_all)
         self._ui_manager.toggleThemeRequested.connect(self._theme_manager.toggle_theme)
         self._ui_manager.tabChanged.connect(self._on_tab_change)

         self.af_dialog_controller.dialog_accepted.connect(self._ui_manager.enable_buttons)
         self.af_dialog_controller.dialog_cancelled.connect(self._ui_manager.enable_buttons)

         # kinda ugly way but current workaround - to be refactored
         # ideally - create the TabManager to handle all these kind of stuff.
         # self.mutex_dialog_controller.dialog_accepted.connect(self._ui_manager.enable_buttons)
         # self.mutex_dialog_controller.dialog_cancelled.connect(self._ui_manager.enable_buttons)

         # Connect UI manager's internal signals
         self._ui_manager.connect_signals()

     def _on_tab_change(self, index):
         # Update right panel based on selected tab
         self._ui_manager.set_right_panel_current_index(index)

         # Update header filepath
         if index == 0:
             self._ui_manager.update_header_filepath(self._af_dcfg_file)
         elif index == 1:
             self._ui_manager.update_header_filepath(self._mutex_file)

     def _get_active_controller(self):
         """Get the controller for the currently active tab."""
         current_index = self._ui_manager.get_current_tab_index()
         if current_index == 0:
             return self._af_doc_controller
         elif current_index == 1:
             return self._mutex_doc_controller
         return None

     # Action methods remain the same but use UI manager for messages
     def _on_insert_new_requested(self):
         controller = self._get_active_controller()
         if controller:
             success = controller.insert_line("")
             if not success:
                 self._ui_manager.show_warning_message("Insert Line", "No line selected to insert after.")

     def _on_edit_requested(self):
         self._ui_manager.disable_buttons()
         # Maybe we want to disable only the current tab's buttons.
         controller = self._get_active_controller()
         if controller:
             controller.enter_edit_mode()

     def _delete_selected_line(self):
         controller = self._get_active_controller()
         if controller:
             controller.delete_line()

     def _undo_last_action(self):
         controller = self._get_active_controller()
         if controller:
             success = controller.undo_action()
             if not success:
                 self._ui_manager.show_info_message("Undo", "Nothing to undo.")

     def _redo_last_action(self):
         controller = self._get_active_controller()
         if controller:
             success = controller.redo_action()
             if not success:
                 self._ui_manager.show_info_message("Redo", "Nothing to redo.")

     def _save_changes(self):
         controller = self._get_active_controller()
         if controller:
             success = controller.save_changes()
             if success:
                 self._ui_manager.show_info_message("Save", "Changes saved successfully.")
             else:
                 self._ui_manager.show_warning_message("Save", "Failed to save changes.")

     def _on_save_all(self):
         for controller in self.controllers:
                if controller.has_unsaved_changes():
                    success = controller.save_changes()
                    if not success:
                        self._ui_manager.show_warning_message("Save All", "Failed to save all changes.")
                        return
         self._ui_manager.show_info_message("Save All", "All changes saved successfully.")

     def closeEvent(self, event):
         has_changes = self._af_doc_controller.has_unsaved_changes()
         # or self._mutex_doc_controller.has_unsaved_changes())

         if has_changes:
             reply = self._ui_manager.show_question_message(
                 "Unsaved Changes",
                 "You have unsaved changes. Do you want to save before quitting?",
                 QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
             )

             if reply == QMessageBox.Save:
                 self._af_doc_controller.save_changes()
                 # self._mutex_doc_controller.save_changes()
                 event.accept()
             elif reply == QMessageBox.Cancel:
                 event.ignore()
             else:  # Discard
                 event.accept()
         else:
             event.accept()