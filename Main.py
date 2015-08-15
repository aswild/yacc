#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui
from ui_yacc_main_window import Ui_yacc_main_window
from Backend import Backend
import pdb

CONFIG_FILE = 'vaperecipes.json'

class YaccMain(QtGui.QMainWindow):
    def __init__(self, parent=None):
        self.is_init = False
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_yacc_main_window()
        self.ui.setupUi(self)

        # set up backend and load recipes
        self.config_file = CONFIG_FILE
        self.load_config()

        # Fill in UI defaults
        self.ui.totalvol_box.setText('10')
        self.ui.nic_box.setText('2')
        self.ui.vg_box.setText('70')

        # add combo box options
        self.ui.mix_box.addItem('Juice from Ingredients', 'from_ingredients')
        self.ui.mix_box.addItem('Juice from Concentrate', 'from_concentrate')
        self.ui.mix_box.addItem('Concentrate', 'concentrate')

        # status bar
        self.status_config_message_label = QtGui.QLabel()
        self.ui.status_bar.addPermanentWidget(self.status_config_message_label)

        # signals/slots
        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.update_button.clicked.connect(self.update_mix)
        self.ui.recipe_box.currentIndexChanged.connect(self.update_mix)
        self.ui.recipe_box.currentIndexChanged.connect(self.update_recipe_status)
        self.ui.mix_box.currentIndexChanged.connect(self.update_mix)
        self.ui.totalvol_box.textChanged.connect(self.update_mix)
        self.ui.nic_box.textChanged.connect(self.update_mix)
        self.ui.vg_box.textChanged.connect(self.update_mix)
        self.ui.reload_button.clicked.connect(self.load_config)

        self.is_init = True
        self.update_mix()
        self.update_config_status()
        self.update_recipe_status()

    def update_mix(self):
        if not self.is_init:
            return

        mix_inputs = self.check_inputs()
        if mix_inputs is None:
            return

        mix = self.be.calculate_mix(*mix_inputs)
        if mix is None:
            # calculate_mix returns None if the recipe can't be found, so just bail
            # This shouldn't really happen since recipe_box is only populated by items that
            # backend.get_recipes returns
            mix = 'Backend Error!'

        self.ui.output_box.setPlainText(mix)

    def update_config_status(self):
        cfg = self.be.get_config()
        self.status_config_message_label.setText('Nicotine: %d mg/mL %s; Recipes Loaded: %d'%(
                                                cfg['nic_strength'], cfg['nic_base'].upper(), cfg['n_recipes']))
    
    def load_config(self):
        is_init_last = self.is_init
        self.is_init = False # make sure update_mix doesn't fail when the config is cleared out
        self.be = Backend(self.config_file)
        selected_recipe = self.ui.recipe_box.currentText()

        self.ui.recipe_box.clear()
        for recipe in self.be.get_recipes():
            self.ui.recipe_box.addItem(recipe)

        selected_index = self.ui.recipe_box.findText(selected_recipe)
        if selected_index != -1:
            self.ui.recipe_box.setCurrentIndex(selected_index)

        self.is_init = is_init_last
        self.update_mix()

    def update_recipe_status(self):
        if not self.is_init:
            return

        current_recipe = str(self.ui.recipe_box.currentText())
        total_flav = self.be.get_total_flavor(current_recipe)
        if total_flav is None:
            self.ui.status_bar.showMessage('Recipe %s not found!'%current_recipe)
        else:
            total_flav = total_flav * 100.0
            self.ui.status_bar.showMessage('Recipe: %s; Total Flavor: %.1f%%; Max VG: %.1f%%'%(
                                            current_recipe, total_flav, 100.0-total_flav))

    def check_inputs(self):
        """ Read the mix parameters from the UI elements and convert numbers to type float.
            If float() returns a value error, mark that input box red and return None, otherwise
            return a tuple of parameters that can be passed directly to backend.calculate_mix()
        """

        # We can always make these strings, and strings are expected anyway so no error checking
        # calculate_mix will make sure that the selected recipe exists
        recipe = str(self.ui.recipe_box.currentText())
        mix = str(self.ui.mix_box.itemData(self.ui.mix_box.currentIndex()))

        err = False
        try:
            totalvol = float(self.ui.totalvol_box.text())
            if totalvol <= 0:
                raise ValueError
            self.ui.totalvol_box.setStyleSheet('')
        except ValueError:
            self.ui.totalvol_box.setStyleSheet('background-color: rgb(255, 102, 102);')
            err = True

        try:
            nic = float(self.ui.nic_box.text())
            if nic < 0:
                raise ValueError
            self.ui.nic_box.setStyleSheet('')
        except ValueError:
            self.ui.nic_box.setStyleSheet('background-color: rgb(255, 102, 102);')
            err = True

        try:
            vg = float(self.ui.vg_box.text())
            if vg < 0:
                raise ValueError
            self.ui.vg_box.setStyleSheet('')
        except ValueError:
            self.ui.vg_box.setStyleSheet('background-color: rgb(255, 102, 102);')
            err = True

        return None if err else (recipe, totalvol, nic, vg, mix)


    def exit(self):
        QtCore.QCoreApplication.instance().quit()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = YaccMain()
    myapp.show()
    sys.exit(app.exec_())
