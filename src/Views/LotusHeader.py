import os

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit
import os

class LotusHeader(QWidget):
    def __init__(self, filepath):
        super().__init__()
        # Main layout
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)  # Remove outer margins
        self._layout.setSpacing(0)
        self._work_area = os.environ['LOTUS_ROOT_DIR']
        self._filepath = os.path.realpath(filepath)

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
        work_area_widget_layout.addWidget(QLabel("Work Area:"))
        self.work_area_line_edit = QLineEdit(self._work_area)
        self.work_area_line_edit.setReadOnly(True)
        work_area_widget_layout.addWidget(self.work_area_line_edit)
        work_area_widget.setLayout(work_area_widget_layout)
        self._layout.addWidget(work_area_widget)
        
        # Filepath Widget
        filepath_widget = QWidget()
        filepath_widget_layout = QHBoxLayout()
        filepath_widget_layout.addWidget(QLabel("File:"))
        self.filepath_line_edit = QLineEdit(self._filepath)
        self.filepath_line_edit.setReadOnly(True)
        filepath_widget_layout.addWidget(self.filepath_line_edit)
        filepath_widget.setLayout(filepath_widget_layout)
        self._layout.addWidget(filepath_widget)

        self.setLayout(self._layout)

    def change_filepath(self, filepath):
        self._filepath = os.path.realpath(filepath)
        self.filepath_line_edit.setText(self._filepath)
        self.update()
