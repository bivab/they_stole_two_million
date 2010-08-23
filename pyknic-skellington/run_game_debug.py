#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: run_game_debug.py 218 2009-07-18 20:44:59Z dr0iddr0id $'

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

from gamelib import main

def load(filename):
    import hotshot.log
    from hotshot.log import ENTER, EXIT, LINE
    log = hotshot.log.LogReader(filename)
    db = {}
    accum = 0
    for event in log:
        what, (filename, lineno, funcname), tdelta = event
        if tdelta > 0:
            accum += tdelta
        if what == LINE:
            try:
                db[(filename, lineno, funcname)].append(tdelta * 0.0000001)
            except:
                db[(filename, lineno, funcname)] = [tdelta * 0.0000001]
        elif what == ENTER:
            try:
                db[(filename, lineno, funcname)].append(accum * 0.0000001)
            except:
                db[(filename, lineno, funcname)] = [accum * 0.0000001]
            accum = 0
        elif what == EXIT:
            try:
                db[(filename, lineno, funcname)].append(accum * 0.0000001)
            except:
                db[(filename, lineno, funcname)] = [accum * 0.0000001]
            accum = 0
    return db

def print_data(db, count=80, sorted_by=None):
    # Print the top line timings
    print '\n', '-'*70
    if sorted_by:
        print 'sorte by', sorted_by
    print "%10s %10s %-20s  %5s  %s" % ('call count', 'total time', 'func', 'filename', 'lineno')
    print ''
    for i in range(min(count, len(db))):
        tottime, callcount, (filename, lineno, funcname) = db[i]
#        filename = os.path.basename(filename)
        print "%10i %010f %-20s  %5s  %s" % (callcount, tottime, funcname, filename, lineno)

def run_debug():
    # running in debug mode
    if u"-profile" in sys.argv:
        import cProfile
        import tempfile
        import os
 
        profile_data_fname = "t.profile" #tempfile.mktemp("prf")
        try:
            cProfile.run('main.main()', profile_data_fname)
        finally:
            pass
    else:
        main.main()


if __name__ == '__main__':
    run_debug()
