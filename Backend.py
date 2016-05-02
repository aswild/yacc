# Calculator backend which loads json configs/recipes, and calculates mixes

import json, pprint
import pdb

class Backend(object):

    def __init__(self, arg=None):
        self.filename = None
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
                    self.filename = arg
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

        # assumes all flavors are PG, will fix this later
        totalflav = sum([1.0*totalvol*recipe[f] for f in recipe.keys()])
        totalflav_part = totalflav / float(totalvol)
        message = None

        if mix != 'concentrate':
            if vg > 1:
                vg = vg / 100.0

            message = None
            nic = 1.0*nic*totalvol / self._nic_strength

            # make sure we're within Max VG/Min VG range
            max_vg = 1.0 - self.get_total_flavor(recipe_name) - (nic if self._nic_base=='pg' else 0)
            if vg > max_vg:
                vg = max_vg
                message = 'Using Max VG: %.1f%%'%(max_vg*100.0)
            else:
                min_vg = nic / totalvol if self._nic_base=='vg' else 0.0
                if vg < min_vg:
                    vg = min_vg
                    message = 'Using Max PG: %.1f%%'%(100.0*(1.0-min_vg))

            totalvg = totalvol * vg
            totalpg = totalvol - totalvg

            if self._nic_base == 'vg':
                addpg = totalpg - totalflav
                addvg = totalvg - nic
            else:
                addpg = totalpg - totalflav - nic
                addvg = totalvg

            # force nonnegative numbers in case rounding makes -.0000000001 or whatever
            if addpg < 0:
                addpg = 0
            if addvg < 0:
                addvg = 0


        # generate string to return for the output box
        max_flavor_name_len = max(len(f) for f in (list(recipe.keys()) + ['Nicotine']))
        ret = ''

        if mix != 'from_concentrate':
            for f in sorted(recipe.keys()):
                if mix == 'from_ingredients':
                    f_vol = 1.0*totalvol*recipe[f]
                else: # 'concentrate'
                    f_vol = (totalvol * recipe[f]) / totalflav_part

                spaces = max_flavor_name_len - len(f)
                ret += '\n%s: %3.2f mL'%(' '*spaces + f, f_vol)
            # the first character will always be a newline from the loop above, which we don't want, so kill it
            ret = ret[1:]

        elif mix == 'from_concentrate':
            # "Concentrate" is longer than Nicotine, so it gets the max
            max_flavor_name_len = len('Concentrate')
            ret = 'Concentrate: %3.2f mL'%totalflav


        if mix != 'concentrate':
            # add nic/VG/PG
            ret += '\n\n' + ' '*(max_flavor_name_len-8) + 'Nicotine: %3.2f mL'%nic
            ret += '\n'   + ' '*(max_flavor_name_len-2) + 'VG: %3.2f mL'%addvg
            ret += '\n'   + ' '*(max_flavor_name_len-2) + 'PG: %3.2f mL'%addpg

        if message is not None:
            ret += '\n\n' + message

        return ret

    def calculate_concentrate_mix(self, recipe_name, totalvol=10):
        try:
            recipe = self._recipes[recipe_name]
        except KeyError:
            print("Error: recipe %s not found!"%recipe_name)
            return None

        # generate string to return for the output box
        max_flavor_name_len = max(len(f) for f in (list(recipe.keys()) + ['Nicotine']))
        ret = ''
        for f in sorted(recipe.keys()):
            f_vol = 1.0*totalvol*recipe[f]
            spaces = max_flavor_name_len - len(f)
            ret += '\n%s: %3.2f mL'%(' '*spaces + f, f_vol)

        # the first character will always be a newline from the loop above, which we don't want, so kill it
        ret = ret[1:]


    def get_total_flavor(self, recipe_name):
        try:
            recipe = self._recipes[recipe_name]
        except KeyError:
            print("Error: recipe %s not found!"%recipe_name)
            return None
        return sum(recipe.values())

    def get_recipe(self, recipe):
        try:
            return self._recipes[recipe]
        except KeyError:
            return None
    
    def get_recipes(self):
        recs = list(self._recipes.keys())
        recs.sort()
        return recs

    def get_config(self):
        return {'n_recipes': len(self._recipes.keys()),
                'nic_strength': self._nic_strength,
                'nic_base': self._nic_base}

    def update_recipe(self, recipe_name, recipe_data):
        self._recipes[recipe_name] = recipe_data

    def update_recipes(self, recipes):
        for r in recipes:
            self._recipes[r] = recipes[r]

    def write_file(self, filename=None):
        print('Backend.write_file')
        if filename is None:
            filename = self.filename
            if filename is None:
                print('Backend.write_file: no filename given!')
                return

        # convert floats to percents
        rout = {}
        for r in self._recipes:
            rout[r] = {}
            for f in self._recipes[r]:
                rout[r][f] = self._recipes[r][f] * 100.0

        js = json.dumps(rout, sort_keys=True, indent=4, separators=(',', ': '))
        with open(filename, 'w') as fp:
            fp.write(js)
