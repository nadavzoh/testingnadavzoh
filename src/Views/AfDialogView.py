from PyQt5.QtWidgets import (
    QTabWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
    QLabel, QLineEdit, QCheckBox, QListView, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel


class AfDialogView(QTabWidget):
    templateChanged = pyqtSignal(str, bool)  # template, use_regex
    netChanged = pyqtSignal(str, bool)  # pattern, use_regex
    afChanged = pyqtSignal(str)

    emToggled = pyqtSignal(bool)
    shToggled = pyqtSignal(bool)

    netsSearchChanged = pyqtSignal(str)
    templatesSearchChanged = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.net_matches_list_model = QStringListModel()
        self.template_matches_list_model = QStringListModel()
        self._setup_ui()
        self._connect_signals()

    def _create_regex_input(self, label_text, placeholder_text):
        """Create a layout with a label, line edit, and regex checkbox."""
        layout = QVBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)

        regex_checkbox = QCheckBox("Regex")
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(regex_checkbox)

        return layout, line_edit, regex_checkbox

    def _create_results_list_view(self, model=None):
        """Create a configured QListView for results."""
        results_area = QListView()
        if model:
            results_area.setModel(model)
        results_area.setEditTriggers(QListView.NoEditTriggers)
        results_area.setAlternatingRowColors(True)
        results_area.setSelectionMode(QListView.SingleSelection)
        # TODO: double clicking should send a signal with the line and update the dialog
        return results_area

    def _create_results_tab(self, tab_name):
        """Create a results tab with a list view."""
        results_tab = QWidget()
        results_layout = QVBoxLayout()

        # Use the method to create the list view
        results_tab.results_area = (
            self._create_results_list_view(self.net_matches_list_model)
            if tab_name == "All Nets"
            else self._create_results_list_view(self.template_matches_list_model)
        )

        results_layout.addWidget(results_tab.results_area)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        results_tab.search_box = QLineEdit()
        results_tab.search_box.setPlaceholderText("Search results...")
        if tab_name == "All Nets":
            results_tab.search_box.textChanged.connect(lambda: self.netsSearchChanged.emit(results_tab.search_box.text()))
        else:
            results_tab.search_box.textChanged.connect(lambda: self.templatesSearchChanged.emit(results_tab.search_box.text()))

        results_layout.addWidget(results_tab.search_box)
        results_tab.setLayout(results_layout)

        return results_tab

    def _setup_ui(self):
        """Set up the user interface components."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        inputs_layout = QHBoxLayout()
        # Template input
        template_layout, self.template_edit, self.template_enable_regex = (
            self._create_regex_input("Template:","Enter pattern or regex"))
        inputs_layout.addLayout(template_layout)
        # Net input
        net_layout, self.net_edit, self.net_enable_regex = (
            self._create_regex_input("Net:","Enter pattern or regex"))
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
        # Create tabs dynamically
        self.results_tabs.addTab(self._create_results_tab("All Nets"), "All Nets")
        self.results_tabs.addTab(self._create_results_tab("All Templates"), "All Templates")

        main_layout.addWidget(self.results_tabs)

        # Line preview
        line_preview_layout = QHBoxLayout()
        line_preview_label = QLabel("Line to be inserted:")
        line_preview_layout.addWidget(line_preview_label)
        self.line_preview = QLineEdit()
        self.line_preview.setReadOnly(True)
        line_preview_layout.addWidget(self.line_preview)
        main_layout.addLayout(line_preview_layout)


    def _connect_signals(self):
        self.net_edit.textChanged.connect(lambda:
            self.netChanged.emit(self.get_net_pattern(), self.get_net_use_regex())
        )
        self.net_enable_regex.stateChanged.connect(lambda:
            self.netChanged.emit(self.get_net_pattern(), self.get_net_use_regex())
        )
        self.template_edit.textChanged.connect(lambda:
            self.templateChanged.emit(self.get_template_pattern(), self.get_template_use_regex())
        )
        self.template_enable_regex.stateChanged.connect(lambda:
            self.templateChanged.emit(self.get_template_pattern(), self.get_template_use_regex())
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

    def get_net_pattern(self):
        return self.net_edit.text().strip()

    def get_net_use_regex(self):
        return self.net_enable_regex.isChecked()

    def get_template_pattern(self):
        return self.template_edit.text().strip()

    def get_template_use_regex(self):
        return self.template_enable_regex.isChecked()

    def update_results_preview(self, net_matches, template_matches):
        # Convert the text into a list of items
        items = [line for line in net_matches.split('\n') if line.strip()]
        self.net_matches_list_model.setStringList(items)
        items = [line for line in template_matches.split('\n') if line.strip()]
        self.template_matches_list_model.setStringList(items)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)