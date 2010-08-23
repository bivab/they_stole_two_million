#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: run_game.py 218 2009-07-18 20:44:59Z dr0iddr0id $'

import sys
import os
import subprocess


# run in right directory
if not sys.argv[0]:
    appdir = os.path.abspath(os.path.dirname(__file__))
else:
    appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
os.chdir(appdir)
if not appdir in sys.path:
    sys.path.insert(0,appdir)

def run_optimized():
    if __debug__:
        # start subprocess
        subp_args = [str(sys.executable), "-O", str(__file__)]
        for arg in sys.argv[1:]:
            subp_args.append(arg)
        #subprocess.Popen(subp_args)
        subprocess.call(subp_args)
    else:
        # running optimized
        # import the game
        from gamelib import main
        main.main()

if __name__ == '__main__':
    run_optimized()
