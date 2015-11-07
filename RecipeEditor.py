from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal
from ui_yacc_main_window import Ui_yacc_main_window
from ui_recipe_builder_window import Ui_MainWindow
from Backend import Backend
import pdb

class RecipeEditor(QtGui.QMainWindow):
    signal_button_clicked = pyqtSignal(str)
    signal_exit = pyqtSignal(str)

    def __init__(self, parent=None, backend=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.be = backend

        self.ui.pushButton.clicked.connect(self.handle_click)

    def handle_click(self):
        text = self.ui.lineEdit.text()
        self.signal_button_clicked.emit(text)

    # override
    def closeEvent(self, event):
        text = self.ui.lineEdit.text()
        self.signal_exit.emit(text)
        event.accept()
