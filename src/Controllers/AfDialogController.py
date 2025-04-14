from PyQt5.QtCore import pyqtSignal, Qt
from src.Controllers.AbstractDialogController import AbstractDialogController


class AfDialogController(AbstractDialogController):
    """Controller for the Activity Factor Dialog"""

    def __init__(self, model, view):
        self.unfiltered_net_matches = []
        self.unfiltered_template_matches = []
        super().__init__(model, view)
        # Start with form disabled
        self.toggle_tab_editable(False)

    def _connect_signals(self):
        """Connect signals from the view to slots in this controller."""
        # Connect AF tab specific signals
        self.view.netChanged.connect(self.on_net_changed)
        self.view.templateChanged.connect(self.on_template_changed)
        self.view.afChanged.connect(self.on_af_changed)
        self.view.emToggled.connect(self.on_em_toggled)
        self.view.shToggled.connect(self.on_sh_toggled)

        # Connect search signals
        self.view.netsSearchChanged.connect(self.on_net_search_changed)
        self.view.templatesSearchChanged.connect(self.on_template_search_changed)
        self.view.netMatchDoubleClicked.connect(self.on_item_double_clicked)
        # Connect common buttons
        self.view.reset_button.clicked.connect(self._on_clear_dialog_requested)
        self.view.cancel_button.clicked.connect(self._on_cancel_dialog)
        self.view.save_line_button.clicked.connect(self._on_save_line_requested)

    def get_active_tab(self):
        """Get the index of the currently active tab."""
        return self.view.tabs.currentIndex()

    def on_net_search_changed(self, search_text):
        """Handle net search text changes."""
        if not search_text:
            filtered_matches = self.unfiltered_net_matches
            if self.edit_mode:
                self.view.save_line_button.setEnabled(True)
        else:
            filtered_matches = [match for match in self.unfiltered_net_matches
                                if search_text.lower() in match.lower()]
            if self.edit_mode:
                self.view.save_line_button.setEnabled(False)
        self.view.net_matches_list_model.setStringList(filtered_matches)

    def on_template_search_changed(self, search_text):
        """Handle template search text changes."""
        if not search_text:
            filtered_matches = self.unfiltered_template_matches
            if self.edit_mode:
                self.view.save_line_button.setEnabled(True)
        else:
            filtered_matches = [match for match in self.unfiltered_template_matches
                                if search_text.lower() in match.lower()]
            if self.edit_mode:
                self.view.save_line_button.setEnabled(False)
        self.view.template_matches_list_model.setStringList(filtered_matches)


    def on_item_double_clicked(self, item_text):
        """Handle double-click on a net item in the results list"""
        # Parse the item text which should be in format "template:net"
        try:
            if ":" in item_text:
                template, net = item_text.split(":", 1)
                # Set the fields with the selected values
                self.model.template = template
                self.model.net = net
                self.model.template_regex = False
                self.model.net_regex = False
                self.model.em_enabled = False
                self.model.sh_enabled = False

                # Update the view
                self.view.template_edit.setText(template)
                self.view.net_edit.setText(net)
                self.view.template_enable_regex.setChecked(False)
                self.view.net_enable_regex.setChecked(False)
                self.view.em_checkbox.setChecked(False)
                self.view.sh_checkbox.setChecked(False)

                # Update the line preview
                self.update_line_preview()
        except Exception as e:
            print(f"Internal Error. Could not parse double-clicked item: {e}")

    def toggle_tab_editable(self, editable: bool):
        """Enable or disable editing of the form."""
        self.view.set_editable(editable)

    def _on_cancel_dialog(self):
        """Handle dialog cancel."""
        self.dialog_cancelled.emit()
        self.toggle_tab_editable(False)

    def fill_dialog_with_line(self, line):
        """Fill dialog with data parsed from config line."""
        if line.startswith("#"):
            # It's a comment
            # Parse data into a format the view can understand
            data = line
        else:
            # It's an AF line
            try:
                data = self.model.get_fields_from_line(line)
            except ValueError as e:
                self.view.show_error("Invalid line format", str(e))
                return

        # Let the view handle the filling using the data
        self.view.fill_from_data(data)

        # Update preview displays if it's an AF line
        if not line.startswith("#"):
            self.display_matches_preview()

    def _on_save_line_requested(self):
        """Handle save button click."""
        if self.get_active_tab() == 0:  # Pattern tab
            try:
                if self.model.validate_input():
                    self.dialog_accepted.emit(self.view.line_preview.text())
            except ValueError as e:
                self.view.show_error("Validation Error", str(e))
                return
        elif self.get_active_tab() == 1:  # Comment tab
            self.dialog_accepted.emit(f"# {self.view.comment_edit.toPlainText()}")

        self.dialog_cancelled.emit()
        self.toggle_tab_editable(False)

    def on_net_changed(self, net, use_regex):
        """Handle net pattern change."""
        self.model.net = net
        self.model.net_regex = use_regex
        self.display_matches_preview()
        self.update_line_preview()

    def on_template_changed(self, template, use_regex):
        """Handle template pattern change."""
        self.model.template = template
        self.model.template_regex = use_regex
        self.display_matches_preview()
        self.update_line_preview()

    def on_af_changed(self, af_text):
        """Handle activity factor change."""
        self.model.activity_factor = af_text
        self.update_line_preview()

    def on_em_toggled(self, enabled):
        """Handle EM checkbox toggle."""
        self.model.em_enabled = enabled
        self.update_line_preview()

    def on_sh_toggled(self, enabled):
        """Handle SH checkbox toggle."""
        self.model.sh_enabled = enabled
        self.update_line_preview()

    def display_matches_preview(self):
        """Update the preview with current matches."""
        try:
            net_matches, template_matches = self.model.find_matches()
            self.unfiltered_net_matches = net_matches
            self.unfiltered_template_matches = template_matches
            if net_matches:
                self.view.update_results_preview("\n".join(net_matches), "\n".join(template_matches))
            else:
                self.view.update_results_preview("No matches found.", "")
        except ValueError as e:
            self.view.update_results_preview(str(e), str(e))

    def update_line_preview(self):
        """Update the line preview with formatted line."""
        line = self.model.format_line()
        self.view.line_preview.setText(line)

    def _on_clear_dialog_requested(self):
        """Handle dialog reset."""
        self.view.clear_form()

    def set_edit_mode(self, is_edit: bool):
        """Set whether the dialog is in edit mode."""
        self.edit_mode = is_edit
        self.toggle_tab_editable(is_edit)