from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QTimer


class LazyLoadingListModel(QAbstractListModel):
    """
    A list model that efficiently handles very large datasets through lazy loading.

    This implementation uses Qt's fetchMore/canFetchMore mechanism for true lazy loading,
    only loading items when they're about to be displayed. This approach significantly
    reduces memory usage and improves application responsiveness when dealing with
    large datasets that would otherwise cause performance issues.

    Attributes:
        _data_provider (callable): Function that provides data chunks
        _total_item_count (int): Total number of items available in the dataset
        _loaded_items (list): Items that have been loaded so far
        _chunk_size (int): Number of items to fetch at once
    """

    def __init__(self, data_provider=None, parent=None):
        """
        Initialize the model with a data provider function.

        Args:
            data_provider (callable, optional): A function that takes (start_index, count)
                parameters and returns a list of items to display. If None, an empty list is used.
            parent (QObject, optional): The parent object for Qt's object hierarchy.
        """
        super().__init__(parent)
        self._data_provider = data_provider or (lambda start, count: [])
        self._total_item_count = 0  # Total number of items available
        self._loaded_items = []  # Items loaded so far
        self._chunk_size = 100  # Number of items to fetch at once

    def rowCount(self, parent=QModelIndex()):
        """
        Return the number of rows in the model that are currently loaded.

        Args:
            parent (QModelIndex, optional): The parent index. Always invalid for list models.

        Returns:
            int: The number of loaded items
        """
        return len(self._loaded_items)

    def data(self, index, role=Qt.DisplayRole):
        """
        Return data for the specified index and role.

        Args:
            index (QModelIndex): The index to retrieve data for
            role (int, optional): The role for which to retrieve data

        Returns:
            object: The data for the specified index and role, or None if invalid
        """
        if not index.isValid() or index.row() >= len(self._loaded_items):
            return None

        if role == Qt.DisplayRole:
            row = index.row()
            return self._loaded_items[row]

        return None

    def canFetchMore(self, parent=QModelIndex()):
        """
        Check if more data is available to fetch.

        Called by the view to determine if it should call fetchMore().

        Args:
            parent (QModelIndex, optional): The parent index. Always invalid for list models.

        Returns:
            bool: True if there is more data to fetch, False otherwise
        """
        if parent.isValid():
            return False

        has_more = len(self._loaded_items) < self._total_item_count
        return has_more

    def fetchMore(self, parent=QModelIndex()):
        """
        Fetch more items from the data provider when needed.

        This is called by the view when it needs more items to display, typically
        when the user scrolls down to see more items.

        Args:
            parent (QModelIndex, optional): The parent index. Always invalid for list models.
        """
        if parent.isValid():
            return

        start = len(self._loaded_items)
        remaining = self._total_item_count - start
        items_to_fetch = min(self._chunk_size, remaining)

        if items_to_fetch <= 0:
            return

        # Signal that we're about to insert rows
        self.beginInsertRows(QModelIndex(), start, start + items_to_fetch - 1)

        # Fetch the data
        new_items = self._data_provider(start, items_to_fetch)

        # Add the new items to our loaded items
        self._loaded_items.extend(new_items)

        # Signal that we've finished inserting rows
        self.endInsertRows()

    def setItemCount(self, count):
        """
        Set the total number of items available from the data provider.

        This resets the model's internal state to prepare for a new dataset.

        Args:
            count (int): The total number of items available.
        """
        if count == self._total_item_count:
            return

        self.beginResetModel()
        self._total_item_count = count
        self._loaded_items = []  # Clear all loaded items
        self.endResetModel()

    def setDataProvider(self, provider):
        """
        Set a new data provider function.

        This resets the model's internal state to prepare for a new data source.

        Args:
            provider (callable): A function that takes (start_index, count) parameters
                and returns a list of items to display.
        """

        self.beginResetModel()
        self._data_provider = provider
        self._loaded_items = []  # Clear all loaded items
        self.endResetModel()

    def setChunkSize(self, size):
        """
        Set the chunk size for fetching data.

        Adjusting the chunk size allows tuning the performance based on the dataset and
        available memory. Larger chunk sizes reduce the number of fetches but use more memory.

        Args:
            size (int): The number of items to fetch in each chunk
        """
        self._chunk_size = size


    def load_all_at_once(self):
        """
        Force loading of all items at once.

        This is useful for operations that need access to all items,
        such as searching or filtering.

        Warning:
            This defeats the purpose of lazy loading and should be
            used with caution for very large datasets as it may cause
            memory and performance issues.
        """

        if len(self._loaded_items) >= self._total_item_count:
            return

        self.beginResetModel()
        self._loaded_items = self._data_provider(0, self._total_item_count)
        self.endResetModel()