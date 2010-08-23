#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module for mathematical helper functions, mostly for geometry, hence the name.
"""

__version__ = '$Id: __init__.py 247 2009-07-31 17:02:25Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

from vectors import Vec2, sign, Vec3


__all__ = ['Vec2', 'Vec3', 'sign']

if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))

