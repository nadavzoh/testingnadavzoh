
# think about how it interacts with the LotusUIManager.

class LotusTabManager:
    """
    This class manages the tabs in the Lotus application.
    It handles adding and removing tabs, as well as managing their content.
    Also - it will handle the tab order, visibility and signal connections between the
    currently active left panel tab and the right panel.
    """

    def __init__(self):
        """
        Initializes the LotusTabManager.
        """
        pass

    def add_tab(self, tab_name):
        """
        Adds a new tab to the application.

        :param tab_name: The name of the tab to add.
        """
        pass

    def remove_tab(self, tab_name):
        """
        Removes a tab from the application.

        :param tab_name: The name of the tab to remove.
        """
        pass

    def set_tab_order(self, tab_order):
        """
        Sets the order of the tabs in the application.

        :param tab_order: A list of tab names in the desired order.
        """
        pass

    def set_tab_visibility(self, tab_name, visible):
        """
        Sets the visibility of a tab in the application.

        :param tab_name: The name of the tab to set visibility for.
        :param visible: True to show the tab, False to hide it.
        """
        pass

    def connect_signals(self, signal, slot):
        """
        Connects a signal to a slot for the currently active tab.

        :param signal: The signal to connect.
        :param slot: The slot to connect the signal to.
        """
        pass

    def disconnect_signals(self, signal, slot):
        """
        Disconnects a signal from a slot for the currently active tab.

        :param signal: The signal to disconnect.
        :param slot: The slot to disconnect the signal from.
        """
        pass

    def update_tab_content(self, tab_name, content):
        """
        Updates the content of a tab in the application.

        :param tab_name: The name of the tab to update.
        :param content: The new content for the tab.
        """
        pass