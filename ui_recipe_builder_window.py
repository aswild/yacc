# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'recipe_builder_window.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(707, 344)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.recipe_list = QtGui.QListWidget(self.centralwidget)
        self.recipe_list.setUniformItemSizes(True)
        self.recipe_list.setObjectName(_fromUtf8("recipe_list"))
        self.verticalLayout.addWidget(self.recipe_list)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.addrecipe_button = QtGui.QPushButton(self.centralwidget)
        self.addrecipe_button.setObjectName(_fromUtf8("addrecipe_button"))
        self.horizontalLayout.addWidget(self.addrecipe_button)
        self.delrecipe_button = QtGui.QPushButton(self.centralwidget)
        self.delrecipe_button.setObjectName(_fromUtf8("delrecipe_button"))
        self.horizontalLayout.addWidget(self.delrecipe_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.save_button = QtGui.QPushButton(self.centralwidget)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.horizontalLayout_2.addWidget(self.save_button)
        self.update_button = QtGui.QPushButton(self.centralwidget)
        self.update_button.setObjectName(_fromUtf8("update_button"))
        self.horizontalLayout_2.addWidget(self.update_button)
        self.autosave_checkbox = QtGui.QCheckBox(self.centralwidget)
        self.autosave_checkbox.setObjectName(_fromUtf8("autosave_checkbox"))
        self.horizontalLayout_2.addWidget(self.autosave_checkbox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.recipe_table = QtGui.QTableWidget(self.centralwidget)
        self.recipe_table.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.recipe_table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.recipe_table.setObjectName(_fromUtf8("recipe_table"))
        self.recipe_table.setColumnCount(0)
        self.recipe_table.setRowCount(1)
        item = QtGui.QTableWidgetItem()
        self.recipe_table.setVerticalHeaderItem(0, item)
        self.recipe_table.horizontalHeader().setVisible(True)
        self.recipe_table.horizontalHeader().setStretchLastSection(True)
        self.recipe_table.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.recipe_table)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.addflavor_button = QtGui.QPushButton(self.centralwidget)
        self.addflavor_button.setObjectName(_fromUtf8("addflavor_button"))
        self.horizontalLayout_3.addWidget(self.addflavor_button)
        self.delflavor_button = QtGui.QPushButton(self.centralwidget)
        self.delflavor_button.setObjectName(_fromUtf8("delflavor_button"))
        self.horizontalLayout_3.addWidget(self.delflavor_button)
        self.revertrecipe_button = QtGui.QPushButton(self.centralwidget)
        self.revertrecipe_button.setObjectName(_fromUtf8("revertrecipe_button"))
        self.horizontalLayout_3.addWidget(self.revertrecipe_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "YACC Redipe Editor", None))
        self.label.setText(_translate("MainWindow", "Select Recipe:", None))
        self.addrecipe_button.setText(_translate("MainWindow", "Add Recipe", None))
        self.delrecipe_button.setText(_translate("MainWindow", "Delete Recipe", None))
        self.save_button.setText(_translate("MainWindow", "Save", None))
        self.update_button.setText(_translate("MainWindow", "Update", None))
        self.autosave_checkbox.setText(_translate("MainWindow", "Auto-Update", None))
        self.addflavor_button.setText(_translate("MainWindow", "Add Flavor", None))
        self.delflavor_button.setText(_translate("MainWindow", "Delete Flavor", None))
        self.revertrecipe_button.setText(_translate("MainWindow", "Revert Recipe", None))

