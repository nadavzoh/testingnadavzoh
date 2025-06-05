from typing import Dict, Any, Callable
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QMenu, QAction, QActionGroup
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, pyqtSignal

class MenuManager:
    """
    Manages the application menu bar and toolbar with actions.
    
    This class is responsible for creating and managing the menu bar and toolbar
    for the application. It provides methods for adding menus, actions, and
    connecting them to appropriate signals and shortcuts.
    """
    
    def __init__(self, main_window: QMainWindow):
        """
        Initialize the menu manager.
        
        Args:
            main_window: The main window that will hold the menu bar
        """
        self._main_window = main_window
        self._menu_bar = main_window.menuBar()

        # Store menus and actions for later reference
        self._menus: Dict[str, QMenu] = {}
        self._actions: Dict[str, QAction] = {}
        
        # Set up standard menus
        self._setup_menus()
        
    def _setup_menus(self):
        """Set up the standard menu structure."""
        # File menu
        file_menu = self.add_menu("&File")
        
        # Edit menu
        edit_menu = self.add_menu("&Edit")
        
        # View menu
        view_menu = self.add_menu("&View")
        
        # Help menu
        help_menu = self.add_menu("&Help")
        
    def setup_file_menu(self, callbacks):
        """
        Set up the file menu with actions.
        
        Args:
            callbacks: Dictionary of callback functions for the actions
        """
        file_menu = self.get_menu("&File")
        if not file_menu:
            return
            
        # New document
        self.add_action(
            file_menu, "New", None, 
            QKeySequence("Ctrl+N"), 
            callbacks.get("new_document")
        )
        
        # Open document
        self.add_action(
            file_menu, "Open...", None, 
            QKeySequence("Ctrl+O"), 
            callbacks.get("open_document")
        )
        
        # Add separator
        self.add_separator(file_menu)
        
        # Save document
        self.add_action(
            file_menu, "Save", None, 
            QKeySequence("Ctrl+S"), 
            callbacks.get("save_document")
        )
        
        # Save As document
        self.add_action(
            file_menu, "Save As...", None, 
            QKeySequence("Ctrl+Shift+S"), 
            callbacks.get("save_document_as")
        )
        
        # Add separator
        self.add_separator(file_menu)
        
        # Exit application
        self.add_action(
            file_menu, "Exit", None, 
            QKeySequence("Alt+F4"), 
            callbacks.get("exit_application")
        )
    
    def setup_edit_menu(self, callbacks):
        """
        Set up the edit menu with actions.
        
        Args:
            callbacks: Dictionary of callback functions for the actions
        """
        edit_menu = self.get_menu("&Edit")
        if not edit_menu:
            return
            
        # Undo
        self.add_action(
            edit_menu, "Undo", None, 
            QKeySequence("Ctrl+Z"), 
            callbacks.get("undo")
        )
        
        # Redo
        self.add_action(
            edit_menu, "Redo", None, 
            QKeySequence("Ctrl+Y"), 
            callbacks.get("redo")
        )
        
        # Add separator
        self.add_separator(edit_menu)
        
        # Cut
        self.add_action(
            edit_menu, "Cut", None, 
            QKeySequence("Ctrl+X"), 
            callbacks.get("cut")
        )
        
        # Copy
        self.add_action(
            edit_menu, "Copy", None, 
            QKeySequence("Ctrl+C"), 
            callbacks.get("copy")
        )
        
        # Paste
        self.add_action(
            edit_menu, "Paste", None, 
            QKeySequence("Ctrl+V"), 
            callbacks.get("paste")
        )
        
        # Add separator
        self.add_separator(edit_menu)
        
        # Line operations submenu
        line_menu = edit_menu.addMenu("Line Operations")
        
        # Move line up
        self.add_action(
            line_menu, "Move Line Up", None, 
            QKeySequence("Alt+Up"), 
            callbacks.get("move_line_up")
        )
        
        # Move line down
        self.add_action(
            line_menu, "Move Line Down", None, 
            QKeySequence("Alt+Down"), 
            callbacks.get("move_line_down")
        )
        
        # Add separator
        self.add_separator(line_menu)
        
        # Insert line
        self.add_action(
            line_menu, "Insert Line", None, 
            QKeySequence("Ctrl+I"), 
            callbacks.get("insert_line")
        )
        
        # Edit line
        self.add_action(
            line_menu, "Edit Line", None, 
            QKeySequence("Ctrl+E"), 
            callbacks.get("edit_line")
        )
        
        # Delete line
        self.add_action(
            line_menu, "Delete Line", None, 
            QKeySequence("Ctrl+D"), 
            callbacks.get("delete_line")
        )
        
        # Add separator
        self.add_separator(line_menu)
        
        # Toggle comment
        self.add_action(
            line_menu, "Toggle Comment", None, 
            QKeySequence("Ctrl+/"), 
            callbacks.get("toggle_comment")
        )
        
        # Duplicate line
        self.add_action(
            line_menu, "Duplicate Line", None, 
            QKeySequence("Ctrl+Shift+D"), 
            callbacks.get("duplicate_line")
        )
    
    def setup_view_menu(self, callbacks):
        """
        Set up the view menu with actions.
        
        Args:
            callbacks: Dictionary of callback functions for the actions
        """
        view_menu = self.get_menu("&View")
        if not view_menu:
            return
            
        # Toggle toolbar
        self.add_action(
            view_menu, "Show Toolbar", None, 
            None, 
            callbacks.get("toggle_toolbar"),
            checkable=True
        )
        
        # Add separator
        self.add_separator(view_menu)
        
        # Zoom In
        self.add_action(
            view_menu, "Zoom In", None, 
            QKeySequence("Ctrl++"), 
            callbacks.get("zoom_in")
        )
        
        # Zoom Out
        self.add_action(
            view_menu, "Zoom Out", None, 
            QKeySequence("Ctrl+-"), 
            callbacks.get("zoom_out")
        )
        
        # Reset Zoom
        self.add_action(
            view_menu, "Reset Zoom", None, 
            QKeySequence("Ctrl+0"), 
            callbacks.get("reset_zoom")
        )
    
    def setup_help_menu(self, callbacks):
        """
        Set up the help menu with actions.
        
        Args:
            callbacks: Dictionary of callback functions for the actions
        """
        help_menu = self.get_menu("&Help")
        if not help_menu:
            return
            
        # About
        self.add_action(
            help_menu, "About Lotus", None, 
            None, 
            callbacks.get("about")
        )
    
    def add_menu(self, title: str) -> QMenu:
        """
        Add a menu to the menu bar.
        
        Args:
            title: The title of the menu
            
        Returns:
            The created menu
        """
        menu = self._menu_bar.addMenu(title)
        self._menus[title] = menu
        return menu
    
    def add_action(self, menu: QMenu, title: str, icon_name: str = None, 
                  shortcut: QKeySequence = None, callback: Callable = None,
                  checkable: bool = False) -> QAction:
        """
        Add an action to a menu.
        
        Args:
            menu: The menu to add the action to
            title: The title of the action
            icon_name: Optional name of the icon for the action
            shortcut: Optional keyboard shortcut for the action
            callback: Optional callback function for the action
            checkable: Whether the action is checkable
            
        Returns:
            The created action
        """
        action = QAction(title, self._main_window)
        
        if icon_name:
            action.setIcon(QIcon(icon_name))
        
        if shortcut:
            action.setShortcut(shortcut)
        
        if callback:
            action.triggered.connect(callback)
            
        action.setCheckable(checkable)
        
        menu.addAction(action)
        self._actions[title] = action
            
        return action
    
    def add_separator(self, menu: QMenu, add_to_toolbar: bool = False):
        """
        Add a separator to a menu.
        
        Args:
            menu: The menu to add the separator to
            add_to_toolbar: Whether to add the separator to the toolbar
        """
        menu.addSeparator()
    
    def get_menu(self, title: str) -> QMenu:
        """
        Get a menu by title.
        
        Args:
            title: The title of the menu
            
        Returns:
            The requested menu, or None if not found
        """
        return self._menus.get(title)
    
    def get_action(self, title: str) -> QAction:
        """
        Get an action by title.
        
        Args:
            title: The title of the action
            
        Returns:
            The requested action, or None if not found
        """
        return self._actions.get(title)
    
    def set_action_enabled(self, action_title: str, enabled: bool):
        """
        Enable or disable an action.
        
        Args:
            action_title: The title of the action
            enabled: Whether the action should be enabled
        """
        action = self.get_action(action_title)
        if action:
            action.setEnabled(enabled)
    
    def set_action_checked(self, action_title: str, checked: bool):
        """
        Set whether an action is checked.
        
        Args:
            action_title: The title of the action
            checked: Whether the action should be checked
        """
        action = self.get_action(action_title)
        if action and action.isCheckable():
            action.setChecked(checked)
