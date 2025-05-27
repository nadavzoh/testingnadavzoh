from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QMenu, QMenuBar
from services.lotus_config import LotusConfig


class LotusMenuManager:
    """
    Manages the application menu bar and its menus.
    
    This class is responsible for creating and configuring the menu bar
    for the Lotus application. It provides a modular approach to adding
    menus and actions with their respective icons, shortcuts, and signals.
    """
    
    def __init__(self, main_window, ui_manager):
        """
        Initialize the menu manager with the main window and UI manager.
        
        Args:
            main_window (QMainWindow): The main window to which the menu bar will be attached
            ui_manager (LotusUIManager): The UI manager for connecting signals
        """
        self._main_window = main_window
        self._ui_manager = ui_manager
        self._menu_bar = main_window.menuBar()
        self._menus = {}
        self._actions = {}
        self.setup_menus()
        # Store menus for later reference if needed
        
    def setup_menus(self):
        """
        Set up all application menus and their actions.
        
        Creates the standard menu structure for the application:
        - File menu: Exit, Save All
        - Edit menu: Undo, Redo
        - View menu: Toggle Theme
        - Help menu: Shortcuts, About
        
        Returns:
            QMenuBar: The configured menu bar
        """
        # File Menu
        file_menu = self._add_menu("&File")
        self._add_action(file_menu, "&Save", "SAVE", QKeySequence.Save,
                         self._ui_manager.saveRequested.emit)
        self._add_action(file_menu, "Save &As", "SAVE", QKeySequence("Ctrl+Alt+S"),
                         self._ui_manager.saveAsRequested.emit)
        self._add_action(file_menu, "Save &All", "SAVE", QKeySequence("Ctrl+Shift+S"),
                         self._ui_manager.saveAllRequested.emit)
        file_menu.addSeparator()
        self._add_action(file_menu, "E&xit", "CANCEL", QKeySequence.Quit, 
                         self._ui_manager.exitRequested.emit)
        
        # Edit Menu
        edit_menu = self._add_menu("&Edit")
        self._add_action(edit_menu, "&Undo", "UNDO", QKeySequence.Undo, 
                         self._ui_manager.undoRequested.emit)
        self._add_action(edit_menu, "&Redo", "REDO", QKeySequence.Redo, 
                         self._ui_manager.redoRequested.emit)
        
        # View Menu
        view_menu = self._add_menu("&View")
        self._add_action(view_menu, "Toggle &Theme", "TOGGLE_THEME", QKeySequence("Ctrl+Shift+T"),
                         self._ui_manager.toggleThemeRequested.emit)
        view_menu.addSeparator()
        self._add_action(view_menu, "Increase &Font Size", None, QKeySequence("Ctrl+="),
                         self._ui_manager.increaseFontSizeRequested.emit)
        self._add_action(view_menu, "Decrease &Font Size", None, QKeySequence("Ctrl+-"),
                         self._ui_manager.decreaseFontSizeRequested.emit)
        self._add_action(view_menu, "Reset &Font Size", None, QKeySequence("Ctrl+0"),
                         self._ui_manager.resetFontSizeRequested.emit)
        
        # Help Menu
        help_menu = self._add_menu("&Help")
        self._add_action(help_menu, "&Shortcuts", None, QKeySequence("Ctrl+H"), 
                         self._ui_manager.show_shortcuts)
        help_menu.addSeparator()
        
        return self._menu_bar
    
    def _add_menu(self, title):
        """
        Add a new menu to the menu bar.
        
        Args:
            title (str): The title of the menu
            
        Returns:
            QMenu: The newly created menu
        """
        menu = self._menu_bar.addMenu(title)
        self._menus[title] = menu
        return menu
    
    def _add_action(self, menu, title, icon_key=None, shortcut=None, slot=None):
        """
        Add an action to a menu.
        
        Args:
            menu (QMenu): The menu to which the action will be added
            title (str): The title of the action
            icon_key (str, optional): The key for the icon in LotusConfig
            shortcut (QKeySequence, optional): The keyboard shortcut
            slot (function, optional): The function to be called when action is triggered
            
        Returns:
            QAction: The newly created action
        """
        action = QAction(title, self._main_window)
        
        if icon_key:
            action.setIcon(LotusConfig.get_icon(icon_key))
        
        if shortcut:
            action.setShortcut(shortcut)
        
        if slot:
            action.triggered.connect(slot)
        
        menu.addAction(action)
        self._actions[title] = action
        return action
    
    def get_menu(self, title):
        """
        Get a menu by its title.
        
        Args:
            title (str): The title of the menu
            
        Returns:
            QMenu: The requested menu or None if not found
        """
        return self._menus.get(title)
    
    def get_action(self, title):
        """
        Get an action by its title.
        
        Args:
            title (str): The title of the action
            
        Returns:
            QAction: The requested action or None if not found
        """
        return self._actions.get(title)