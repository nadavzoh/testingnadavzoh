from controllers.abstract_dialog_controller import AbstractDialogController


class AfDialogController(AbstractDialogController):
    """
    Controller for the Activity Factor Dialog.

    This controller manages the interactions between the Activity Factor dialog view
    and model, handling events, updating the UI, and maintaining state.

    It provides functionality for:
    - Editing activity factor configuration lines
    - Searching for matching nets and templates
    - Displaying results
    - Validating user input

    Attributes:
        unfiltered_net_matches (list): Complete list of matching nets before filtering
        unfiltered_template_matches (list): Complete list of matching templates before filtering
        edit_mode (bool): Whether the dialog is in edit mode
    """

    def __init__(self, model, view):
        """
        Initialize the controller with model and view instances.

        Args:
            model (AfDialogModel): The data model for activity factor configuration
            view (AfDialogView): The view for the activity factor dialog
        """
        self.unfiltered_net_matches = []
        self.unfiltered_template_matches = []
        super().__init__(model, view)
        # Start with form disabled
        self.toggle_tab_editable(False)

    def _connect_signals(self):
        """
        Connect signals from the view to slots in this controller.

        Connects all UI events to their corresponding handlers, linking user
        actions to controller methods that update the model and view.
        """
        # Connect AF-tab specific signals
        self.view.templateChanged.connect(self.on_template_changed)
        self.view.templateRegexChanged.connect(self.on_template_regex_changed)
        self.view.netChanged.connect(self.on_net_changed)
        self.view.netRegexChanged.connect(self.on_net_regex_changed)
        self.view.afChanged.connect(self.on_af_changed)
        self.view.emToggled.connect(self.on_em_toggled)
        self.view.shToggled.connect(self.on_sh_toggled)
        # Connect search signals
        self.view.netsSearchChanged.connect(self.on_net_search_changed)
        self.view.templatesSearchChanged.connect(self.on_template_search_changed)
        self.view.netMatchDoubleClicked.connect(self.on_item_double_clicked)
        self.view.templateMatchDoubleClicked.connect(self.on_item_double_clicked)
        self.view.updateResultsClicked.connect(self.on_update_button)
        # Connect common buttons
        self.view.reset_button.clicked.connect(self._on_clear_dialog_requested)
        self.view.cancel_button.clicked.connect(self._on_cancel_dialog)
        self.view.save_line_button.clicked.connect(self._on_save_line_requested)

    def get_active_tab(self):
        """
        Get the index of the currently active tab.

        Returns:
            int: Index of the active tab (0 for Pattern, 1 for Comment)
        """
        return self.view.tabs.currentIndex()

    def on_net_search_changed(self, search_text):
        """
        Handle net search text changes.

        Delegates filtering to the results view and handles enabling/disabling
        the save button appropriately in edit mode.

        Args:
            search_text (str): The search text entered by the user
        """
        self.view.results_tabs.filter_nets(search_text)
        # Disable save button in edit mode when searching
        if self.edit_mode:
            self.view.save_line_button.setEnabled(not search_text)

    def on_template_search_changed(self, search_text):
        """
        Handle template search text changes.

        Delegates filtering to the results view and handles enabling/disabling
        the save button appropriately in edit mode.

        Args:
            search_text (str): The search text entered by the user
        """
        self.view.results_tabs.filter_templates(search_text)
        # Disable save button in edit mode when searching
        if self.edit_mode:
            self.view.save_line_button.setEnabled(not search_text)

    def on_item_double_clicked(self, item_text):
        """
        Handle double-click on a net or template item in the results list.

        Parses the selected item and updates the form with its values.

        Args:
            item_text (str): The text of the selected item, typically in "template:net" format
        """
        try:
            if ":" in item_text:
                template, net = item_text.split(":", 1)
                self.model.net_regex = False
            else:
                template, net = item_text, ".*"
                self.model.net_regex = True

            # Update the model
            self.model.template, self.model.net = template, net
            self.model.template_regex = False
            self.model.em_enabled = True
            self.model.sh_enabled = True
            # # Update the view
            self.view.template_edit.setText(template)
            self.view.net_edit.setText(net)
            self.view.template_enable_regex.setChecked(self.model.template_regex)
            self.view.net_enable_regex.setChecked(self.model.net_regex)
            self.view.em_sh_radio.setChecked(True)

            self.on_update_button()

        except Exception as e:
            print(f"Internal Error. Could not parse double-clicked item: {e}")

    def toggle_tab_editable(self, editable: bool):
        """
        Enable or disable editing of the form.

        Args:
            editable (bool): Whether fields should be editable
        """
        self.view.set_editable(editable)

    def _on_cancel_dialog(self):
        """
        Handle dialog cancel action.

        Emits the dialog_cancelled signal and disables editing.
        """
        self.dialog_cancelled.emit()
        self.toggle_tab_editable(False)

    def fill_dialog_with_line(self, line, net_matches=None, template_matches=None):
        """
        Fill dialog with data parsed from a configuration line.

        This method parses the provided line and updates the form fields accordingly.
        If matches are provided, they'll be used instead of performing a new search.

        Args:
            line (str): The configuration line to display
            net_matches (list, optional): Pre-cached list of net matches
            template_matches (list, optional): Pre-cached list of template matches
        """
        if not line:
            data = ""
        elif line.startswith("#"):
            data = line
        else:
            try:
                data = self.model.get_fields_from_line(line)
            except ValueError as e:
                self.view.show_error("Invalid line format", str(e))
                return

        self.view.fill_from_data(data)

        # Update results with pre-cached matches if provided
        if net_matches is not None and template_matches is not None:
            self.unfiltered_net_matches = net_matches
            self.unfiltered_template_matches = template_matches
            self.view.update_results_preview(net_matches, template_matches)
        else:
            # Otherwise, find and display matches
            self.on_update_button()


    def _on_save_line_requested(self):
        """
        Handle save button click.

        Validates input and emits the dialog_accepted signal with the formatted line.
        If validation fails, shows an error message.
        """
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

    def display_matches_preview(self):
        """
        Update the preview with current matches.

        Searches for matches based on current model values and updates the view.
        Performance metrics are logged if debugging is enabled.
        """
        try:
            net_matches, template_matches = self.model.find_matches()

            # Store unfiltered matches for reference
            self.unfiltered_net_matches = net_matches
            self.unfiltered_template_matches = template_matches

            self.view.update_results_preview(net_matches, template_matches)

        except ValueError as e:
            self.view.update_results_preview([], [])

    def update_line_preview(self):
        """
        Update the line preview with formatted line.

        Gets the formatted line from the model and updates the preview field in the view.
        """
        line = self.model.format_line()
        self.view.line_preview.setText(line)

    def _on_clear_dialog_requested(self):
        """
        Handle dialog reset action.

        Clears all form fields in the view.
        """
        self.view.clear_form()

    def set_edit_mode(self, is_edit: bool):
        """
        Set whether the dialog is in edit mode.

        Args:
            is_edit (bool): Whether the dialog should be in edit mode
        """
        self.edit_mode = is_edit
        self.toggle_tab_editable(is_edit)

    def on_net_changed(self, net):
        """
        Handle net pattern change.

        Updates the model and refreshes the line preview.

        Args:
            net (str): The new net pattern value
        """
        self.model.net = net
        self.update_line_preview()

    def on_net_regex_changed(self, use_regex):
        """
        Handle net regex checkbox toggle.

        Updates the model and refreshes the line preview.

        Args:
            use_regex (bool): Whether regex should be enabled for net matching
        """
        self.model.net_regex = use_regex
        self.update_line_preview()

    def on_template_changed(self, template):
        """
        Handle template pattern change.

        Updates the model and refreshes the line preview.

        Args:
            template (str): The new template pattern value
        """
        self.model.template = template
        self.update_line_preview()

    def on_template_regex_changed(self, use_regex):
        """
        Handle template regex checkbox toggle.

        Updates the model and refreshes the line preview.

        Args:
            use_regex (bool): Whether regex should be enabled for template matching
        """
        self.model.template_regex = use_regex
        self.update_line_preview()

    def on_af_changed(self, af_text):
        """
        Handle activity factor change.

        Updates the model and refreshes the line preview.

        Args:
            af_text (str): The new activity factor value
        """
        self.model.activity_factor = af_text
        self.update_line_preview()

    def on_em_toggled(self, enabled):
        """
        Handle EM checkbox toggle.

        Updates the model and refreshes the line preview.

        Args:
            enabled (bool): Whether EM should be enabled
        """
        self.model.em_enabled = enabled
        self.update_line_preview()

    def on_sh_toggled(self, enabled):
        """
        Handle SH checkbox toggle.

        Updates the model and refreshes the line preview.

        Args:
            enabled (bool): Whether SH should be enabled
        """
        self.model.sh_enabled = enabled
        self.update_line_preview()

    def on_update_button(self):
        """
        Handle update button click.

        Triggers a search for matches and updates the results display.
        """
        self.display_matches_preview()
