from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel


class CommentTabView(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        self.layout = QVBoxLayout()
        # Comment label
        self.layout.addWidget(QLabel("Comment:"))
        # Comment input line with prefix
        comment_line = QWidget()
        comment_line_layout = QHBoxLayout()
        comment_line_layout.setContentsMargins(0, 0, 0, 0)
        comment_line_layout.addWidget(QLabel("#"))

        self.comment_line_edit = QLineEdit()
        self.comment_line_edit.setPlaceholderText("Write comment here")
        comment_line_layout.addWidget(self.comment_line_edit)

        comment_line.setLayout(comment_line_layout)
        self.layout.addWidget(comment_line)

        self.layout.setSpacing(5)
        self.setLayout(self.layout)
