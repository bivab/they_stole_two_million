#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: main.py 239 2009-07-27 20:41:19Z dr0iddr0id $'

# do not use __file__ because it is not set if using py2exe

# put your imports here
from gamelib import world
import pyknic







def main():
    pyknic.Application(world.PlayState(), '[0,100000000000)','data/custom.yaml').run()


# this is needed in order to work with py2exe
if __name__ == '__main__':
    main()
