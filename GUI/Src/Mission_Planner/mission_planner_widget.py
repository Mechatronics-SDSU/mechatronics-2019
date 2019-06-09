import os
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QDir, QUrl, pyqtSlot, QObject, QJsonValue
from PyQt5.QtGui import QColor

class Mission_Planner(QWidget):
    '''
        This class is PyQt widget for toggeling sub kill status.
    
        Parameter:
        N/A
        
        Returns:
        N/A
    '''
    def __init__(self):
        '''
            Initialize the layout for the widget by setting its color and instantiating
            its components.
            
            Parameter:
            N/A
            
            Returns:
            N/A
        '''
        QWidget.__init__(self)
        
        #Create widgets main layout
        self.layout = QGridLayout(self)

        #Create page and connect QWebChannel
        self.view = QWebEngineView(self)
        self.url = QUrl.fromLocalFile(os.path.abspath('Mission_Planner/mission_planner.html'))
        channel = QWebChannel(self.view.page())
        self.view.page().setWebChannel(channel)
        channel.registerObject("Mission_Planner", self)
        self.view.load(self.url)

        self.layout.addWidget(self.view)
        self.setLayout(self.layout)  

    @pyqtSlot(QJsonValue)
    def send_json(self, json):
        print(json.toString())


if __name__ == "__main__":
    import sys
    app = QApplication([])
    mission_planner_test_gui = Mission_Planner()
    optimal_size = mission_planner_test_gui.sizeHint()
    mission_planner_test_gui.setMaximumSize(optimal_size)
    mission_planner_test_gui.show()
    sys.exit(app.exec_())   