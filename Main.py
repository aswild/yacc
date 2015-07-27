#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui
from ui_yacc_main_window import Ui_yacc_main_window
from Backend import Backend
import pdb

class YaccMain(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_yacc_main_window()
		self.ui.setupUi(self)

		# set up backend
		self.be = Backend('vaperecipes.json')

		# Fill in UI defaults
		self.ui.totalvol_box.setText('100')
		self.ui.nic_box.setText('3')
		self.ui.vg_box.setText('70')

		# add combo box options
		self.ui.mix_box.addItem('Juice from Ingredients', 'from_ingredients')
		self.ui.mix_box.addItem('Juice from Concentrate', 'from_concentrate')
		self.ui.mix_box.addItem('Concentrate', 'concentrate')

		for recipe in self.be.get_recipes():
			self.ui.recipe_box.addItem(recipe)

		# set up signals/slots
		self.ui.actionExit.triggered.connect(self.exit)
		self.ui.update_button.clicked.connect(self.update)
		self.ui.recipe_box.currentIndexChanged.connect(self.update)
		self.ui.mix_box.currentIndexChanged.connect(self.update)
		self.ui.totalvol_box.textChanged.connect(self.update)
		self.ui.nic_box.textChanged.connect(self.update)
		self.ui.vg_box.textChanged.connect(self.update)

		self.update()

	def update(self):
		mix_inputs = self.check_inputs()
		if mix_inputs is None:
			return

		mix = self.be.calculate_mix(*mix_inputs)
		if mix is None:
			# calculate_mix returns None if the recipe can't be found, so just bail
			# This shouldn't really happen since recipe_box is only populated by items that
			# backend.get_recipes returns
			return

		max_flavor_length = max([len(f) for f in (list(mix['flavors'].keys()) + ['Nicotine'])])

		self.ui.output_box.setPlainText('')
		for f in sorted(mix['flavors'].keys()):
			spaces = max_flavor_length - len(f)
			self.ui.output_box.appendPlainText('%s: %3.2f mL'%(' '*spaces + f, mix['flavors'][f]))
		self.ui.output_box.appendPlainText('') # blank line
		self.ui.output_box.appendPlainText(' '*(max_flavor_length-8) + 'Nicotine: %3.2f mL'%mix['nic'])
		self.ui.output_box.appendPlainText(' '*(max_flavor_length-2) + 'VG: %3.2f mL'%mix['vg'])
		self.ui.output_box.appendPlainText(' '*(max_flavor_length-2) + 'PG: %3.2f mL'%mix['pg'])

	def check_inputs(self):
		""" Read the mix parameters from the UI elements and convert numbers to type float.
			If float() returns a value error, mark that input box red and return None, otherwise
			return a tuple of parameters that can be passed directly to backend.calculat_mix()
		"""

		# We can always make these strings, and strings are expected anyway so no error checking
		# calculat_mix will make sure that the selected recipe exists
		recipe = str(self.ui.recipe_box.currentText())
		mix = str(self.ui.mix_box.itemData(self.ui.mix_box.currentIndex()))

		err = False
		try:
			totalvol = float(self.ui.totalvol_box.text())
			self.ui.totalvol_box.setStyleSheet('')
		except ValueError:
			self.ui.totalvol_box.setStyleSheet('background-color: rgb(255, 102, 102);')
			err = True

		try:
			nic = float(self.ui.nic_box.text())
			self.ui.nic_box.setStyleSheet('')
		except ValueError:
			self.ui.nic_box.setStyleSheet('background-color: rgb(255, 102, 102);')
			err = True

		try:
			vg = float(self.ui.vg_box.text())
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
