from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor
from models.af_line_model import AfLineModel


class AfLineListModel(QAbstractListModel):
    """
    A custom Qt list model for managing AF line models in document views.

    This class extends QAbstractListModel to provide a model-view representation
    of lines in the document, handling validation status, color highlighting,
    and match information for each line.  
    It serves as the data provider for document list views in the application.

    Attributes:
        DisplayRole (int): Role for displaying line text
        ColorRole (int): Role for line highlighting color
        ValidationRole (int): Role for line validation status
        NetMatchesRole (int): Role for net matches information
        TemplateMatchesRole (int): Role for template matches information
        lines (list): List of AfLineModel objects representing document lines
        INVALID_COLOR (QColor): Color for invalid lines (red)
        NO_MATCHES_COLOR (QColor): Color for lines with no matches (orange)
        COMMENT_COLOR (QColor): Color for comment lines (grey)
        VALID (int): Constant for valid line status
        INVALID (int): Constant for invalid line status
        WARNING (int): Constant for warning line status
        COMMENT (int): Constant for comment line status
    """

    # Define custom roles for our model
    DisplayRole = Qt.DisplayRole
    ColorRole = Qt.UserRole
    ValidationRole = Qt.UserRole + 1
    NetMatchesRole = Qt.UserRole + 2
    TemplateMatchesRole = Qt.UserRole + 3

    def __init__(self, parent=None):
        """
        Initialize the AF Line List Model.

        Args:
            parent (QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(parent)
        self.lines = []  # List of AfLineModel objects

        # Color constants
        self.INVALID_COLOR = QColor(255, 0, 0)  # Red for invalid lines
        self.NO_MATCHES_COLOR = QColor(255, 100, 0)  # Orange for lines with no matches
        self.COMMENT_COLOR = QColor(150, 150, 150)  # Grey for comment lines

        # Constants for validation status
        self.VALID = 0
        self.INVALID = 1
        self.WARNING = 2
        self.COMMENT = 3

    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of rows in the model.

        Args:
            parent (QModelIndex, optional): Parent index. Defaults to QModelIndex().

        Returns:
            int: Number of lines in the model
        """
        return len(self.lines)

    def data(self, index, role=Qt.DisplayRole):
        """
        Return data for the specified index and role.

        Args:
            index (QModelIndex): Index of the item
            role (int, optional): Data role to return. Defaults to Qt.DisplayRole.

        Returns:
            QVariant: The requested data or QVariant() if the index is invalid
        """
        if not index.isValid() or index.row() >= len(self.lines):
            return QVariant()

        line = self.lines[index.row()]

        if role == Qt.DisplayRole:
            return line.get_line()
        elif role == self.ColorRole:
            return line.get_color()
        elif role == self.ValidationRole:
            return line.get_status()
        elif role == self.NetMatchesRole:
            return line.get_net_matches()
        elif role == self.TemplateMatchesRole:
            return line.get_template_matches()

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        """
        Set data for the specified index and role.

        Args:
            index (QModelIndex): Index of the item to modify
            value: Value to set
            role (int, optional): Data role to set. Defaults to Qt.EditRole.

        Returns:
            bool: True if the data was successfully set, False otherwise
        """
        if not index.isValid() or index.row() >= len(self.lines):
            return False

        line = self.lines[index.row()]

        if role == Qt.EditRole:
            # Create a new AfLineModel with the updated text
            new_line = AfLineModel(value)
            self.lines[index.row()] = new_line
            # Emit data changed signal
            self.dataChanged.emit(index, index)
            return True

        elif role == self.ColorRole:
            # Set the color for the line
            line.set_color(value)
            self.dataChanged.emit(index, index)
            return True

        elif role == self.ValidationRole:
            # Set the validation status for the line
            line.set_status(value)
            self.dataChanged.emit(index, index)
            return True

        elif role == self.NetMatchesRole:
            line.set_net_matches(value)
            self.dataChanged.emit(index, index)
            return True

        elif role == self.TemplateMatchesRole:
            line.set_template_matches(value)
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        """
        Return item flags for the given index.

        Args:
            index (QModelIndex): Index of the item

        Returns:
            Qt.ItemFlags: Flags for the item
        """
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def insertLine(self, position, line_text, validation_status=None, net_matches=None, template_matches=None):
        """
        Insert a new line at the specified position.

        Creates a new AfLineModel with the given text and attributes,
        and inserts it into the model at the specified position.

        Args:
            position (int): Position to insert the line
            line_text (str): Text content of the line
            validation_status (int, optional): Validation status for the line. Defaults to None.
            net_matches (list, optional): Net matches for the line. Defaults to None.
            template_matches (list, optional): Template matches for the line. Defaults to None.

        Returns:
            bool: True if the line was successfully inserted, False otherwise
        """
        if position < 0 or position > len(self.lines):
            position = len(self.lines)

        # Create a new AfLineModel for this line
        line_model = AfLineModel(line_text)

        if validation_status is not None:
            line_model.set_status(validation_status)

        if net_matches is not None:
            line_model.set_net_matches(net_matches)

        if template_matches is not None:
            line_model.set_template_matches(template_matches)

        # Set the color based on validation status and match count
        self.updateLineColor(line_model)

        # Insert into the model
        self.beginInsertRows(QModelIndex(), position, position)
        self.lines.insert(position, line_model)
        self.endInsertRows()

        return True

    def appendLine(self, line_text, validation_status=None, net_matches=None, template_matches=None):
        """
        Add a new line to the **end** of the model.

        Args:
            line_text (str): Text content of the line
            validation_status (int, optional): Validation status for the line. Defaults to None.
            net_matches (list, optional): Net matches for the line. Defaults to None.
            template_matches (list, optional): Template matches for the line. Defaults to None.

        Returns:
            bool: True if the line was successfully appended, False otherwise
        """
        return self.insertLine(len(self.lines), line_text, validation_status, net_matches, template_matches)

    def removeLine(self, position):
        """
        Remove the line at the specified position.

        Args:
            position (int): Position of the line to remove

        Returns:
            bool: True if the line was successfully removed, False otherwise
        """
        if position < 0 or position >= len(self.lines):
            return False

        self.beginRemoveRows(QModelIndex(), position, position)
        del self.lines[position]
        self.endRemoveRows()

        return True

    def updateLine(self, position, line_text):
        """
        Update an existing line at the specified position.

        Creates a new AfLineModel with the updated text.

        Args:
            position (int): Position of the line to update
            line_text (str): New text content for the line

        Returns:
            bool: True if the line was successfully updated, False otherwise
        """
        if position < 0 or position >= len(self.lines):
            return False

        # Create new AfLineModel with updated text
        old_line = self.lines[position]
        new_line = AfLineModel(line_text)

        # Replace in the model
        self.lines[position] = new_line

        # Emit data changed signal
        index = self.index(position)
        self.dataChanged.emit(index, index)

        return True

    def getLine(self, position):
        """
        Get the AfLineModel at the specified position.

        Args:
            position (int): Position of the line to get

        Returns:
            AfLineModel: The line model at the specified position, or None if invalid
        """
        if position < 0 or position >= len(self.lines):
            return None

        return self.lines[position]

    def setContentFromStringList(self, string_list):
        """
        Replace all content with lines from a string list.

        Args:
            string_list (list): List of strings to set as content
        """
        self.beginResetModel()
        self.lines = [AfLineModel(line) for line in string_list]
        self.endResetModel()

    def updateLineMatches(self, position, net_matches, template_matches):
        """
        Update the matches for a line at the specified position.

        Args:
            position (int): Position of the line to update
            net_matches (list): New net matches for the line
            template_matches (list): New template matches for the line

        Returns:
            bool: True if the line matches were successfully updated, False otherwise
        """
        if position < 0 or position >= len(self.lines):
            return False

        line = self.lines[position]
        line.set_net_matches(net_matches)
        line.set_template_matches(template_matches)

        # Emit data changed signal
        index = self.index(position)
        self.dataChanged.emit(index, index)

        return True

    def updateLineValidation(self, position, validation_status):
        """
        Update the validation status for a line at the specified position.

        Args:
            position (int): Position of the line to update
            validation_status (int): New validation status for the line

        Returns:
            bool: True if the validation status was successfully updated, False otherwise
        """
        if position < 0 or position >= len(self.lines):
            return False

        line = self.lines[position]
        line.set_status(validation_status)

        # Emit data changed signal
        index = self.index(position)
        self.dataChanged.emit(index, index)

        return True

    def updateLineColor(self, line_model):
        """
        Update the color of a line based on its validation status and match count.

        This method determines the appropriate color for a line based on its
        validation status, comment status, and match information.

        Args:
            line_model (AfLineModel): The line model to update the color for
        """
        line = line_model.get_line()
        status = line_model.get_status()

        if not line.strip():
            line_model.set_color(None)
            return

        if line.startswith('#'):
            line_model.set_color(self.COMMENT_COLOR)
            return

        if status == self.COMMENT and not line.startswith('#'):
            # The line was previously a comment but now isn't - reset status
            status = self.VALID

        if status == self.INVALID:
            line_model.set_color(self.INVALID_COLOR)
        else:
            net_matches = line_model.get_net_matches()
            # Only set NO_MATCHES_COLOR if we know for sure this line has no matches
            # (net_matches is not None means matches were already searched for)
            if net_matches is not None and len(net_matches) == 0:
                line_model.set_color(self.NO_MATCHES_COLOR)
            else:
                # If matches haven't been checked yet, or it has matches, don't color it orange
                if net_matches is not None and len(net_matches) > 0:
                    # Line has matches, clear any NO_MATCHES_COLOR if it was set previously
                    current_color = line_model.get_color()
                    if current_color == self.NO_MATCHES_COLOR:
                        line_model.set_color(None)  # Reset to default color

    def updateAllColors(self):
        """
        Update colors for all lines in the model.

        Iterates through all lines and updates their colors based on
        their current validation status and match information.
        """
        for i, line in enumerate(self.lines):
            old_color = line.get_color()
            self.updateLineColor(line)

            # Only emit data changed if color actually changed
            if old_color != line.get_color():
                index = self.index(i)
                self.dataChanged.emit(index, index)

    def getStringList(self):
        """
        Get all lines as a string list.

        Returns:
            list: List of strings representing all lines in the model
        """
        return [line.get_line() for line in self.lines]