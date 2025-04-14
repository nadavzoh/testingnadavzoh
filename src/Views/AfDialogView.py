from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QListView, QWidget, QTabWidget
)

from src.Views.AbstractDialogView import AbstractDialogView


class AfDialogView(AbstractDialogView):
    """
    Dialog view for Activity Factor configuration.
    Directly implements all UI components without nested views.
    """
    # Signal definitions
    templateChanged = pyqtSignal(str, bool)  # template, use_regex
    netChanged = pyqtSignal(str, bool)  # pattern, use_regex
    afChanged = pyqtSignal(str)
    emToggled = pyqtSignal(bool)
    shToggled = pyqtSignal(bool)
    netsSearchChanged = pyqtSignal(str)
    templatesSearchChanged = pyqtSignal(str)
    netMatchDoubleClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        self.net_matches_list_model = QStringListModel()
        self.template_matches_list_model = QStringListModel()
        super().__init__(parent)
        self._connect_signals()

    def _create_specific_tabs(self):
        """Create the specific tabs for this dialog view."""
        # Create Pattern tab
        self.pattern_tab = self._create_pattern_tab()
        self.tabs.addTab(self.pattern_tab, "Pattern")

        # Create Comment tab using parent method
        self.comment_tab = self._create_comment_tab()
        self.tabs.addTab(self.comment_tab, "Comment")

    def _create_pattern_tab(self):
        """Create the pattern tab with all AF-specific controls."""
        tab = QWidget()
        main_layout = QVBoxLayout()

        # === Input Section ===
        inputs_layout = QHBoxLayout()

        # Template input
        template_layout, self.template_edit, self.template_enable_regex = (
            self._create_regex_input("Template:", "Enter pattern or regex"))
        inputs_layout.addLayout(template_layout)

        # Net input
        net_layout, self.net_edit, self.net_enable_regex = (
            self._create_regex_input("Net:", "Enter pattern or regex"))
        inputs_layout.addLayout(net_layout)

        # Checkboxes
        checkbox_layout = QVBoxLayout()
        self.em_checkbox = QCheckBox("EM")
        self.sh_checkbox = QCheckBox("SH")
        checkbox_layout.addWidget(self.em_checkbox)
        checkbox_layout.addWidget(self.sh_checkbox)
        inputs_layout.addLayout(checkbox_layout)

        main_layout.addLayout(inputs_layout)

        # Activity Factor input
        af_layout = QHBoxLayout()
        af_layout.addWidget(QLabel("AF:"))
        self.af_edit = QLineEdit()
        self.af_edit.setPlaceholderText("Enter numeric value > 0")
        af_layout.addWidget(self.af_edit)
        main_layout.addLayout(af_layout)

        # Results Tabs
        self.results_tabs = QTabWidget()
        all_nets_tab = self._create_results_tab("All Nets")
        all_templates_tab = self._create_results_tab("All Templates")
        self.results_tabs.addTab(all_nets_tab, "All Nets")
        self.results_tabs.addTab(all_templates_tab, "All Templates")
        main_layout.addWidget(self.results_tabs)

        # Store references to results areas
        self.nets_results_area = all_nets_tab.results_area
        self.templates_results_area = all_templates_tab.results_area

        # Connect double-click signal for nets results area
        self.nets_results_area.doubleClicked.connect(self._on_net_item_double_clicked)

        # Line preview
        line_preview_layout = QHBoxLayout()
        line_preview_layout.addWidget(QLabel("Line to be inserted:"))
        self.line_preview = QLineEdit()
        self.line_preview.setReadOnly(True)
        line_preview_layout.addWidget(self.line_preview)
        main_layout.addLayout(line_preview_layout)

        tab.setLayout(main_layout)
        return tab

    def _on_net_item_double_clicked(self, index):
        """Handle double click on an item in the nets results area"""
        if index.isValid():
            # Get the text of the clicked item
            item_text = self.net_matches_list_model.data(index, Qt.DisplayRole)
            if item_text:
                # Extract template and net from the item text (format is usually "template:net")
                self.netMatchDoubleClicked.emit(item_text)

    def _create_regex_input(self, label_text, placeholder_text):
        """Create a layout with a label, line edit, and regex checkbox."""
        layout = QVBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)

        regex_checkbox = QCheckBox("Regexp")
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(regex_checkbox)

        return layout, line_edit, regex_checkbox

    def _create_results_tab(self, tab_name):
        """Create a results tab with a list view and search box."""
        results_tab = QWidget()
        results_layout = QVBoxLayout()

        # Create results list view
        results_tab.results_area = QListView()
        if tab_name == "All Nets":
            results_tab.results_area.setModel(self.net_matches_list_model)
        else:
            results_tab.results_area.setModel(self.template_matches_list_model)

        results_tab.results_area.setEditTriggers(QListView.NoEditTriggers)
        results_tab.results_area.setAlternatingRowColors(True)
        results_tab.results_area.setSelectionMode(QListView.SingleSelection)
        results_layout.addWidget(results_tab.results_area)

        # Create search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        results_tab.search_box = QLineEdit()
        results_tab.search_box.setPlaceholderText("Search results...")

        if tab_name == "All Nets":
            results_tab.search_box.textChanged.connect(
                lambda: self.netsSearchChanged.emit(results_tab.search_box.text()))
        else:
            results_tab.search_box.textChanged.connect(
                lambda: self.templatesSearchChanged.emit(results_tab.search_box.text()))

        search_layout.addWidget(results_tab.search_box)
        results_layout.addLayout(search_layout)

        results_tab.setLayout(results_layout)
        return results_tab

    def _connect_signals(self):
        """Connect internal widget signals to our custom signals."""
        self.net_edit.textChanged.connect(
            lambda: self.netChanged.emit(self.get_net_pattern(), self.get_net_use_regex())
        )
        self.net_enable_regex.stateChanged.connect(
            lambda: self.netChanged.emit(self.get_net_pattern(), self.get_net_use_regex())
        )
        self.template_edit.textChanged.connect(
            lambda: self.templateChanged.emit(self.get_template_pattern(), self.get_template_use_regex())
        )
        self.template_enable_regex.stateChanged.connect(
            lambda: self.templateChanged.emit(self.get_template_pattern(), self.get_template_use_regex())
        )
        self.af_edit.textChanged.connect(
            lambda text: self.afChanged.emit(text)
        )
        self.em_checkbox.stateChanged.connect(
            lambda state: self.emToggled.emit(state == Qt.Checked)
        )
        self.sh_checkbox.stateChanged.connect(
            lambda state: self.shToggled.emit(state == Qt.Checked)
        )

    # Helper methods for the controller
    def get_net_pattern(self):
        return self.net_edit.text().strip()

    def get_net_use_regex(self):
        return self.net_enable_regex.isChecked()

    def get_template_pattern(self):
        return self.template_edit.text().strip()

    def get_template_use_regex(self):
        return self.template_enable_regex.isChecked()

    def update_results_preview(self, net_matches, template_matches):
        """Update both list views with new data."""
        # Convert the text into lists of items
        net_items = [line for line in net_matches.split('\n') if line.strip()]
        template_items = [line for line in template_matches.split('\n') if line.strip()]

        self.net_matches_list_model.setStringList(net_items)
        self.template_matches_list_model.setStringList(template_items)

    def clear_form(self):
        """Clear all input fields in the current tab."""
        if self.tabs.currentIndex() == 0:  # Pattern tab
            self.net_edit.clear()
            self.net_enable_regex.setChecked(False)
            self.template_edit.clear()
            self.template_enable_regex.setChecked(False)
            self.af_edit.clear()
            self.em_checkbox.setChecked(False)
            self.sh_checkbox.setChecked(False)
            self.update_results_preview("", "")
        else:  # Comment tab
            self.clear_comment_tab()

    def fill_from_data(self, data):
        """Fill the form with the provided data."""
        if isinstance(data, dict):
            # Switch to Pattern tab
            self.tabs.setCurrentIndex(0)

            # Fill AF-specific fields from data dictionary
            self.template_edit.setText(data.get("template", ""))
            self.template_enable_regex.setChecked(data.get("template_regex", False))
            self.net_edit.setText(data.get("net", ""))
            self.net_enable_regex.setChecked(data.get("net_regex", False))
            self.af_edit.setText(data.get("af", ""))
            self.em_checkbox.setChecked(data.get("em", False))
            self.sh_checkbox.setChecked(data.get("sh", False))
        elif isinstance(data, str) and data.startswith("#"):
            # Switch to Comment tab
            self.tabs.setCurrentIndex(1)
            self.comment_edit.setText(data.strip("#").strip())

    def set_editable(self, editable):
        """Enable or disable editing of form fields."""
        # Call parent implementation for common components
        super().set_editable(editable)

        self.net_edit.setEnabled(editable)
        self.net_enable_regex.setEnabled(editable)
        self.template_edit.setEnabled(editable)
        self.template_enable_regex.setEnabled(editable)
        self.af_edit.setEnabled(editable)
        self.em_checkbox.setEnabled(editable)
        self.sh_checkbox.setEnabled(editable)
        self.comment_edit.setEnabled(editable)