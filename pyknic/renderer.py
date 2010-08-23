#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Renderer interface class. The renderer makes the world visible.

The renderer is one of the important parts of the engine. Depending on what
type of game it is used for you need different renderers. The simplest is a
topdown renderer. Or a side view renderer for a side sroller. Isometric is 
a bit more involved, but should be possible too.

:TODO:
    add default implementations
    

"""

__version__ = '$Id: renderer.py 198 2009-07-12 16:37:11Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import pygame


from pyknic.geometry import Vec3
import entity


#-------------------------------------------------------------------------------

class IRenderer(entity.Entity):
    u"""
    The renderer interface.
    
    :Ivariables:
        world_rect : Rect
            the rect in the world, basically the region to be drawn
        rect : Rect
            the region on screen, in screen coordinates
        vec_center : `Vec3`
            a vector that point to the center of the screen rect ( Vec3(w//2, h//2) )
        screen_pos : `Vec3`
            The topleft corner of rect
        
    :TODO:
        screen_pos should be read only
    
    Scrolling is done by moving the world_rect around by manipulating position.
    
    """

    # TODO: replace entities with a MapData instance
    def __init__(self, screen_rect, world_rect=None):
        u"""
        Constructor.
        
        :Parameters:
            screen_rect : Rect
                The region on screen where it should draw.
            world_rect : Rect
                The region in the world that should be seen.
                Default: a Rect the same size as the screen_rect
        
        """
        super(IRenderer, self).__init__()
        self._world = None
        self.world_rect = pygame.Rect((0, 0), screen_rect.size)
        if world_rect:
            self.world_rect = world_rect
        self.rect = pygame.Rect(screen_rect)
        self.vec_center = Vec3(screen_rect.w // 2,  screen_rect.h // 2)
        # TODO: moving the rect should upldate screen_pos
        self.screen_pos = Vec3(self.rect.topleft[0],  self.rect.topleft[1])

    world = property(lambda self: self._world, doc=u'''get the world this renderer belongs, read only''')

    def screen_to_world(self, screen_coord):
        u"""
        Converts screen cooridnates in world coordinates.
        
        :Parameters:
            screen_coord : `Vec3`, `Vec2`, tuple
                The screen coordinates to convert. Type may depend on implmementation.
        
        :Note:
            This method needs to be implemented.
        """
        raise NotImplementedError(u'Not implemented method of IRenderer')

    def world_to_screen(self, world_coord):
        u"""
        Converts world cooridnates in screen coordinates.
        
        :Parameters:
            world_coord : `Vec3`, `Vec2`, tuple
                The world coordinates to convert. Type may depend on implmementation.
        
        :Note:
            This method needs to be implemented.
        """
        raise NotImplementedError(u'Not implemented method of IRenderer')

    def render(self, screen_surf, offset):
        u"""
        Renders the world to screen.
        
        :Parameters:
            screen_surf : Surface
                The surface to draw on.
            offset : `Vec3`, `Vec2`, tuple
                The offsset, actually ignored by the renderers (the renderer actually defines the offset).
        
        :Note:
            This method need to be implemented.
        """
        raise NotImplementedError()

    # Q: is this actually needed? 
    # A: yes to overwrite entities update behavior, especially the self.rect
    def update(self, gdt, gt, dt, t, *args, **kwargs):
        u"""
        Updates the renderers position. 
        
        :Parameters:
            gdt : float
                Game delta time.
            gt : float
                Game time, may differ from real time because of time dilation or pauses.
            dt : int
                Time delta since last frame. Real time.
            t : int
                Current time.
        
        All times are in [ms]
        
        """
        # update position
        self.velocity += gdt * self.acceleration
        self.position += gdt * self.velocity
        # update world rect
        if self.target:
            self.position = self.target.position
        self.world_rect.center = self.position.as_xy_tuple()

#-------------------------------------------------------------------------------




#-------------------------------------------------------------------------------

if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))


