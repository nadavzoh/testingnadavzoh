from PyQt5.QtCore import QObject, pyqtSignal
class AfDialogController(QObject):
    dialog_accepted = pyqtSignal(str)
    dialog_cancelled = pyqtSignal()

    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        self.edit_mode = False
        self.unfiltered_net_matches = []
        self.unfiltered_template_matches = []

        self.toggle_tab_editable(False)  # default is not editable
        self.view.main_tab.netChanged.connect(self.on_net_changed)
        self.view.main_tab.templateChanged.connect(self.on_template_changed)
        self.view.main_tab.afChanged.connect(self.on_af_changed)
        self.view.main_tab.emToggled.connect(self.on_em_toggled)
        self.view.main_tab.shToggled.connect(self.on_sh_toggled)

        self.view.main_tab.netsSearchChanged.connect(lambda search_text: self.on_net_search_changed(search_text))
        self.view.main_tab.templatesSearchChanged.connect(lambda search_text: self.on_template_search_changed(search_text))

        self.view.reset_button.clicked.connect(self._on_clear_dialog_requested)
        self.view.cancel_button.clicked.connect(lambda: self._on_cancel_dialog())
        self.view.save_line_button.clicked.connect(self._on_save_line_requested)

    def get_active_tab(self):
        return self.view.tabs.currentIndex()


    def on_net_search_changed(self, search_text):
        if not search_text:
            filtered_matches = self.unfiltered_net_matches
            if self.edit_mode:
                self.view.save_line_button.setEnabled(True)
        else:
            filtered_matches = [match for match in self.unfiltered_net_matches
                                if search_text.lower() in match.lower()]
            if self.edit_mode:
                self.view.save_line_button.setEnabled(False)
        self.view.main_tab.net_matches_list_model.setStringList(filtered_matches)

    def on_template_search_changed(self, search_text):
        if not search_text:
            filtered_matches = self.unfiltered_template_matches
            if self.edit_mode:
                self.view.save_line_button.setEnabled(True)
        else:
            filtered_matches = [match for match in self.unfiltered_template_matches
                                if search_text.lower() in match.lower()]
            if self.edit_mode:
                self.view.save_line_button.setEnabled(False)
        self.view.main_tab.template_matches_list_model.setStringList(filtered_matches)

    def change_tab(self, tab_name: str):
        if tab_name.upper() == "AF":
            self.view.tabs.setCurrentIndex(0)
        elif tab_name.upper() == "COMMENT":
            self.view.tabs.setCurrentIndex(1)

    def toggle_tab_editable(self, editable: bool):
        self.view.comment_tab.comment_line_edit.setEnabled(editable)

        self.view.main_tab.net_edit.setEnabled(editable)
        self.view.main_tab.net_enable_regex.setEnabled(editable)
        self.view.main_tab.template_edit.setEnabled(editable)
        self.view.main_tab.template_enable_regex.setEnabled(editable)
        self.view.main_tab.af_edit.setEnabled(editable)
        self.view.main_tab.em_checkbox.setEnabled(editable)
        self.view.main_tab.sh_checkbox.setEnabled(editable)

        self.view.save_line_button.setEnabled(editable)
        self.view.cancel_button.setEnabled(editable)

    def _on_cancel_dialog(self):
        self.dialog_cancelled.emit()
        self.toggle_tab_editable(False)

    def fill_dialog_with_line(self, line):  # TODO: REFRACTOR
        if line.startswith("#"):
            self.change_tab("COMMENT")
            self.view.comment_tab.comment_line_edit.setText(line.strip("#").strip())
            return
        # else - AF tab
        self.change_tab("AF")
        try:
            fields = self.model.get_fields_from_line(line)
        except ValueError as e:
            self.view.main_tab.show_error("Invalid line format", str(e))
            return
        self.view.main_tab.template_edit.setText(fields.get("template", ""))
        self.view.main_tab.template_enable_regex.setChecked(fields.get("template_regex", False))
        self.view.main_tab.net_edit.setText(fields.get("net", ""))
        self.view.main_tab.net_enable_regex.setChecked(fields.get("net_regex", False))
        self.view.main_tab.af_edit.setText(fields.get("af", ""))
        self.view.main_tab.em_checkbox.setChecked(fields.get("em", False))
        self.view.main_tab.sh_checkbox.setChecked(fields.get("sh", False))
        self.display_matches_preview()

    def _on_save_line_requested(self):
        if self.get_active_tab() == 0:
            try:
                if self.model.validate_input():
                    self.dialog_accepted.emit(self.view.main_tab.line_preview.text())
            except ValueError as e:
                self.view.main_tab.show_error("Validation Error", str(e))
                return
        elif self.get_active_tab() == 1:
            self.dialog_accepted.emit(f"# {self.view.comment_tab.comment_line_edit.toPlainText()}")
        self.dialog_cancelled.emit()
        self.toggle_tab_editable(False)

    def on_net_changed(self, net, use_regex):
        self.model.net = net
        self.model.net_regex = use_regex
        self.display_matches_preview()
        self.update_line_preview()

    def on_template_changed(self, template, use_regex):
        self.model.template = template
        self.model.template_regex = use_regex
        self.display_matches_preview()
        self.update_line_preview()

    def on_af_changed(self, af_text):
        self.model.activity_factor = af_text
        self.update_line_preview()

    def on_em_toggled(self, enabled):
        self.model.em_enabled = enabled
        self.update_line_preview()

    def on_sh_toggled(self, enabled):
        self.model.sh_enabled = enabled
        self.update_line_preview()

    def display_matches_preview(self):
        try:
            net_matches, template_matches = self.model.find_matches()
            self.unfiltered_net_matches = net_matches
            self.unfiltered_template_matches = template_matches
            if net_matches:
                self.view.main_tab.update_results_preview("\n".join(net_matches), "\n".join(template_matches))
            else:
                self.view.main_tab.update_results_preview("No matches found.", "")
        except ValueError as e:
            self.view.main_tab.update_results_preview(str(e), str(e))

    def update_line_preview(self):
        line = self.model.format_line()
        self.view.main_tab.line_preview.setText(line)

    def _on_clear_dialog_requested(self):
        # TODO: clear search fields
        if self.view.tabs.currentIndex() == 0:
            self.view.main_tab.net_edit.clear()
            self.view.main_tab.net_enable_regex.setChecked(False)
            self.view.main_tab.template_edit.clear()
            self.view.main_tab.template_enable_regex.setChecked(False)
            self.view.main_tab.af_edit.clear()
            self.view.main_tab.em_checkbox.setChecked(False)
            self.view.main_tab.sh_checkbox.setChecked(False)
            self.view.main_tab.update_results_preview("", "")
        if self.view.tabs.currentIndex() == 1:
            self.view.comment_tab.comment_line_edit.clear()

    def set_edit_mode(self, is_edit: bool):
        self.edit_mode = is_edit