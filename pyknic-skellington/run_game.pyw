#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: run_game.py 199 2009-07-12 16:38:49Z dr0iddr0id $'

import sys
import os
import subprocess
import datetime


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
    try:
        std_out = sys.stdout
        std_err = sys.stderr
        mode = 'wb'
        # not sure if a timestamp is appreciated since it generates lots of 
        # files, simply replace 'now' to use it
        now = ''
        #now = '-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        name = 'out%s.txt' %(now)
        sys.stdout = open(name, mode)
        name = 'err%s.txt' %(now)
        sys.stderr = open(name, mode)

        run_optimized()

    finally:
        sys.stdout.close()
        sys.stdout = std_out
        sys.stderr.close()
        sys.stderr = std_err
