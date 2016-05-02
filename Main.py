#! /usr/bin/env python

import sys
import platform
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from PyQt4.QtGui import QFont, QFontInfo
from yacc_main_window import Ui_yacc_main_window
from RecipeEditor import RecipeEditor
from Backend import Backend
import pdb

CONFIG_FILE = 'vaperecipes.json'

class YaccMain(QtGui.QMainWindow):
    def __init__(self, parent=None):
        self.is_init = False
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_yacc_main_window()
        self.ui.setupUi(self)

        # extra UI setup: cross-platform monospace font
        mfont = self.get_monospace_font()
        self.ui.output_box.setFont(mfont)

        # set up backend and load recipes
        self.config_file = CONFIG_FILE
        self.load_config()

        # Fill in UI defaults
        self.ui.totalvol_box.setText('10')
        self.ui.nic_box.setText('3')
        self.ui.vg_box.setText('70')

        # add combo box options
        self.ui.mix_box.addItem('Juice from Ingredients', 'from_ingredients')
        self.ui.mix_box.addItem('Juice from Concentrate', 'from_concentrate')
        self.ui.mix_box.addItem('Concentrate', 'concentrate')

        # status bar
        self.status_config_message_label = QtGui.QLabel()
        self.ui.status_bar.addPermanentWidget(self.status_config_message_label)

        # recipe editor
        self.recipe_editor = None

        # saved values of nic/vg for switching in and out of concentrate mode
        self.save_nic = None
        self.save_vg = None

        # signals/slots
        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.update_button.clicked.connect(self.update_mix)
        self.ui.recipe_box.currentIndexChanged.connect(self.update_mix)
        self.ui.recipe_box.currentIndexChanged.connect(self.update_recipe_status)
        self.ui.mix_box.currentIndexChanged.connect(self.handle_mixtype_change)
        self.ui.totalvol_box.textChanged.connect(self.update_mix)
        self.ui.nic_box.textChanged.connect(self.update_mix)
        self.ui.vg_box.textChanged.connect(self.update_mix)
        self.ui.reload_button.clicked.connect(self.load_config)
        self.ui.redit_button.clicked.connect(self.launch_redit)
        self.ui.actionAdd_Recipes.triggered.connect(self.launch_redit)

        self.is_init = True
        self.update_mix_type()
        self.update_mix()
        self.update_config_status()
        self.update_recipe_status()

    def get_monospace_font(self):
        preferred_fonts_windows = ['Courier New', 'Lucida Console']
        preferred_fonts_linux = ['Noto Mono', 'Monospace']

        if 'Windows' in platform.system():
            pfonts = preferred_fonts_windows
        else:
            pfonts = preferred_fonts_linux

        for fontname in pfonts:
            font = QFont(fontname)
            font.setPointSize(12)
            info = QFontInfo(font)
            if info.fixedPitch():
                return font

        print('Warning: no font in preferred list %s found!'%pfonts)
        font = QFont()
        font.setStyleHint(QFont.Monospace)
        info = QFontInfo(font)
        print('Selected font family: %s'%info.family())

    def update_mix(self):
        if not self.is_init:
            return

        mix_inputs = self.check_inputs()
        if mix_inputs is None:
            return

        mix = self.be.calculate_mix(**mix_inputs)
        if mix is None:
            # calculate_mix returns None if the recipe can't be found, so just bail
            # This shouldn't really happen since recipe_box is only populated by items that
            # backend.get_recipes returns
            mix = 'Backend Error!'

        self.ui.output_box.setPlainText(mix)

    def update_mix_type(self):
        if not self.is_init:
            return

        mix_type = self.ui.mix_box.itemData(self.ui.mix_box.currentIndex())
        if mix_type == 'concentrate':
            # making concentrate, so disable nic and VG
            self.save_nic = self.ui.nic_box.text()
            self.save_vg  = self.ui.vg_box.text()
            self.ui.nic_box.setText('')
            self.ui.nic_box.setEnabled(False)
            self.ui.vg_box.setText('')
            self.ui.vg_box.setEnabled(False)

        else:
            # default, unlock nic and vg boxes
            self.ui.nic_box.setEnabled(True)
            if self.save_nic is not None:
                self.ui.nic_box.setText(self.save_nic)
                self.save_nic = None

            self.ui.vg_box.setEnabled(True)
            if self.save_vg is not None:
                self.ui.vg_box.setText(self.save_vg)
                self.save_vg = None
        
    def update_config_status(self):
        cfg = self.be.get_config()
        self.status_config_message_label.setText('Nicotine: %d mg/mL %s; Recipes Loaded: %d'%(
                                                cfg['nic_strength'], cfg['nic_base'].upper(), cfg['n_recipes']))
    
    def load_config(self):
        is_init_last = self.is_init
        self.is_init = False # make sure update_mix doesn't fail when the config is cleared out
        self.be = Backend(self.config_file)
        selected_recipe = self.ui.recipe_box.currentText()
        self.populate_recipe_box(selected_recipe)

        self.is_init = is_init_last
        self.update_mix()

    def populate_recipe_box(self, selected_recipe=None):
        is_init_last = self.is_init
        self.is_init = False
        self.ui.recipe_box.clear()
        for recipe in self.be.get_recipes():
            self.ui.recipe_box.addItem(recipe)

        if selected_recipe is not None:
            selected_index = self.ui.recipe_box.findText(selected_recipe)
            if selected_index != -1:
                self.ui.recipe_box.setCurrentIndex(selected_index)
        self.is_init = is_init_last

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


        # NOTE: names here must match the inputs of Backend.calculate_mix
        inputs_out = {'recipe_name': recipe,
                      'mix': mix}

        inputs_check = [('totalvol', self.ui.totalvol_box)]

        if mix != 'concentrate':
            inputs_check += [('nic', self.ui.nic_box),
                             ('vg', self.ui.vg_box)]

        err = False
        for (field, box) in inputs_check:
            try:
                inputs_out[field] = float(box.text())
                if inputs_out[field] < 0:
                    raise ValueError
                box.setStyleSheet('')
            except ValueError:
                box.setStyleSheet('background-color: rgb(255, 102, 102);')
                err = True

        return None if err else inputs_out

    def launch_redit(self):
        if self.recipe_editor is None:
            self.recipe_editor = RecipeEditor(self, self.be)
            self.recipe_editor.signal_exit.connect(self.handle_redit_exit)
            self.recipe_editor.signal_backend_updated.connect(self.handle_redit_backend_update)
            self.recipe_editor.show()

    def handle_mixtype_change(self):
        # wrapper here for change event on mix type box
        # Do this rather than assigning 2 slots so it executes in definite order
        self.update_mix_type()
        self.update_mix()

    @pyqtSlot()
    def handle_redit_backend_update(self):
        selected_recipe = self.ui.recipe_box.currentText()
        self.populate_recipe_box(selected_recipe)
        self.update_recipe_status()
        self.update_mix()

    @pyqtSlot(str)
    def handle_redit_exit(self, text):
        self.ui.output_box.setPlainText('RBUILD EXIT:' + text)
        self.recipe_editor = None

    def exit(self):
        QtCore.QCoreApplication.instance().quit()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = YaccMain()
    myapp.show()
    sys.exit(app.exec_())
