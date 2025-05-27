from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel, QTimer
from PyQt5.QtGui import QKeySequence, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListView, QLineEdit, QTabWidget, QShortcut

from models.lazy_loading_list_model import LazyLoadingListModel


class ResultsTab(QWidget):
    """
    A reusable tab widget for displaying search results with filtering.

    This widget provides efficient display of search results with debounced
    search filtering, performance optimizations for large datasets, and
    visual feedback during long operations.

    Signals:
        itemDoubleClicked(str): Emitted when an item is double-clicked
        searchChanged(str): Emitted when search text changes

    Attributes:
        title (str): The title of this results tab
        search_box (QLineEdit): Input field for search/filter text
        count_label (QLabel): Label showing the number of items
        results_area (QListView): List view displaying results
        results_model: Model for the list view (QStringListModel or LazyLoadingListModel)
        _all_items (list): Complete list of all items before filtering
        _filtered_items (list): List of items after filtering is applied
        _search_timer (QTimer): Timer for debounced search
        _pending_search_text (str): Text waiting to be searched
        _search_in_progress (bool): Whether a search operation is in progress
    """

    itemDoubleClicked = pyqtSignal(str)
    searchChanged = pyqtSignal(str)

    def __init__(self, title, search_shortcut_key=None, parent=None):
        """
        Initialize a new ResultsTab.

        Args:
            title (str): The tab title
            search_shortcut_key (QKeySequence, optional): The keyboard shortcut to focus the search box
            parent (QWidget, optional): The parent widget
        """
        super().__init__(parent)
        self.title = title
        self.search_shortcut_key = search_shortcut_key
        self._all_items = []  # Initialize empty items list
        self._filtered_items = []  # Initial filtered items list

        # Create a timer for debouncing search
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(1000)  # 1000ms (1 second) debounce time
        self._search_timer.timeout.connect(self._perform_search)
        self._pending_search_text = ""

        # Flag to avoid unnecessary updates
        self._search_in_progress = False

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """
        Set up the user interface components.

        Creates and arranges all UI elements including search box and results list.
        """
        layout = QVBoxLayout(self)

        # Search box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(f"Search {self.title.lower()}...")
        search_layout.addWidget(QLabel("Filter:"))
        search_layout.addWidget(self.search_box)

        # Count label
        self.count_label = QLabel("0 items")
        search_layout.addWidget(self.count_label)

        layout.addLayout(search_layout)

        # Results list
        self.results_area = QListView()

        # Use QStringListModel initially - we'll update to LazyLoadingListModel when needed
        self.results_model = QStringListModel()
        self.results_area.setModel(self.results_model)

        layout.addWidget(self.results_area)

        # Configure search shortcut if provided
        if self.search_shortcut_key:
            self.search_shortcut = QShortcut(self.search_shortcut_key, self)
            self.search_shortcut.activated.connect(self._focus_search)

    def _connect_signals(self):
        """
        Connect signals between internal components.

        Sets up signal-slot connections to handle user interactions.
        """
        # Only connect to _debounced_search, not directly to signal
        self.search_box.textChanged.connect(self._debounced_search)
        self.results_area.doubleClicked.connect(self._on_item_double_clicked)

    def _focus_search(self):
        """
        Focus the search box and select all text in it.

        Called when the search shortcut is activated.
        """
        self.search_box.setFocus()
        self.search_box.selectAll()

    def _get_item_provider(self):
        """
        Return a data provider function for the LazyLoadingListModel.

        This function fetches chunks of data when requested by the lazy loading model.

        Returns:
            function: A data provider function that takes start and count parameters
        """

        def provider(start, count):
            # This function provides a chunk of items starting at 'start' with length 'count'
            if not hasattr(self, '_filtered_items') or not self._filtered_items:
                return []

            end = min(start + count, len(self._filtered_items))
            return self._filtered_items[start:end]

        return provider

    def _debounced_search(self, text):
        """
        Store the search text and start/restart the debounce timer.

        This delays the actual filtering operation until the user pauses typing,
        preventing performance issues when typing quickly.

        Args:
            text (str): The search text entered by the user
        """
        # If text hasn't changed, don't trigger a new search
        if self._pending_search_text == text:
            return

        self._pending_search_text = text

        # Show a "Searching..." message in the count label if there are many items
        if hasattr(self, '_all_items') and len(self._all_items) > 1000:
            self.count_label.setText("Searching...")

        # Don't emit searchChanged signal here - only after search completes
        # Instead, mark search as in-progress
        self._search_in_progress = True

        # Start/restart the debounce timer
        self._search_timer.start()

    def _perform_search(self):
        """
        Perform the actual search after the debounce period.

        Filters the items based on the pending search text and updates the model.
        This is called automatically when the debounce timer expires.
        """
        filter_text = self._pending_search_text

        if not hasattr(self, '_all_items'):
            self._search_in_progress = False
            return

        try:
            # Apply filtering
            if not filter_text:
                self._filtered_items = self._all_items
            else:
                # Filter the items - this is the potentially slow operation
                self._filtered_items = [item for item in self._all_items if filter_text.lower() in item.lower()]

            # Update the model based on its type
            if isinstance(self.results_model, QStringListModel):
                self.results_model.setStringList(self._filtered_items)
            else:
                # For LazyLoadingListModel
                self.results_model.setItemCount(len(self._filtered_items))

            # Update count label
            self.count_label.setText(f"{len(self._filtered_items)} items")

            # NOW emit the searchChanged signal with the final search text
            # but only if this was triggered by typing (not programmatic filtering)
            if self._search_in_progress:
                self.searchChanged.emit(filter_text)
                self._search_in_progress = False

        except Exception as e:
            self.count_label.setText("Error filtering")
            self._search_in_progress = False

    def _filter_results(self, filter_text):
        """
        Legacy filter function - now uses the debounced search mechanism.

        This is kept for backward compatibility with existing code.

        Args:
            filter_text (str): Text to filter by
        """
        # This is called programmatically, not from user typing
        self._search_in_progress = False
        self._pending_search_text = filter_text

        # If called directly (not from textChanged), perform the search immediately
        # Cancel any pending search timer to avoid conflicts
        if self._search_timer.isActive():
            self._search_timer.stop()

        self._perform_search()

    def _on_item_double_clicked(self, index):
        """
        Handle double-click on an item in the results list.

        Emits the itemDoubleClicked signal with the text of the selected item.

        Args:
            index (QModelIndex): The index that was clicked
        """
        try:
            if not index.isValid():
                return

            item = self.results_model.data(index, Qt.DisplayRole)
            if item:
                self.itemDoubleClicked.emit(item)
        except Exception as e:
            print(f"Error handling double-click in {self.title} tab: {str(e)}")

    def set_items(self, items):
        """
        Set the items to be displayed in the list.

        This method automatically chooses between QStringListModel and
        LazyLoadingListModel based on the size of the dataset for optimal performance.

        Args:
            items (list): List of strings to display
        """
        try:
            if items is None:
                items = []

            if isinstance(items, str):
                print(f"{self.title} tab received string instead of list for items")
                items = []

            self._all_items = items
            self._filtered_items = items  # Start with all items visible

            # For small datasets, use QStringListModel for simplicity and better performance
            if len(items) <= 1000:
                if not isinstance(self.results_model, QStringListModel):
                    self.results_model = QStringListModel()
                    self.results_area.setModel(self.results_model)
                self.results_model.setStringList(items)
            else:
                # For large datasets, use LazyLoadingListModel
                # Only create a new model if needed to avoid UI flicker
                if not isinstance(self.results_model, LazyLoadingListModel):
                    self.results_model = LazyLoadingListModel(self._get_item_provider())
                    self.results_model.setChunkSize(100)  # Load more items at once for smoother scrolling
                    self.results_area.setModel(self.results_model)
                self.results_model.setItemCount(len(items))

            self.count_label.setText(f"{len(items)} items")

            # Re-apply any existing filter
            if self.search_box.text():
                # Use the direct filter to avoid debounce delay on initial load
                self._filter_results(self.search_box.text())

        except Exception as e:
            print(f"Error setting items in {self.title} tab: {str(e)}")
            self.count_label.setText("Error loading items")


    def keyPressEvent(self, event):
        """
        Handle key press events for the results tab.

        Specifically captures Enter/Return key presses to trigger item activation
        when the list view has focus.

        Args:
            event (QKeyEvent): The key event to process
        """
        # When Enter/Return is pressed anywhere in the tab, delegate to results_area if it has focus
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            # Check if results_area has focus
            if self.results_area.hasFocus():
                current = self.results_area.currentIndex()
                if current.isValid():
                    self._on_item_double_clicked(current)
                    return  # Event handled, don't pass to parent

        # For all other cases, pass the event to the parent class
        super().keyPressEvent(event)


class MatchResultsListView(QTabWidget):
    """
    A tabbed widget displaying pattern matching results.

    This widget provides two tabs: one for nets results and one for templates results.
    It handles search, filtering, and displaying of matching items with efficient
    lazy loading for large datasets.

    Signals:
        netMatchDoubleClicked(str): Emitted when a net match is double-clicked
        templateMatchDoubleClicked(str): Emitted when a template match is double-clicked
        netsSearchChanged(str): Emitted when the nets search text changes
        templatesSearchChanged(str): Emitted when the templates search text changes

    Attributes:
        nets_tab (ResultsTab): Tab for displaying net matches
        templates_tab (ResultsTab): Tab for displaying template matches
        nets_results_area (QListView): Direct reference to the nets list view
        templates_results_area (QListView): Direct reference to the templates list view
    """

    netMatchDoubleClicked = pyqtSignal(str)
    templateMatchDoubleClicked = pyqtSignal(str)
    netsSearchChanged = pyqtSignal(str)
    templatesSearchChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initialize a new MatchResultsListView widget.

        Args:
            parent (QWidget, optional): The parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

        # Configure tab bar to expand tab width
        self.setTabsClosable(False)
        self.tabBar().setExpanding(False)  # Don't expand to fill space

        # Apply adaptive styling for tabs
        self.setStyleSheet("""
            QTabBar::tab {
                padding-left: 15px;
                padding-right: 15px;
                padding-top: 5px;
                padding-bottom: 5px;
            }
        """)

    def _setup_ui(self):
        """
        Set up the user interface components.

        Creates the nets and templates tabs with their respective list views.
        """
        self.nets_tab = ResultsTab("Nets", search_shortcut_key=QKeySequence("Ctrl+F"))
        self.templates_tab = ResultsTab("Templates", search_shortcut_key=QKeySequence("Ctrl+F"))

        self.addTab(self.nets_tab, "Nets")
        self.addTab(self.templates_tab, "Templates")

        # backward compatibility
        self.nets_results_area = self.nets_tab.results_area
        self.templates_results_area = self.templates_tab.results_area

    def _connect_signals(self):
        """
        Connect signals between internal components.

        Sets up signal-slot connections to relay signals from tabs to this widget.
        """
        self.nets_tab.itemDoubleClicked.connect(self.netMatchDoubleClicked)
        self.templates_tab.itemDoubleClicked.connect(self.templateMatchDoubleClicked)
        self.nets_tab.searchChanged.connect(self.netsSearchChanged)
        self.templates_tab.searchChanged.connect(self.templatesSearchChanged)

    def update_results(self, net_matches, template_matches):
        """
        Update both net and template results.

        Sets the items to be displayed in both tabs and updates tab titles
        to include the count of items.

        Args:
            net_matches (list): List of matching net strings
            template_matches (list): List of matching template strings
        """
        try:
            self.nets_tab.set_items(net_matches)
            self.templates_tab.set_items(template_matches)

            # Update tab titles with counts
            nets_text = f"Nets ({len(net_matches) if net_matches else 0})"
            templates_text = f"Templates ({len(template_matches) if template_matches else 0})"

            self.setTabText(0, nets_text)
            self.setTabText(1, templates_text)

            # Calculate if we need to adjust tab widths for the text
            font_metrics = QFontMetrics(self.font())
            nets_width = font_metrics.horizontalAdvance(nets_text) + 20  # Add padding
            templates_width = font_metrics.horizontalAdvance(templates_text) + 20  # Add padding

            # Ensure tab bar has enough width
            self.tabBar().setMinimumWidth(nets_width + templates_width)

        except Exception as e:
            print(f"Error updating results: {str(e)}")
            self.setTabText(0, "Nets (Error)")
            self.setTabText(1, "Templates (Error)")

    def filter_nets(self, filter_text):
        """
        Filter nets results by the given text.

        Delegates to the nets tab's filter method.

        Args:
            filter_text (str): Text to filter by
        """
        self.nets_tab._filter_results(filter_text)

    def filter_templates(self, filter_text):
        """
        Filter template results by the given text.

        Delegates to the templates tab's filter method.

        Args:
            filter_text (str): Text to filter by
        """
        self.templates_tab._filter_results(filter_text)

    def clear_search_box(self):
        """
        Clear the search box in both tabs.

        Resets the search text and updates the displayed items.
        """
        self.nets_tab.search_box.clear()
        self.templates_tab.search_box.clear()