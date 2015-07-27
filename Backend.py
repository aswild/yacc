# Calculator backend which loads json configs/recipes, and calculates mixes

import json
import pdb

class Backend(object):

	def __init__(self, arg=None):
		if arg is None:
			self._default_config()
		elif type(arg) == dict:
			self._import_config_dict(arg)
		elif type(arg) == str:
			# if arg is a string, assume it's a json filename
			try:
				with open(arg) as fp:
					js = json.load(fp)
					self._import_config_dict(js)
			except:
				print("Error: Unable to load %s! Using default config"%arg)
				self._default_config()
		else:
			print("Error: Unknown constructor argument type! Using default config")
			self._default_config()

	def _default_config(self):
		self._recipes = {}
		self._nic_base = 'vg'
		self._nic_strength = 100.0


	def _import_config_dict(self, arg):
		if '_recipes' in arg.keys():
			self._recipes = self._check_recipes(arg['_recipes'])
			try:
				self._nic_base = arg['_config']['nic_base']
			except KeyError:
				self._nic_base = 'vg'
			try:
				self._nic_strength = arg['_config']['nic_strength']
			except KeyError:
				self._nic_strength = 100
		else:
			# if there's no _recipes dict inside, then assume the whole file is
			# a dict of recipes, and use defaults for nic stuff
			self._default_config()
			self._recipes = self._check_recipes(arg)

	def _check_recipes(self, recipes):
		""" parse the recipes dict given to make sure they're valid
		and automatically remove invalid recipes
		TODO: actually implement this
		TODO: incorporate Qt signals for GUI warning messages"""

		ret = {}
		if type(recipes) is not dict:
			print("Error: recipes is not type 'dict'!")
			return ret

		for (recipe, flavors) in recipes.items():
			if type(flavors) is not dict:
				print("Error: recipe %s does not contain a dict of flavors"%recipe)
				continue
			ret[recipe] = {}
			for (flav, amount) in flavors.items():
				if type(amount) is not int and type(amount) is not float:
					print("Error: flavor %s has non-numeric amount: %s"%(flav, amount))
					continue
				# always assume percent
				amount = amount / 100.0
				ret[recipe][flav] = amount

		return ret

	def calculate_mix(self, recipe_name, totalvol=10, nic=3, vg=70, mix='juice_from_ingredients'):
		""" Calculate the mix for the given recipe and parameters
		TODO: check for max PG/VG and correct appropriately
		"""
		try:
			#pdb.set_trace()
			recipe = self._recipes[recipe_name]
		except KeyError:
			print("Error: recipe %s not found!"%recipe_name)
			return None

		ret = {}
		if vg > 1:
			vg = vg / 100.0

		
		# assumes all flavors are PG, will fix this later
		totalflav = sum([1.0*totalvol*recipe[f] for f in recipe.keys()])
		nic = 1.0*nic*totalvol / self._nic_strength

		# make sure we're within Max VG/Min VG range
		max_vg = 1.0 - self.get_total_flavor(recipe_name) - (nic if self._nic_base=='pg' else 0)
		if vg > max_vg:
			vg = max_vg
			ret['message'] = 'Using Max VG: %.1f%%'%(max_vg*100.0)
		else:
			min_vg = nic / totalvol if self._nic_base=='vg' else 0.0
			if vg < min_vg:
				vg = min_vg
				ret['message'] = 'Using Max PG: %.1f%%'%(100.0*(1.0-min_vg))

		totalvg = totalvol * vg
		totalpg = totalvol - totalvg

		if self._nic_base == 'vg':
			addpg = totalpg - totalflav
			addvg = totalvg - nic
		else:
			addpg = totalpg - totalflav - nic
			addvg = totalvg

		# force positive numbers in case rounding makes -.0000000001 or whatever
		if addpg < 0:
			addpg = 0
		if addvg < 0:
			addvg = 0

		ret['pg'] = addpg
		ret['vg'] = addvg
		ret['nic'] = nic
		ret['flavors'] = {}
		for (f, amount) in recipe.items():
			ret['flavors'][f] = 1.0*totalvol*amount

		return ret

	def get_recipes(self):
		recs = list(self._recipes.keys())
		recs.sort()
		return recs

	def get_config(self):
		return {'n_recipes': len(self._recipes.keys()),
				'nic_strength': self._nic_strength,
				'nic_base': self._nic_base}

	def get_total_flavor(self, recipe_name):
		try:
			recipe = self._recipes[recipe_name]
		except KeyError:
			print("Error: recipe %s not found!"%recipe_name)
			return None
		return sum(recipe.values())

