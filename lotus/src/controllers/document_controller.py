class DocumentController:
    """
    Controller for document operations and interactions.

    Manages interactions between the document model and view, handling operations
    such as line editing, insertion, deletion, and validation, as well as
    synchronizing UI components with the underlying document data.

    Attributes:
        model: The document data model.
        view: The document view.
        dialog_controller: Controller for dialog interactions.
    """

    def __init__(self, model, view):
        """
        Initialize the document controller.

        Args:
            model: The document data model.
            view: The document view component.
        """
        self.model = model
        self.view = view
        self.dialog_controller = None

        # Initialize view with document content
        self.view.update_content(self.model.dcfg_file_content)

        # Update line colors based on validation status
        self.update_line_colors_and_matches()

        # Connect view signals
        self.view.lineSelected.connect(self.on_line_selected)
        self.view.lineDoubleClicked.connect(self.on_line_double_clicked)
        self.view.toggleCommentRequested.connect(self.toggle_comment)  # Ctrl+/ shortcut
        self.view.duplicateLineRequested.connect(self.duplicate_line)  # Ctrl+D shortcut
        self.view.moveLineUpRequested.connect(self.move_line_up)  # Alt + Up shortcut
        self.view.moveLineDownRequested.connect(self.move_line_down)  # Alt + Down shortcut

    def set_dialog_controller(self, dialog_controller):
        """
        Set the dialog controller and connect its signals.

        Args:
            dialog_controller: The dialog controller to use for editing operations.
        """
        self.dialog_controller = dialog_controller
        self.dialog_controller.dialog_accepted.connect(lambda line: self.edit_line(line))
        self.dialog_controller.dialog_accepted.connect(lambda: self.view.setEnabled(True))
        self.dialog_controller.dialog_cancelled.connect(lambda: self._on_cancel_dialog())
        self.dialog_controller.dialog_cancelled.connect(lambda: self.view.setEnabled(True))

    def update_line_colors_and_matches(self):
        """
        Update line colors and pattern matches for all lines in the document.

        Refreshes the validation status for each line, updates text colors
        based on validation, and finds pattern matches for non-comment lines.
        """
        list_model = self.view.get_model()

        # First, make sure model has all the lines
        list_model.setContentFromStringList(self.model.dcfg_file_content)

        # For each line, update validation status and find matches
        for i, line in enumerate(self.model.dcfg_file_content):
            # Update validation status
            validation_status = self.model.get_validation_status(i)
            list_model.updateLineValidation(i, validation_status)

            # Find matches for non-comment lines
            if validation_status != self.model.COMMENT and not line.startswith('#'):
                net_matches, template_matches = self.model.find_matches(line)  # kinda costly but needed, for now.. might refactor.
                list_model.updateLineMatches(i, net_matches, template_matches)

        # Update all line colors based on validation and matches
        list_model.updateAllColors()

    def on_line_selected(self, index):
        """
        Handle line selection event from the view.

        Args:
            index (int): The index of the selected line.
        """
        self.model.set_selected_index(index)

    def on_line_double_clicked(self, index):
        """
        Handle double-click event on a line.

        Opens the line in the dialog for editing, populating the dialog
        with the line content and any pattern matches.

        Args:
            index (int): The index of the double-clicked line.
        """
        if self.dialog_controller and index >= 0:
            line = self.model.dcfg_file_content[index]

            list_model = self.view.get_model()
            line_model = list_model.getLine(index)

            if line_model and not line.startswith('#'):
                # Pass matches to dialog controller if they exist
                net_matches = line_model.get_net_matches() or []
                template_matches = line_model.get_template_matches() or []
                self.dialog_controller.fill_dialog_with_line(line, net_matches, template_matches)
            else:
                self.dialog_controller.fill_dialog_with_line(line)

    def insert_line(self, line):
        """
        Insert a new line at the currently selected position.

        Args:
            line (str): The text content to insert as a new line.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        index = self.view.get_selected_index()
        success = self.model.insert_line(line, index)
        if success:
            list_model = self.view.get_model()
            validation_status = self.model.get_validation_status(index)

            net_matches, template_matches = [], []
            if not line.startswith('#') and line.strip():
                net_matches, template_matches = self.model.find_matches(line)

            list_model.insertLine(index, line, validation_status, net_matches, template_matches)

            self.update_line_colors_and_matches()
            self.view.select_line(index)
            self.on_line_selected(index)
        return success

    def edit_line(self, line):
        """
        Edit the currently selected line.

        Args:
            line (str): The new content for the selected line.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        index = self.model.current_selected_index
        if index >= 0:
            success = self.model.edit_current_line(line)
            if success:
                list_model = self.view.get_model()
                validation_status = self.model.get_validation_status(index)

                net_matches, template_matches = [], []
                if not line.startswith('#') and line.strip():
                    net_matches, template_matches = self.model.find_matches(line)

                list_model.updateLine(index, line)
                list_model.updateLineValidation(index, validation_status)
                list_model.updateLineMatches(index, net_matches, template_matches)
                list_model.updateLineColor(list_model.getLine(index))

                self.update_line_colors_and_matches()
                self.view.select_line(self.model.current_selected_index)
                self.on_line_selected(self.model.current_selected_index)
                self.dialog_controller.set_edit_mode(False)
            return success
        return False

    def enter_edit_mode(self):
        """
        Enable editing mode in the dialog and disable the main view.

        Sends signals to enable the save button in the dialog and makes
        the document temporarily uneditable while editing is in progress.
        """
        self.dialog_controller.set_edit_mode(True)
        self.dialog_controller.toggle_tab_editable(True)
        self.view.setEnabled(False)

    def _on_cancel_dialog(self):
        """
        Handle dialog cancellation.

        Resets edit mode and re-enables the main document view.
        """
        self.dialog_controller.set_edit_mode(False)
        self.view.setEnabled(True)

    def delete_line(self):
        """
        Delete the currently selected line.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        index = self.view.get_selected_index()
        success = self.model.delete_line(index)
        if success:
            list_model = self.view.get_model()
            list_model.removeLine(index)

            # refresh
            self.view.update_content(self.model.dcfg_file_content)
            self.update_line_colors_and_matches()

            # Select the line at the same position (or last line if deleted last)
            new_index = min(index, len(self.model.dcfg_file_content) - 1)
            if new_index >= 0:
                self.view.select_line(new_index)
                self.on_line_selected(new_index)
        return success

    def move_line_up(self):
        if self.model.move_line_up():
            # refresh
            self.view.update_content(self.model.dcfg_file_content)
            self.update_line_colors_and_matches()
            self.view.select_line(self.model.current_selected_index)

    def move_line_down(self):
        if self.model.move_line_down():
            # refresh
            self.view.update_content(self.model.dcfg_file_content)
            self.update_line_colors_and_matches()
            self.view.select_line(self.model.current_selected_index)

    def undo_action(self):
        """
        Undo the last action.

        Returns:
            bool: True if an action was undone, False otherwise.
        """
        success = self.model.undo_last_action()
        if success:
            # refresh
            self.view.update_content(self.model.dcfg_file_content)
            self.update_line_colors_and_matches()

            # Select the appropriate line after undo
            if self.model.current_selected_index >= 0:
                self.view.select_line(self.model.current_selected_index)
                self.on_line_selected(self.model.current_selected_index)
        return success

    def redo_action(self):
        """
        Redo the last undone action.

        Returns:
            bool: True if an action was redone, False otherwise.
        """
        success = self.model.redo_action()
        if success:
            # refresh
            self.view.update_content(self.model.dcfg_file_content)
            self.update_line_colors_and_matches()

            # Select the appropriate line after redo
            if self.model.current_selected_index >= 0:
                self.view.select_line(self.model.current_selected_index)
                self.on_line_selected(self.model.current_selected_index)
        return success

    def save_changes(self):
        """
        Save changes to the document file.

        Returns:
            bool: True if the save operation succeeded, False otherwise.
        """
        success = self.model.save_to_file()
        return success

    def has_unsaved_changes(self):
        """
        Check if the document has unsaved changes.

        Returns:
            bool: True if there are unsaved changes, False otherwise.
        """
        return self.model.has_unsaved_changes()

    def toggle_comment(self):
        """
        Toggle comment status of the currently selected line.

        Returns:
            bool: True if the comment was toggled, False otherwise.
        """
        if self.model.current_selected_index >= 0:
            success = self.model.toggle_comment()
            if success:
                index = self.model.current_selected_index
                line = self.model.dcfg_file_content[index]
                validation_status = self.model.get_validation_status(index)

                list_model = self.view.get_model()
                list_model.updateLine(index, line)
                list_model.updateLineValidation(index, validation_status)

                if not line.startswith('#') and line.strip():
                    net_matches, template_matches = self.model.find_matches(line)
                    list_model.updateLineMatches(index, net_matches, template_matches)

                list_model.updateLineColor(list_model.getLine(index))
                self.view.select_line(self.model.current_selected_index)
                return True
        return False

    def duplicate_line(self):
        """
        Duplicate the currently selected line.

        Returns:
            bool: True if the line was duplicated, False otherwise.
        """
        if self.model.current_selected_index >= 0:
            index = self.model.current_selected_index
            selected_line_model = self.model.line_models[index]
            net_matches = selected_line_model.get_net_matches() or []
            template_matches = selected_line_model.get_template_matches() or []
            success = self.model.duplicate_line()
            if success:
                # Get the duplicated line
                line = self.model.dcfg_file_content[index + 1]
                validation_status = self.model.get_validation_status(index + 1)

                list_model = self.view.get_model()

                # net_matches, template_matches = [], []
                # if not line.startswith('#') and line.strip():
                    # net_matches, template_matches = self.model.find_matches(line)

                list_model.insertLine(index + 1, line, validation_status, net_matches, template_matches)

                self.update_line_colors_and_matches()
                self.view.select_line(self.model.current_selected_index)
                return True
        return False