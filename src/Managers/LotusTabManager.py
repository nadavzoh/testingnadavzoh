from PyQt5.QtCore import QObject, pyqtSignal
from src.Factories.TabFactory import TabFactory


class LotusTabManager(QObject):
    """
    Manager class to handle tab operations and coordination between different tabs.
    It uses TabFactory to create tabs and manages their lifecycle.
    """
    tabChanged = pyqtSignal(int)

    def __init__(self, ui_manager, files_manager):
        """
        Initialize the tab manager with UI manager and files manager.

        Args:
            ui_manager: The UI manager to handle UI updates
            files_manager: The files manager to get file paths
        """
        super().__init__()
        self.ui_manager = ui_manager
        self.files_manager = files_manager

        # Container for all tabs
        self.tabs = []
        self.active_tab_index = 0

        # Connect signals
        self.ui_manager.tabChanged.connect(self.on_tab_changed)

    def initialize_tabs(self):
        """Initialize default tabs based on files from the files manager"""
        self.add_tab("af",
                     self.files_manager.get_af_dcfg_file(),
                     self.files_manager.get_spice_file())

        # TODO: ENABLE MUTEX TAB
        # self.add_tab("mutex",
        #              self.files_manager.get_mutex_dcfg_file(),
        #              self.files_manager.get_spice_file())

        # Set first tab as active if tabs exist
        if self.tabs:
            self.set_active_tab(0)
            self.ui_manager.update_header_filepath(self.tabs[0]['config_file'])

    def add_tab(self, tab_type, config_file, spice_file):
        """
        Add a new tab of the specified type.

        Args:
            tab_type (str): Type of tab to add (e.g., "af", "mutex")
            config_file (str): Path to the configuration file
            spice_file (str): Path to the spice file

        Returns:
            int: Index of the newly added tab
        """
        # Create tab components using factory
        tab = TabFactory.create_tab(tab_type, config_file, spice_file)

        # Add views to UI
        doc_view = tab['document']['view']
        dialog_view = tab['dialog']['view']
        title = tab['title']

        # Add to UI manager and get indexes
        doc_tab_index = self.ui_manager.add_tab_to_left_panel(doc_view, title)
        dialog_panel_index = self.ui_manager.add_right_panel_content(dialog_view)

        # Store tab data with UI indexes
        tab['doc_tab_index'] = doc_tab_index
        tab['dialog_panel_index'] = dialog_panel_index
        tab['config_file'] = config_file

        # Add tab to managed list
        self.tabs.append(tab)

        # Connect signals from dialog controller
        dialog_controller = tab['dialog']['controller']
        dialog_controller.dialog_accepted.connect(self.ui_manager.enable_buttons)
        dialog_controller.dialog_cancelled.connect(self.ui_manager.enable_buttons)

        # Return the tab index
        return len(self.tabs) - 1

    def on_tab_changed(self, index):
        """Handle tab changed event from UI"""
        if 0 <= index < len(self.tabs):
            self.active_tab_index = index
            self.set_active_tab(index)

    def set_active_tab(self, index):
        """Set the active tab by index"""
        if 0 <= index < len(self.tabs):
            self.active_tab_index = index
            tab = self.tabs[index]

            # Update UI to show the right dialog panel
            self.ui_manager.set_right_panel_current_index(tab['dialog_panel_index'])

            # Update filepath in header
            if 'config_file' in tab:
                self.ui_manager.update_header_filepath(tab['config_file'])

    def get_active_controller(self):
        """Get the document controller for the active tab"""
        if 0 <= self.active_tab_index < len(self.tabs):
            return self.tabs[self.active_tab_index]['document']['controller']
        return None

    def get_controllers(self):
        """Get all document controllers"""
        return [tab['document']['controller'] for tab in self.tabs]