#! /usr/bin/env python
# Simple wrapper script which uses the PyQt4.uic module to compile
# all *.ui files in the current directory to Python code

import os

try:
    from PyQt4 import uic
    uic.compileUiDir(os.getcwd())
except Exception as e:
    print("Error compiling UI Files!")
    print(e)
    import traceback
    traceback.print_exc()
    exit(1)
else:
    print("Successfully updated *.ui -> *.py")
    exit(0)
