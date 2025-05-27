import os
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit


class LotusHeader(QWidget):
    """
    A widget that displays header information about the Lotus environment.

    Displays three read-only fields:
    - FUB: The functional unit block from LOTUS_FUB environment variable
    - WA: The working area from LOTUS_USER_WARD environment variable
    - File: The current file being edited (settable via change_filepath method)

    This provides context to the user about which environment and file they're working with.
    """

    def __init__(self):
        """Initialize the header widget with information from environment variables."""
        super().__init__()

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # FUB Widget
        fub_widget = QWidget()
        fub_widget_layout = QHBoxLayout()
        fub_widget_layout.addWidget(QLabel("FUB:"))
        self.fub_widget_line_edit = QLineEdit(os.environ['LOTUS_FUB'])
        self.fub_widget_line_edit.setReadOnly(True)
        fub_widget_layout.addWidget(self.fub_widget_line_edit)
        fub_widget.setLayout(fub_widget_layout)
        self._layout.addWidget(fub_widget)

        # Work Area Label
        work_area_widget = QWidget()
        work_area_widget_layout = QHBoxLayout()
        work_area_widget_layout.addWidget(QLabel("WA:"))
        self.work_area_line_edit = QLineEdit(os.environ['LOTUS_USER_WARD'])
        self.work_area_line_edit.setReadOnly(True)
        work_area_widget_layout.addWidget(self.work_area_line_edit)
        work_area_widget.setLayout(work_area_widget_layout)
        self._layout.addWidget(work_area_widget)

        # Filepath Widget
        filepath_widget = QWidget()
        filepath_widget_layout = QHBoxLayout()
        filepath_widget_layout.addWidget(QLabel("File:"))
        self.filepath_line_edit = QLineEdit()
        self.filepath_line_edit.setReadOnly(True)
        filepath_widget_layout.addWidget(self.filepath_line_edit)
        filepath_widget.setLayout(filepath_widget_layout)
        self._layout.addWidget(filepath_widget)

        self.setLayout(self._layout)

    def change_filepath(self, filepath):
        """
        Update the displayed file path.

        Args:
            filepath (str): The path to the currently active file
        """
        self.filepath_line_edit.setText(filepath)
