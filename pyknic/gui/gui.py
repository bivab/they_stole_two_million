# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: gui.py 275 2009-08-02 09:16:08Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import pygame
import pygame.font
pygame.font.init()


import pyknic

import pyknic.geometry
import pyknic.entity
from pyknic.geometry import Vec3


class FPSDisplay(pyknic.entity.Entity):
    u"""
    Diplay the current fps.
    """
    
    def __init__(self, get_fps, screen_pos, take_average=True):
        u"""
        Constructor.
        
        :Parameters:
            get_fps : function
                a function that return the delta time from last frame in [ms]
                usually it will be Clock.get_fps take from the_app.clock.get_fps
            screen_pos : Vec3
                Position on screen.
            take_average : bool
                Sets averagin on/off. The average is taken over *all* frames.
                Defaults to True.
        """
        if __debug__: print 'FPSDisplay __init__'
        super(FPSDisplay, self).__init__(position=screen_pos)
        #-- prepare chache --#
        self._img_cache = {} # {'digit' : (surf, rect)}
        
        font = pygame.font.Font(u'freesansbold.ttf', 72)
        if __debug__: print 'FPSDisplay __init__ font done'
        
        background_color = (128, 128, 128)
        for digit in '0123456789.':
            surf = font.render(digit, 100, (255, 255, 255), background_color) # text, antialias, color, background=None
            surf = surf.convert()
            surf.set_colorkey(background_color)
            surf.set_alpha(80)
            self._img_cache[digit] = (surf, surf.get_rect().w)
        if __debug__: print 'FPSDisplay __init__ caching digits done'
        self._get_fps = get_fps
        #-- public --#
        self.round = 1
        self.enabled = True
        self.layer = 100000
        # average list
        self._count = 0
        self._sum = 0
        self._take_average = take_average
        if __debug__: print 'FPSDisplay __init__ done'

    def render(self, screen_surf, ignored=None, ignored2=None):
        u"""Render method."""
        if self.enabled:
            fps = self._get_fps()
            if self._take_average:
                self._sum += fps
                self._count += 1
                fps = self._sum / self._count
            blit = screen_surf.blit
            inc = 0
            x, y = self.position.as_xy_tuple()
            for d in str(round(fps, self.round)):
                surf, width = self._img_cache[d]
                blit(surf, (x + inc, y))
                inc += width
#            self.rect.w = inc
#            pygame.draw.rect(screen_surf, (255,255,255), self.rect, 1)

    def update(self, *args):
        pass

#    def hit(self, world_coord):
#        res = super(FPSDisplay, self).hit(world_coord)
##        if res:
##            print 'pfs hit'
#        return res
        
#    def on_screenmouse_enter(self, world_coord):
#        print 'fps m enter',  world_coord, self
#
#    def on_screenmouse_leave(self, world_coord):
#        print 'fps m leave',  world_coord, self

#------------------------------------------------------------------------------



if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))


