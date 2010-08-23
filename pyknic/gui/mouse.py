# -*- coding: utf-8 -*-

"""
The ScreenMouse provides some useful things for interacting with the mouse.
"""

__version__ = '$Id: mouse.py 239 2009-07-27 20:41:19Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import pygame
from pygame.mouse import get_pos as get_mouse_pos

import pyknic
import pyknic.geometry
import pyknic.events
from pyknic.geometry import Vec3
from pyknic.utilities.utilities import SortedList
from pyknic.events import Signal

#------------------------------------------------------------------------------

# TODO: add default graphic
# TODO: drag interaction scheme
class ScreenMouse(pyknic.entity.Entity):
    u"""
    The pyknic mouse. 
    
    Features:
     * hot-spot
     * sprite stack
     * capture
     * automatic send of enter/leave an entity and/or renderer
    
    The hot-spot of the mouse is actually defined by the offset of the sprite 
    (or look at it as the cursor sprite is adjusted such the hot-spot is at the 
    coords or the mouse).
    
    :Ivariables:
        screen_pos : Vec3
            the current screen pos
        layer : int
            the layer the mouse is in
        collision_rect_offset : Vec3
            offset of the self.rect from the hot-spot
            self.rect is used for collision checking, so be careful using this option
        rect : Rect
            should always have (0, 0) as size, unless wanted differently, actually 
            it is not direcly used by ScreenMouse, but later using collision detection
            it will be useful. Its like the bounding box of the mouse entity.
        hover_entity : entity
            the topmost entity the mouse is currently over (that returns hit() == True)
        hover_renderer : renderer
            the topmost renderer the mouse is currently over (that returns hit() == True)
    
    
    :TODO:
        Should mouse also send on_gui_mouse_press /release to entites?
    """

    def __init__(self, state):
        u""" Initialize ScreenMouse"""
        if __debug__: print 'ScreenMouse __init__'
        self._init_done = False
        self._sprites = [] # sprite stack
        super(ScreenMouse, self).__init__()
        self._worlds = SortedList([], lambda x: -x.layer)
        if __debug__: print 'ScreenMouse __init__ _worlds SortedList done'
        self._init_done = True
        #-- public --#
        self.screen_pos = Vec3(0, 0)
        self.layer = 100000
        self.collision_rect_offset = Vec3(0, 0)
        self.hover_entity = None
        self.hover_renderer = None
        #-- unsure --#
        # TODO: add default sprite
#        self.position = None
#        self._capturer = None
#        Not sure if this is right place
#        self.on_screenmouse_button_down = Signal('screenmouse_button_down')
#        self.on_screenmouse_button_up = Signal('screenmouse_button_up')
        self.is_dragging = False
        self.events = pyknic.events.SignalProvider()
        if __debug__: print 'ScreenMouse __init__ SignalProvider done'
        self._state = state
        self.register_event_listeners()
        if __debug__: print 'ScreenMouse __init__ register events done'
        if __debug__: print 'ScreenMouse __init__ done'

    def register_event_listeners(self):
        state_events = self._state.events
        # unregister
        state_events.mouse_drag -= self.on_mouse_drag
        state_events.mouse_drag_drop -= self.on_drag_drop
        state_events.mouse_drag_start -= self.on_drag_start
        state_events.mouse_motion -= self.on_mouse_motion
        state_events.mouse_button_down -= self.on_mouse_button_down
        state_events.mouse_button_up -= self.on_mouse_button_up
        # register
        state_events.mouse_drag += self.on_mouse_drag
        state_events.mouse_drag_drop += self.on_drag_drop
        state_events.mouse_drag_start += self.on_drag_start
        state_events.mouse_motion += self.on_mouse_motion
        state_events.mouse_button_down += self.on_mouse_button_down
        state_events.mouse_button_up += self.on_mouse_button_up

#    is_captured = property(lambda self: self._capturer is not None, doc=u'read only, return bool')
#    def _set_capturer(self, capturer):
#        self._capturer = capturer
#    capturer = property(lambda self: self._capturer, _set_capturer, doc=u'get/set capturer, set to None to release capture')

    def _set_spr(self, value):
        # allow to set a sprite from __init__
        if not self._init_done:
            self.push_sprite(value)
        else:
            raise Exception(u'spr is read only for mouse, use push_sprite() and pop_sprite() instead!')
    spr = property(lambda self: self._sprites[-1], _set_spr, doc=u'read-only, use push_sprite() and pop_sprite() instead!')

    def on_mouse_drag(self, pos, rel, buttons, mods):
        u"""
        :TODO: doc
        """
        self.is_dragging = True
        self.on_mouse_motion(pos, rel, True)
        if self.hover_renderer:
            self.events.screenmouse_drag(self.position, self.hover_renderer.screen_to_world(Vec3(*rel)), buttons, mods)

    def on_drag_drop(self, pos, buttons, mods):
        if self.hover_renderer:
            self.events.screenmouse_drag_drop(self.position, buttons, mods)
            if self.hover_entity:
                self.hover_entity.on_screenmouse_drag_drop(self.position, buttons, mods)

    def on_drag_start(self, pos, buttons, mods):
        if self.hover_renderer:
            self.events.screenmouse_drag_start(self.position, buttons, mods)
            if self.hover_entity:
                self.hover_entity.on_screenmouse_drag_start(self.position, buttons, mods)

    def on_mouse_motion(self, pos, rel, dragging=False):
        u"""
        :TODO: doc
        """
        self.is_dragging = dragging
        self.screen_pos = Vec3(*pos)
        # TODO: is this a good idea to stop processing if captured?
        #if not self.is_captured:
        # check world collisions
        for world in self._worlds: # normally one world
            for renderer in world.get_renderers(): # normally 1-2 renderers
                if renderer.hit(self.screen_pos): # normally only 1 is hit
                    if renderer != self.hover_renderer:
                        if self.hover_renderer:
                            self.hover_renderer.on_screenmouse_leave(self.screen_pos, dragging)
                        self.hover_renderer = renderer
                        renderer.on_screenmouse_enter(self.screen_pos, dragging)
                    # update world position
                    self.position = renderer.screen_to_world(self.screen_pos)
                    if self.position:
                        self.rect.topleft = self.position.as_xy_tuple()
                        # entites sorted by layer, last is in front
                        for entity in reversed(world.get_entities_in_region(self.rect)):
                            # only do something if we hit an entity different from last time
                            if entity.hit(self.position):
                                # check if entity is hit
                                if entity != self and entity != self.hover_entity:
                                    # replace
                                    if self.hover_entity: # may be None
                                        self.hover_entity.on_screenmouse_leave(self.position, dragging)
                                    self.hover_entity = entity
                                    entity.on_screenmouse_enter(self.position, dragging)
                                return
                            else:
                                if self.hover_entity:
                                    self.hover_entity.on_screenmouse_leave(self.position, dragging)
                                    self.hover_entity = None
                        self.events.screenmouse_motion(self.position, self.hover_renderer.screen_to_world(Vec3(*rel)))
                    else:
                        # FIXME: TODO: this isnt a good nor elegant solution!!
                        raise Exception( 'SCREENMOUSE invalid POSITON %s' % (self.position))
                        self.position = Vec3(-99999, -99999, -99999)
                    return
            # either no world or no entity.hit() return True
            if self.hover_entity:
                self.hover_entity.on_screenmouse_leave(self.position, self.is_dragging)
                self.hover_entity = None
        if self.hover_renderer:
            self.hover_renderer.on_screenmouse_leave(self.screen_pos, self.is_dragging)
            self.hover_renderer = None

    def on_mouse_button_down(self, pos, buttons, mods):
        if self.hover_renderer:
            if self.hover_entity:
                self.hover_entity.on_screenmouse_button_down(self.position, buttons, mods)
            self.events.screenmouse_button_down(self.position, buttons, mods)

    def on_mouse_button_up(self, pos, buttons, mods):
        if self.hover_renderer:
            if self.hover_entity:
                self.hover_entity.on_screenmouse_button_up(self.position, buttons, mods)
            self.events.screenmouse_button_up(self.position, buttons, mods)

    def render(self, screen_surf, offset=Vec3(0, 0), screen_offset=Vec3(0, 0)):
        u"""
        Draws the ScreenMouse with its sprite. The 'hot spot' is defined by 
        the sprite offset.
        
        :TODO:
            rewrite to only render in the correct renderer
        """
        if self.hover_renderer and self.hover_renderer.rect.size == screen_surf.get_size() and self._sprites:
            spr = self._sprites[-1]
            screen_surf.blit(spr.image, (self.screen_pos - screen_offset - spr.offset).as_xy_tuple())

    #-- world registration --#
    def register_world(self, world):
        u"""
        The worlds that the mouse should interact have to be registered.
        By doing so, the ScreenMouse is added to the worls as normal entity.
        """
        world.add_entity(self)
        self._worlds.insort(world)

    def unregister_world(self, world):
        u"""
        Remove a world and stop interact with it.
        """
        if world in self._worlds:
            self._worlds.remove(world)
            world.remove_entity(self)

    #-- sprites interaction --#
    def push_sprite(self, sprite):
        u"""
        Set a different sprite. The mouse will use this immediatly.
        """
        self._sprites.append(sprite)

    def pop_sprite(self):
        u"""
        Remove a previously pushed sprite. Make sure there is always
        a sprite left (last should always be the default sprite) or you wont 
        see a mouse.
        """
        return self._sprites.pop()

#    def set_default_sprite(self, sprite):
#        u"""
#        Set the first sprite of the stack. It overwrites any sprite 
#        at position 0 (first) of the stack.
#        """
#        if self._sprites:
#            self._sprites[0] = sprite
#        else:
#            self._sprites.append(sprite)

# TODO: not sure if this is a good idea
#    def on_mouse_button_down(self, pos, button, mods):
#        u"""
#        Calls on_screenmouse_button_down on the colliding entity, if hit.
#        """
#        pass
#        
#    def on_mouse_button_up(self, pos, button, mods):
#        u"""
#        Calls on_screenmouse_button_up on the colliding entity, if hit.
#        """
#        pass



if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))


