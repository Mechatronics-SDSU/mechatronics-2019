import os
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QDir, QUrl, pyqtSlot, QObject, QJsonValue
from PyQt5.QtGui import QColor

class Mission_Planner(QWidget):
    '''
        This class is the PyQt widget editing mission order and params, and sending those through MechOS.
    
        Parameter:
        N/A
        
        Returns:
        N/A
    '''
    def __init__(self, file_path='Mission_Planner/mission_planner.html'):
        '''
            Initialize the layout for the widget by setting its color and instantiating
            its components. Set up the QWebEngine and QWebChannel for dispalying JS and
            passing a callback function.
            
            Parameter:
                file_path: path to the html file
            
            Returns:
            N/A
        '''
        QWidget.__init__(self)
        
        #Create widgets main layout
        self.layout = QGridLayout(self)

        #Create page and connect QWebChannel
        self.view = QWebEngineView(self)
        self.url = QUrl.fromLocalFile(os.path.abspath(file_path))
        channel = QWebChannel(self.view.page())
        self.view.page().setWebChannel(channel)
        channel.registerObject("Mission_Planner", self)
        self.view.load(self.url)

        #Add to layout
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)  

    @pyqtSlot(QJsonValue)
    def send_json(self, json):
        '''
            Callback function that can be called from the JS script, will pass
            on a JSON value to MechOS
            
            Parameter:
                json: a QJsonValue to be sent to MechOS
            
            Returns:
            N/A
        '''
        print(json.toString())


if __name__ == "__main__":
    import sys
    app = QApplication([])
    mission_planner_test_gui = Mission_Planner('mission_planner.html')
    optimal_size = mission_planner_test_gui.sizeHint()
    mission_planner_test_gui.setMaximumSize(optimal_size)
    mission_planner_test_gui.show()
    sys.exit(app.exec_())   