#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: __init__.py 236 2009-07-26 22:18:06Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

#try:
#    # use installed yaml as possible (probably faster)
#    import yaml
#except:
#    # else use internal pyyaml
#    import yamlv308 as yaml


if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))

