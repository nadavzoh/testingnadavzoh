from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QWidget, QTabWidget, QPushButton,
    QRadioButton, QButtonGroup, QGroupBox
)
from PyQt5.QtGui import QKeySequence
from widgets.match_results_list_view import MatchResultsListView
from views.abstract_dialog_view import AbstractDialogView


class AfDialogView(AbstractDialogView):
    """
    Dialog view for Activity Factor configuration.

    This class provides the UI components for the Activity Factor configuration dialog,
    including pattern inputs, activity factor settings, and result previews.
    It extends AbstractDialogView to inherit common dialog functionality.

    Signals:
        templateChanged(str): Emitted when template pattern changes
        templateRegexChanged(bool): Emitted when template regex option changes
        netChanged(str): Emitted when net pattern changes
        netRegexChanged(bool): Emitted when net regex option changes
        afChanged(str): Emitted when activity factor value changes
        emToggled(bool): Emitted when EM option is toggled
        shToggled(bool): Emitted when SH option is toggled
        netsSearchChanged(str): Emitted when nets search text changes
        templatesSearchChanged(str): Emitted when templates search text changes
        netMatchDoubleClicked(str): Emitted when a net match is double-clicked
        templateMatchDoubleClicked(str): Emitted when a template match is double-clicked
        updateResultsClicked(): Emitted when the update results button is clicked
    """
    # Signal definitions
    templateChanged = pyqtSignal(str)
    templateRegexChanged = pyqtSignal(bool)
    netChanged = pyqtSignal(str)
    netRegexChanged = pyqtSignal(bool)
    afChanged = pyqtSignal(str)
    emToggled = pyqtSignal(bool)
    shToggled = pyqtSignal(bool)
    netsSearchChanged = pyqtSignal(str)
    templatesSearchChanged = pyqtSignal(str)
    netMatchDoubleClicked = pyqtSignal(str)
    templateMatchDoubleClicked = pyqtSignal(str)
    updateResultsClicked = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialize the Activity Factor dialog view.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._connect_signals()

    def _create_tabs(self):
        """
        Create the specific tabs for this dialog view.

        Creates and adds the Pattern tab and Comment tab to the tab widget.
        """
        self.pattern_tab = self._create_pattern_tab()
        self.tabs.addTab(self.pattern_tab, "Pattern")

        self.comment_tab = self._create_comment_tab()
        self.tabs.addTab(self.comment_tab, "Comment")

    def _create_pattern_tab(self):
        """
        Create the pattern tab with all AF-specific controls.

        Returns:
            QWidget: The configured pattern tab widget
        """
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

        # Mode selection
        radio_group_box = QGroupBox("Mode")
        radio_layout = QVBoxLayout()
        # Create radio buttons
        self.em_only_radio = QRadioButton("EM only")
        self.sh_only_radio = QRadioButton("SH only")
        self.em_sh_radio = QRadioButton("EM+SH")
        # Add radio buttons to layout
        radio_layout.addWidget(self.em_only_radio)
        radio_layout.addWidget(self.sh_only_radio)
        radio_layout.addWidget(self.em_sh_radio)
        radio_group_box.setLayout(radio_layout)
        # Create button group for mutual exclusivity
        self.mode_button_group = QButtonGroup()
        self.mode_button_group.addButton(self.em_only_radio)
        self.mode_button_group.addButton(self.sh_only_radio)
        self.mode_button_group.addButton(self.em_sh_radio)
        # Set default selection
        self.em_sh_radio.setChecked(True)
        inputs_layout.addWidget(radio_group_box)
        main_layout.addLayout(inputs_layout)

        # Activity Factor input
        af_layout = QHBoxLayout()
        af_layout.addWidget(QLabel("AF:"))
        self.af_edit = QLineEdit()
        self.af_edit.setPlaceholderText("Enter numeric value > 0")
        af_layout.addWidget(self.af_edit)

        self.update_results_button = QPushButton("Update results")

        af_layout.addWidget(self.update_results_button)

        main_layout.addLayout(af_layout)

        self.results_tabs = MatchResultsListView()
        main_layout.addWidget(self.results_tabs)

        # backward compatibility, thinking about removing it
        self.nets_results_area = self.results_tabs.nets_results_area
        self.templates_results_area = self.results_tabs.templates_results_area

        # Line preview
        line_preview_layout = QHBoxLayout()
        line_preview_layout.addWidget(QLabel("Line to be inserted:"))
        self.line_preview = QLineEdit()
        self.line_preview.setReadOnly(True)
        line_preview_layout.addWidget(self.line_preview)
        main_layout.addLayout(line_preview_layout)

        tab.setLayout(main_layout)
        return tab

    def _create_regex_input(self, label_text, placeholder_text):
        """
        Create a layout with a label, line edit, and regex checkbox.

        Args:
            label_text (str): The label text
            placeholder_text (str): The placeholder text for the line edit

        Returns:
            tuple: A tuple containing (layout, line_edit, regex_checkbox)
        """
        layout = QVBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)

        regex_checkbox = QCheckBox("Regexp")
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(regex_checkbox)

        return layout, line_edit, regex_checkbox

    def _connect_signals(self):
        """
        Connect internal widget signals to the view's custom signals.

        Links UI component signals (like textChanged) to the view's signals
        that will be consumed by the controller.
        """
        self.net_edit.textChanged.connect(
            lambda: self.netChanged.emit(self.get_net_pattern())
        )
        self.net_enable_regex.stateChanged.connect(
            lambda: self.netRegexChanged.emit(self.get_net_use_regex())
        )
        self.template_edit.textChanged.connect(
            lambda: self.templateChanged.emit(self.get_template_pattern())
        )
        self.template_enable_regex.stateChanged.connect(
            lambda: self.templateRegexChanged.emit(self.get_template_use_regex())
        )
        self.af_edit.textChanged.connect(
            lambda text: self.afChanged.emit(text)
        )
        self.em_only_radio.toggled.connect(self._on_radio_toggled)
        self.sh_only_radio.toggled.connect(self._on_radio_toggled)
        self.em_sh_radio.toggled.connect(self._on_radio_toggled)

        self.update_results_button.clicked.connect(
            lambda: self.updateResultsClicked.emit()
        )

        self.net_edit.installEventFilter(self)
        self.template_edit.installEventFilter(self)
        self.af_edit.installEventFilter(self)

        self.results_tabs.netsSearchChanged.connect(self.netsSearchChanged)
        self.results_tabs.templatesSearchChanged.connect(self.templatesSearchChanged)
        self.results_tabs.netMatchDoubleClicked.connect(self.netMatchDoubleClicked)
        self.results_tabs.templateMatchDoubleClicked.connect(self.templateMatchDoubleClicked)

    def _on_radio_toggled(self):
        """
        Handle radio button state changes and emit appropriate signals.

        Determines the current state of EM and SH options based on the
        radio button selection and emits corresponding signals.
        """
        em_enabled = self.em_only_radio.isChecked() or self.em_sh_radio.isChecked()
        self.emToggled.emit(em_enabled)

        sh_enabled = self.sh_only_radio.isChecked() or self.em_sh_radio.isChecked()
        self.shToggled.emit(sh_enabled)

    def get_net_pattern(self):
        """
        Get the current net pattern text.

        Returns:
            str: The current net pattern text, trimmed
        """
        return self.net_edit.text().strip()

    def get_net_use_regex(self):
        """
        Check if net regex option is enabled.

        Returns:
            bool: True if the net regex checkbox is checked
        """
        return self.net_enable_regex.isChecked()

    def get_template_pattern(self):
        """
        Get the current template pattern text.

        Returns:
            str: The current template pattern text, trimmed
        """
        return self.template_edit.text().strip()

    def get_template_use_regex(self):
        """
        Check if template regex option is enabled.

        Returns:
            bool: True if the template regex checkbox is checked
        """
        return self.template_enable_regex.isChecked()

    def update_results_preview(self, net_matches, template_matches):
        """
        Update both list views with new match data.

        Args:
            net_matches (list): List of net match strings
            template_matches (list): List of template match strings
        """
        self.results_tabs.update_results(net_matches, template_matches)

    def clear_form(self):
        """
        Clear all input fields in all tabs.

        Resets the form to its default state.
        """
        self.net_edit.clear()
        self.net_enable_regex.setChecked(False)
        self.template_edit.clear()
        self.template_enable_regex.setChecked(False)
        self.af_edit.clear()
        self.em_sh_radio.setChecked(True)  # Default to EM+SH
        self.line_preview.clear()
        self.update_results_preview([], [])
        self.results_tabs.clear_search_box()

        self.clear_comment_tab()

    def fill_from_data(self, data):
        """
        Fill the form with the provided data.

        Args:
            data: Either a dictionary containing field values or a comment string.
                 If a dictionary, it should contain keys corresponding to form fields.
                 If a string beginning with '#', it's treated as a comment.
        """
        # TODO: this method currently handles both tab changes, tab enabling and data filling.
        # ideally we would separate these actions to 3 methods but this is just a tmp fix.
        if not data:
            # If data is None or empty, clear the form
            self.clear_form()
            self.tabs.setTabEnabled(0, True)  # Disable Pattern tab
            self.tabs.setTabEnabled(1, True)  # Enable Comment tab
        elif isinstance(data, dict):
            self.tabs.setTabEnabled(1, False)  # Disable Comment tab
            self.tabs.setTabEnabled(0, True)  # Enable Pattern tab
            self.tabs.setCurrentIndex(0)  # Switch to Pattern tab

            self.template_edit.setText(data.get("template", ""))
            self.template_enable_regex.setChecked(data.get("template_regex", False))
            self.net_edit.setText(data.get("net", ""))
            self.net_enable_regex.setChecked(data.get("net_regex", False))

            self.af_edit.setText(data.get("af", ""))
            em = data.get("em", False)
            sh = data.get("sh", False)

            if em and sh:
                self.em_sh_radio.setChecked(True)
            elif em:
                self.em_only_radio.setChecked(True)
            elif sh:
                self.sh_only_radio.setChecked(True)
            else:
                # If for some reason both are False, default to EM+SH
                self.em_sh_radio.setChecked(True)

        elif isinstance(data, str) and data.startswith("#"):
            self.tabs.setTabEnabled(0, False)  # Disable Pattern tab
            self.tabs.setTabEnabled(1, True)  # Enable Comment tab
            self.tabs.setCurrentIndex(1)  # Switch to Comment tab
            self.comment_edit.setText(data.strip("#").strip())

    def set_editable(self, editable):
        """
        Enable or disable editing of form fields.

        Args:
            editable (bool): True to enable editing, False to disable
        """
        super().set_editable(editable)

        self.net_edit.setEnabled(editable)
        self.net_enable_regex.setEnabled(editable)
        self.template_edit.setEnabled(editable)
        self.template_enable_regex.setEnabled(editable)
        self.af_edit.setEnabled(editable)
        self.em_only_radio.setEnabled(editable)
        self.sh_only_radio.setEnabled(editable)
        self.em_sh_radio.setEnabled(editable)
        self.comment_edit.setEnabled(editable)

    def update_nets_count_label(self, count):
        """
        Update the nets count label with the current number of items.

        Args:
            count (int): Number of items to display
        """
        self.results_tabs.nets_tab.count_label.setText(f"{count} items")

    def update_templates_count_label(self, count):
        """
        Update the templates count label with the current number of items.

        Args:
            count (int): Number of items to display
        """
        self.results_tabs.templates_tab.count_label.setText(f"{count} items")

    def update_line_preview(self, line_text):
        """
        Update the line preview with the provided text.

        Args:
            line_text (str): The text to show in the line preview
        """
        self.line_preview.setText(line_text)

    def eventFilter(self, obj, event):
        """
        Event filter to handle Enter key presses in input fields.

        When Enter is pressed in any of the input fields, this triggers
        the update_results_button click action.

        Args:
            obj (QObject): The object that triggered the event.
            event (QEvent): The event that occurred.

        Returns:
            bool: True if the event was handled, False to pass to the default handler
        """
        if event.type() == QEvent.KeyPress and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            if obj in [self.net_edit, self.template_edit, self.af_edit]:
                self.updateResultsClicked.emit()
                return True
        return super().eventFilter(obj, event)
