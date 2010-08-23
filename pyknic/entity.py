#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Here are defined the basic Entity and some default variants of it.

:TODO:
    add default variants of Entity
"""

__version__ = '$Id: entity.py 275 2009-08-02 09:16:08Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import pyknic
import pyknic.animation
from pyknic.geometry import Vec3
import pygame
from pygame.sprite import DirtySprite

#-------------------------------------------------------------------------------
class Spr(object):

    def __init__(self, image=None, offset = Vec3(0, 0), source_rect=None, blendmode=0):
        self.image = image
        if self.image is None:
            self.image = pygame.Surface((0, 0))
        self.offset = offset
        self.source_rect = source_rect
        self.blendmode = blendmode

#Spr = pyknic.animation.Animation

#-------------------------------------------------------------------------------
class Entity(object):
    u"""
    The basic game 'object'. 
    
    :Ivariables:
        rect : Rect
            The rect of the entity in world coordinates. It is the 
            collision bounding box of this entity. center is placed
            at position per default.
        position : `Vec3`
            The world position as a vector. Same as rect.center
        velocity : `Vec3`
            The velocity of the entity.
        acceleration : `Vec3`
            The acceleration of the entity.
        spr : `Animation`
            A sprite object or any object that has a 'image' and 'offset' attribute.
            Has to be set before first call to render.
        t_speed : float
            The per instance time dilation factor. May not be used.
        attachements : list
            The list of attached things, should be `Entity`
        dirty : int
            Indicates that the entity has moved, changed, layer changed so it has
            to be redrawn. Usage depends on the renderer used.
        
    """
    def __init__(self, spr=None, position=None, velocity=None, acceleration=None, coll_rect = None):
        u"""
        Constructor.
        
        :Parameters:
            spr : Sprite
                The sprite can be set at instancing. Default: None
            position : `Vec3`
                The start position. Default: Vec3(0, 0)
            velocity : `Vec3`
                The starting veloctity. Default: Vec3(0, 0)
            acceleration : `Vec3`
                The starting acceleration. Default: Vec3(0, 0)
            coll_rect : Rect
                The collision rect (bounding box). Default: Rect(0, 0, 0, 0)
        
        """
        #-- needed --#
        self.rect = pygame.Rect(0, 0, 0, 0)
        if coll_rect:
            self.rect = coll_rect
        self.position = Vec3(0, 0)
        if position:
            self.position.values = position # world coord
        self.rect.center = self.position.as_xy_tuple()
        self.spr = spr
        self._layer = 0
        self.dirty = 0 # 0 not dirty, 1 dirty, should be set either by move or layer change
        #-- optional --#
        self.velocity = Vec3(0, 0)
        if velocity:
            self.velocity = velocity
        self.acceleration = Vec3(0, 0)
        if acceleration:
            self.acceleration = acceleration
#        if spr:
#            self.spr.pos = self.pos # save ref
        self.t_speed = 1.0

        #-- attachements --#
        self.attachements = []
        self._target = None

    def _set_target(self, target):
        self._target = target
    target = property(lambda self: self._target, _set_target, doc=u'get/set a target to follow or None, entities with target set has to handle them in their custom code')

    def _set_layer(self, new_layer):
        self.dirty = 1
        self._layer = new_layer

    layer = property(lambda self: self._layer, _set_layer, 
                    doc=u"""
                        get/set layer
                        
                        The layer this entity is drawn. May not always be the only ordering 
                        criteria, this depends on the renderer used.
                    
                        """)

    def update(self, gdt, gt, dt, t, *args, **kwargs):
        u"""
        Updates the `Entity`. 
        Default update does those things:
        
            - update velocity
            - update position
            - updates rect.center with position
        
        If target is set then just adjusts position to targets.position.
        
        :Parameters:
            gdt : float
                game delta time, the time that has passed since last frame.
            gt : float
                The game time. This may differ from real time, since game 
                time can run slower or faster or can be paused.
            dt : int
                Real time delta since last frame.
            t : int
                Real time since program startup.
        
        All times are in [ms].
        """
        if self.target:
            self.position = self.target.position
        else:
            # update position
            dt = gdt * self.t_speed
            self.velocity += self.t_speed * dt * self.acceleration
            self.position += self.t_speed * dt * self.velocity
        # update collision rect
        self.rect.center = self.position.as_xy_tuple()

    def render(self, screen_surf, offset=Vec3(0, 0), screen_offset=Vec3(0, 0)):
        u"""
        Draws the entity.
        
        :Parameters:
            screen_surf : Surf
                The screen to draw on.
            offset : `Vec3`
                The offset from the world coordinates system. Default: Vec3(0, 0)
            screen_offset : `Vec3`
                On the real screen, the offset. Normally not used. Default: Vec3(0, 0)
        
        """
        screen_surf.blit(self.spr.image, (self.position - offset - self.spr.offset).as_xy_tuple(), self.spr.source_rect, self.spr.blendmode)

    # Q: should update and render take care of attachemens or not? 
    # A: no, each entity has to handle the target itself
    def attach(self, entity):
        u""":Note: unstable"""
        if entity not in self.attachements:
            self.attachements.append(entity)
            entity.target = self

    def detach(self, entity):
        u""":Note: unstable"""
        if entity in self.attachements:
            self.attachements.remove(entity)
            entity.target = None

    def collision_response(self, other):
        u""":Note: unstable"""
        pass
    def activate(self, player, *args, **kwargs):
        u""":Note: unstable"""
        pass
    def handle_event(self, event):
        u""":Note: unstable"""
        pass
    
    #-- mouse interaction --#
    def hit(self, world_coord):
        u"""
        Test hit with world coordinates and return boolean.
        If the coordiantes hit the entity it should return True.
        Otherwise False.
        
        This default implementation just returns True regardles of size.
        
        :Parameters:
            world_coord : `Vec3`
                The cooridnates to test.
        
        """
        return self.rect.collidepoint(world_coord.as_xy_tuple())
    
    def on_screenmouse_enter(self, world_coord, dragging):
        u"""
        This is called when mouse hovers over it and `Entity` is topmost.
        When this entity is the topmost and the `ScreenMouse` enters
        the area of this entity, this method is called. The default 
        implementation does nothing.
        
        This default implementation does nothing (pass).
        
        :Parameters:
            world_coord : `Vec3`
                Where the mouse entered this entity. May be a bit inaccurate.
        """
        pass
    
    def on_screenmouse_leave(self, world_coord, dragging):
        u"""
        This is called when mouse leaves it and `Entity` is topmost.
        When this entity is the topmost and the `ScreenMouse` leaves
        the area of this entity, this method is called. The default 
        implementation does nothing.
        
        This default implementation does nothing (pass).
        
        :Parameters:
            world_coord : `Vec3`
                Where the mouse left this entity. May be a bit inaccurate.
        """
        pass

    def on_screenmouse_button_down(self, pos, buttons, mods):
        u"""
        This is called when the mouse is over this entity and a 
        mouse button is pressed. The default implementation does nothing.
        
        :Parameters:
            pos : `Vec3`
                world coordinates of the screen mouse position.
            buttons : tuple
                (int, int, int) as in pygame mouse button down
            mods : int
                keyboard modifiers, as in the pygame event
        """
        pass

    def on_screenmouse_button_up(self, pos, buttons, mods):
        u"""
        This is called when the mouse is over this entity and a 
        mouse button is released. The default implementation does nothing.
        
        :Parameters:
            pos : `Vec3`
                world coordinates of the screen mouse position.
            buttons : tuple
                (int, int, int) as in pygame mouse button down
            mods : int
                keyboard modifiers, as in the pygame event
        """
        pass

    def on_screenmouse_drag_start(self, pos, buttons, mods):
        u"""
        This is called when the `ScreenMouse` starts dragging when it
        is over this entity. Thats where you could attach data to the mouse and
        maybe change the mouse cursor. The default implementation does nothing.
        
        :Parameters:
            pos : `Vec3`
                world coordinates of the screen mouse position.
            buttons : tuple
                (int, int, int) as in pygame mouse button down
            mods : int
                keyboard modifiers, as in the pygame event
        """
        pass

    def on_screenmouse_drag_drop(self, pos, buttons, mods):
        u"""
        This is called when the `ScreenMouse` stops dragging over this 
        entity. The default implementation does nothing.
        
        :Parameters:
            pos : `Vec3`
                world coordinates of the screen mouse position.
            buttons : tuple
                (int, int, int) as in pygame mouse button down
            mods : int
                keyboard modifiers, as in the pygame event
        """
        pass


#-------------------------------------------------------------------------------

if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))


