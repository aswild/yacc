from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt4.QtGui import QTableWidgetItem, QListWidgetItem, QColor, QMessageBox, QInputDialog
from ui_yacc_main_window import Ui_yacc_main_window
from ui_recipe_builder_window import Ui_MainWindow
from Backend import Backend
import pdb

# role constants for YQListWidgetItem
RECIPE_ITEM_NAME   = 33
RECIPE_ITEM_STAGED = 34
RECIPE_ITEM_DATA   = 35

class RecipeItem(QListWidgetItem):
    """ Child class of QListWidgetItem, so that I can store the recipe name and staged status
    directly in RecipeEditor.recipe_list_items
    I'm also just gonna use these instance variables directly without dealing with roles and the data()
    because why wrap basic calls in get/set methods? This isn't CS class, I can do what I want!
    """
    def __init__(self, recipe_name='', staged=False, recipe_data=None):
        QListWidgetItem.__init__(self, recipe_name)
        self.recipe_name = recipe_name
        self.staged = staged
        self.recipe_data = recipe_data
        self.setText(recipe_name)

    def stage(self, stage=True, recipe_data=None):
        if stage:
            self.staged = True
            self.recipe_data = recipe_data
            self.setText(self.recipe_name + ' (*)')
        else:
            self.staged = False
            self.recipe_data = None
            self.setText(self.recipe_name)

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
        self.ui.recipe_list.currentItemChanged.connect(self.handle_rlist_item_change)
        self.ui.recipe_table.cellChanged.connect(self.handle_rtable_cell_change)
        self.ui.revertrecipe_button.clicked.connect(self.handle_revert_click)
        self.ui.save_button.clicked.connect(self.handle_save_click)
        self.ui.update_button.clicked.connect(self.update_backend)

        self.ui.addrecipe_button.clicked.connect(self.handle_addrecipe_click)
        self.ui.delrecipe_button.clicked.connect(self.handle_delrecipe_click)
        self.ui.addflavor_button.clicked.connect(self.handle_addflavor_click)
        self.ui.delflavor_button.clicked.connect(self.handle_delflavor_click)

        # initialize recipe list
        self.recipe_list_items = {}
        for recipe_name in self.be.get_recipes():
            self.add_recipe_to_list(recipe_name)
        self.ui.recipe_list.setCurrentRow(0)

    def add_recipe_to_list(self, recipe_name, stage=False, recipe_data=None):
        item = RecipeItem(recipe_name, stage, recipe_data)
        self.recipe_list_items[recipe_name] = item
        self.ui.recipe_list.addItem(item)

    def get_recipe_data(self, recipe_name):
        try:
            if self.recipe_list_items[recipe_name].staged:
                return self.recipe_list_items[recipe_name].recipe_data
            else:
                return self.be.get_recipe(recipe_name)
        except KeyError:
            print('RecipeEditor.get_recipe_data: KeyError caught!')
            return {}

    def get_staged_recipes_data(self):
        ret = {}
        for (name, item) in self.recipe_list_items.items():
            if item.staged:
                ret[name] = item.recipe_data

        return ret

    def load_recipe(self, recipe_name=None, create_new=False):
        if self.updating_internal or (recipe_name is None and not create_new):
            return
        self.updating_internal = True

        self.current_recipe = recipe_name if recipe_name is not None else 'New Recipe'

        if create_new:
            recipe = {'New Flavor 1':0}
            #self.stage_recipe(recipe_name, recipe)
            self.add_recipe_to_list(recipe_name, True, recipe)
            self.ui.recipe_list.setCurrentItem(self.recipe_list_items[recipe_name])
        else:
            recipe = self.get_recipe_data(recipe_name)
        
        self.ui.recipe_table.clearContents()
        self.ui.recipe_table.setRowCount(len(recipe))

        for (i, flavor) in enumerate(sorted(recipe)):
            self.ui.recipe_table.setItem(i, 0, QTableWidgetItem(flavor))
            self.ui.recipe_table.setItem(i, 1, QTableWidgetItem('%.1f'%(recipe[flavor]*100.0)))

        self.ui.recipe_table.resizeColumnToContents(0)
        self.updating_internal = False

    def update_backend(self):
        self.be.update_recipes(self.get_staged_recipes_data())
        
        # unstage all staged recipes
        for (r, item) in self.recipe_list_items.items():
            item.stage(False)

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
        if recipe_name is None:
            recipe_name = self.current_recipe
        if recipe_data is None:
            recipe_data = self.compile_current_recipe()

        item = self.recipe_list_items[recipe_name]
        item.stage(True, recipe_data)

    def unstage_recipe(self, recipe_name=None):
        if recipe_name is None:
            recipe_name = self.current_recipe

        item = self.recipe_list_items[recipe_name]
        item.stage(False)

    def get_recipe_row(self, recipe_name):
        try:
            return self.ui.recipe_list.row(self.recipe_list_items[recipe_name])
        except KeyError:
            return None

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def handle_rlist_item_change(self, current, previous):
        if current is not None:
            recipe_name = current.recipe_name
            self.load_recipe(recipe_name)

    @pyqtSlot(int, int)
    def handle_rtable_cell_change(self, row, col):
        if self.updating_internal:
            # bail if we're loading a recipe
            return

        if col == 0:
            # TODO actually stage flavor name changes
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
        self.unstage_recipe()
        self.load_recipe(self.current_recipe)

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
