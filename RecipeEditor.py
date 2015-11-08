from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt4.QtGui import QTableWidgetItem, QColor, QMessageBox, QInputDialog
from ui_yacc_main_window import Ui_yacc_main_window
from ui_recipe_builder_window import Ui_MainWindow
from Backend import Backend
import pdb

class RecipeEditor(QtGui.QMainWindow):
    signal_exit = pyqtSignal(str)
    signal_backend_updated = pyqtSignal()

    def __init__(self, parent=None, backend=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.updating_internal = False
        self.recipes_to_commit = {}
        self.current_recipe = None

        # store backend from Main
        self.be = backend if backend is not None else Backend()

        # init recipe table
        self.ui.recipe_table.setColumnCount(2)
        self.ui.recipe_table.setRowCount(0)
        self.ui.recipe_table.setHorizontalHeaderLabels(['Flavor', 'Strength (%)'])

        # signals/slots
        self.ui.recipe_list.currentRowChanged.connect(self.handle_rlist_row_change)
        self.ui.recipe_table.cellChanged.connect(self.handle_rtable_cell_change)
        self.ui.revertrecipe_button.clicked.connect(self.handle_revert_click)
        self.ui.save_button.clicked.connect(self.handle_save_click)
        self.ui.update_button.clicked.connect(self.update_backend)

        self.ui.addrecipe_button.clicked.connect(self.handle_addrecipe_click)
        self.ui.delrecipe_button.clicked.connect(self.handle_delrecipe_click)
        self.ui.addflavor_button.clicked.connect(self.handle_addflavor_click)
        self.ui.delflavor_button.clicked.connect(self.handle_delflavor_click)

        # initialize recipe list
        for r in self.be.get_recipes():
            self.ui.recipe_list.addItem(r)
        self.ui.recipe_list.setCurrentRow(0)

    def load_recipe(self, recipe_name=None, create_new=False):
        if self.updating_internal or (recipe_name is None and not create_new):
            return
        self.updating_internal = True

        self.current_recipe = recipe_name if recipe_name is not None else 'New Recipe'

        if create_new:
            recipe = {'New Flavor 1':0}
            self.stage_recipe(recipe_name, recipe)
        elif recipe_name in self.recipes_to_commit:
            recipe = self.recipes_to_commit[recipe_name]
        else:
            recipe = self.be.get_recipe(recipe_name)
        
        self.ui.recipe_table.clearContents()
        self.ui.recipe_table.setRowCount(len(recipe))

        for (i, flavor) in enumerate(sorted(recipe)):
            self.ui.recipe_table.setItem(i, 0, QTableWidgetItem(flavor))
            self.ui.recipe_table.setItem(i, 1, QTableWidgetItem('%.1f'%(recipe[flavor]*100.0)))

        self.ui.recipe_table.resizeColumnToContents(0)
        self.updating_internal = False

    def update_backend(self):
        self.be.update_recipes(self.recipes_to_commit)
        
        # unstage all staged recipes
        for r in list(self.recipes_to_commit.keys()):
            self.unstage_recipe(r)

        self.signal_backend_updated.emit()

    def compile_current_recipe(self):
        recipe = {}
        nrows = self.ui.recipe_table.rowCount()
        for r in range(nrows):
            flavor = self.ui.recipe_table.item(r, 0).text()
            value =  float(self.ui.recipe_table.item(r, 1).text()) / 100.0
            recipe[flavor] = value

        return recipe

    def stage_recipe(self, recipe_name=None, recipe_data=None):
        #print('RecipeEditor.stage_recipe called')
        if recipe_name is None:
            recipe_name = self.current_recipe
        if recipe_data is None:
            self.recipes_to_commit[recipe_name] = self.compile_current_recipe()
        else:
            self.recipes_to_commit[recipe_name] = recipe_data

        regex = recipe_name + r"( \(\*\))?"
        rowmatches = self.ui.recipe_list.findItems(regex, Qt.MatchRegExp)
        #print('RecipeEditor.stage_recipe found %s'%str(rowmatches))
        if len(rowmatches) < 1:
            return
        rowmatches[0].setText(recipe_name + ' (*)')

    def unstage_recipe(self, recipe_name=None):
        #print('unstage_recipe called')
        if recipe_name is None:
            recipe_name = self.current_recipe
        try:
            self.recipes_to_commit.pop(recipe_name)
        except KeyError:
            pass

        item = self.get_recipe_item(recipe_name)
        name = self.recipe_name_staged(item.text())[0]
        item.setText(name)

    def recipe_name_staged(self, name=None):
        if name is None:
            # if None, get current selection
            name = self.ui.recipe_list.currentItem().text()

        if name.endswith(' (*)'):
            name = name[:-4]
            return name, True
        else:
            return name, False

    def get_recipe_row(self, recipe_name):
        regex = recipe_name + r"( \(\*\))?"
        rowmatches = self.ui.recipe_list.findItems(regex, Qt.MatchRegExp)
        if len(rowmatches) > 0:
            return self.ui.recipe_list.row(rowmatches[0])
        else:
            return None

    def get_recipe_item(self, recipe_name):
        row = self.get_recipe_row(recipe_name)
        if row is not None:
            return self.ui.recipe_list.item(row)
        else:
            return None

    @pyqtSlot(int)
    def handle_rlist_row_change(self, row):
        recipe_name = self.recipe_name_staged(self.ui.recipe_list.item(row).text())[0]
        self.load_recipe(recipe_name)

    @pyqtSlot(int, int)
    def handle_rtable_cell_change(self, row, col):
        if self.updating_internal:
            # bail if we're loading a recipe from backend
            return

        if col == 0:
            self.ui.recipe_table.resizeColumnToContents(0)
            return

        item = self.ui.recipe_table.item(row, col)
        value = item.text()
        try:
            nval = float(value)
            if nval < 0:
                raise ValueError

            # set updating_internal while doing this to prevent the color change from triggering
            # handle_rable_cell_change (well, it still gets triggered, but returns before doing anything)
            self.updating_internal = True
            item.setBackgroundColor(QColor(0xffffff))
            self.updating_internal = False
            self.stage_recipe()
        except ValueError:
            self.updating_internal = True
            item.setBackgroundColor(QColor(255, 102, 102))
            self.updating_internal = False
            self.unstage_recipe()

    @pyqtSlot(bool)
    def handle_revert_click(self):
        self.load_recipe(self.current_recipe)
        self.unstage_recipe()

    @pyqtSlot(bool)
    def handle_save_click(self):
        reply = QMessageBox.question(self, 'Confirm Save', 'Really write JSON data file?',
                QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.update_backend()
            self.be.write_file()

    @pyqtSlot(bool)
    def handle_addrecipe_click(self):
        (recipe_name, ok) = QInputDialog.getText(self, 'New Recipe', 'Enter Recipe Name:')
        if ok:
            self.current_recipe = recipe_name
            self.ui.recipe_list.addItem(recipe_name)
            
            #mutex this change
            self.updating_internal = True
            self.ui.recipe_list.setCurrentRow(self.get_recipe_row(recipe_name))
            self.updating_internal = False

            self.load_recipe(recipe_name, create_new=True)

    @pyqtSlot(bool)
    def handle_delrecipe_click(self):
        recipe_name = self.recipe_name_staged()[0]
        reply = QMessageBox.question(self, 'Delete Recipe?', 'Really Delete the recipe "%s"?'%recipe_name,
                QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            pass

    @pyqtSlot(bool)
    def handle_addflavor_click(self):
        pass

    @pyqtSlot(bool)
    def handle_delflavor_click(self):
        pass

    # override
    def closeEvent(self, event):
        self.signal_exit.emit('')
        event.accept()
