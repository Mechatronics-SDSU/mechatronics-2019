import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout
from PyQt5.QtGui import QIcon, QColor, QPalette
from PyQt5.QtCore import pyqtSlot, Qt, Signal
from nav_odometery_widget import Navigation_GUI
from pid_tuner_widget import PID_Tuner_Widget


class Tabbed_Display(QWidget):

    def __init__(self, parent):
        '''
        Initializes a Tabbed Display widget.

        Parameters:
            parent: The parent Qwidget
        '''
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)

        # Set the background color of the widget
        tabbed_display_palette = self.palette()
        tabbed_display_palette.setColor(self.backgroundRole(), QColor(64, 64, 64))
        self.setPalette(tabbed_display_palette)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.setFixedSize(700, 700)

        # Set color of QTabWidget
        tabs_palette = self.tabs.palette()
        tabs_palette.setColor(QPalette.Window, QColor(64, 64, 64))
        self.tabs.setPalette(tabs_palette)

        # Add tabs to layout
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Call method _update_mode() when tab is changed
        self.tabs.currentChanged.connect(self._update_mode)

    def add_tab(self, widget, title):
        '''
        Creates a new tab and adds a Qwidget to it.

        Parameters:
            widget: The Qwidget to be displayed.
            title: (string) The title of the Tab

        Returns:
            N/A
        '''
        # Init parent widget
        parent = QWidget()
        layout = QVBoxLayout(parent)

        # Set color
        background = parent.palette()
        background.setColor(QPalette.Window, QColor(64, 64, 64))
        parent.setPalette(background)
        parent.setAutoFillBackground(True)

        # Add widget to parent
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(widget)
        parent.setLayout(layout)

        # Add parent to tab
        self.tabs.addTab(parent, title)
        widget.setEnabled(True)
        widget.setAutoFillBackground(True)

    def _update_mode(self):
        '''
        Publishes the current tab index.

        Parameters:
            N/A

        Returns:
            N/A
        '''
        # Get current index
        mode = self.tabs.currentIndex()
        print(mode)

        # Publish current index
        self.parent.movement_mode_pub.publish(bytes(mode))


if __name__ == "__main__":
    import sys
    app = QApplication([])
    tabbed_display = Tabbed_Display()
    tabbed_display.show()
    sys.exit(app.exec_())
