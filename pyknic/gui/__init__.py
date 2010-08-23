#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: __init__.py 275 2009-08-02 09:16:08Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

from gui import FPSDisplay
import mouse

#TheMouse = mouse.ScreenMouse()

__all__ = ['FPSDisplay']

import pyknic
import pygame.font
from pyknic.geometry import Vec3
pygame.font.init()
import pyknic.animation

#-------------------------------------------------------------------------------

class Label(pyknic.entity.Entity):
    u"""
    A Label gui element. The label is only rendered once (or after any change). 
    Otherwise it is just a image blit.
    
    
    """

    def __init__(self, text, font_color=(0, 0, 0), font_bgd_color=None, font=None):
        u"""
        Constructor.
        
        :Parameters:
            text : string
                The text this label should show.
            font_color : tuple
                Color of the font as a (r, g, b) tuple
            font_bgd_color : tuple
                Background color of the font as a (r, g, b) tuple.
                Defaults to None, a black background color.
            font : pygame.font.Font
                A font object. Defaults to None, the pygame default font is used.
                
        
        """
        super(Label, self).__init__()
        self._text = text
        self.dirty = 1
        self._font = font
        if self._font is None:
            self._font = pygame.font.Font(pygame.font.get_default_font(), 16)
        self._font_color = font_color
        self._font_bgd_color = font_bgd_color
        self.spr = pyknic.entity.Spr()
        self._prerender()

    def _set_text(self, text):
        self._text = text
        self.dirty = 1
    text = property(lambda self: self._text, _set_text, doc=u'''get/set the text''')

    def _set_font(self, font):
        self._font = font
        self.dirty = 1
    font = property(lambda self: self._font, _set_font, doc=u'''get/set the font''')

    def _set_color(self, color):
        self._font_color = color
        self.dirty = 1
    color = property(lambda self: self._font_color, _set_color, doc=u'''get/set font color''')

    def _set_bgd_color(self, color):
        self._font_bgd_color = color
        self.dirty = 1
    background_color = property(lambda self: self._font_bgd_color, _set_bgd_color, doc=u'''get/set background color''')

#    def update(self, gdt, gt, dt, t):
#        pass

    def _prerender(self):
        self.dirty = 0
        if self._font_bgd_color:
            self.spr.image = self._font.render(self._text, 0, self._font_color, self._font_bgd_color)
        else:
            self.spr.image = self._font.render(self._text, 0, self._font_color)
        self.rect = self.spr.image.get_rect(topleft=self.position.as_xy_tuple())

    def render(self, screen_surf, offset=pyknic.geometry.Vec3(0, 0), screen_offset=None):
        u"""
        Renders the label, same as `Entity.render`.
        """
        if self.dirty:
            self._prerender()
#        print '??????', offset, self.text, self.position, self.spr.offset
        super(Label, self).render(screen_surf, offset)

#-------------------------------------------------------------------------------

class Button(pyknic.entity.Entity):
    u"""
    Button implementation.
    """
    class _IButtonState(object):
#        def __init__(_self): super(Button.IButtonState, _self).__init__()
        def hit(_self, self, world_coord):
            return super(Button, self).hit(world_coord)
        def on_screenmouse_enter(_self, self, world_coord, dragging): pass
        def on_screenmouse_leave(_self, self, world_coord, dragging): pass
#        def render(_self, self, screen_surf, offset, screen_offset): pass
        def update(_self, self, gdt, gt, dt, t): pass
        def on_mouse_down(_self, self, pos, button, mods): pass
        def on_mouse_up(_self, self, pos, button, mods): pass
        def exit_state(_self, self): pass
        def enter_state(_self, self): pass
        def on_mouse_up_release(_self, self, pos, button, mods): pass

    class _NormalState(_IButtonState):
        def enter_state(_self, self):
            self.spr = self.state_sprites[0]
            self.spr.play()
            self.rect = self.spr.image.get_rect(topleft=self.position.as_xy_tuple())
        def on_screenmouse_enter(_self, self, world_coord, dragging):
#            print 'btn mouse enter', world_coord, dragging
            if dragging:
                pass
            else:
                self._change_state(self._hover)
        def on_mouse_up(_self, self, pos, button, mods):
            if self.hit(Vec3(*pos)):
                self._change_state(self._hover)

    class _HoverState(_IButtonState): 
        def on_mouse_down(_self, self, pos, button, mods):
            if self.hit(pyknic.geometry.Vec3(*pos)): # TODO: change to world coord?
                self._change_state(self._pressed)
                return True
        def on_screenmouse_leave(_self, self, world_coord, dragging):
            self._change_state(self._normal)
        def enter_state(_self, self):
            self.spr = self.state_sprites[1]
            self.spr.play()
            self.rect = self.spr.image.get_rect(topleft=self.position.as_xy_tuple())

    class _PressedState(_IButtonState):
#        def __init__(_self): super(Button.PressedState, _self).__init__()
        def on_mouse_up(_self, self, pos, button, mods):
            if self.hit(pos): # TODO: change to world coord?
                self._change_state(self._hover)
                self.event_click(self)
            else:
                self._change_state(self._normal)
        def enter_state(_self, self):
            self.spr = self.state_sprites[2]
            self.spr.play()
            self.rect = self.spr.image.get_rect(topleft=self.position.as_xy_tuple())
        def on_mouse_up_release(_self, self, pos, button, mods):
            if self.hit(pos):
                _self.on_mouse_up(self, pos, button, mods)
            else:
                self._change_state(self._normal)
        def on_screenmouse_enter(_self, self, world_coord, dragging):
            self.spr = self.state_sprites[2]
            self.spr.play()
            self.rect = self.spr.image.get_rect(topleft=self.position.as_xy_tuple())
        def on_screenmouse_leave(_self, self, world_coord, dragging):
            self.spr = self.state_sprites[0]
            self.spr.play()
            self.rect = self.spr.image.get_rect(topleft=self.position.as_xy_tuple())

    class _DisabledState(_IButtonState): 
#        def __init__(_self): super(Button.DisabledState, _self).__init__()
        def enter_state(_self, self):
            self.spr = self.state_sprites[3]
            self.spr.play()
            self.rect = self.spr.image.get_rect(topleft=self.position.as_xy_tuple())
        def on_mouse_down(_self, self, pos, button, mods):
            if self.hit(pyknic.geometry.Vec3(*pos)): # TODO: change to world coord?
                return True

    _normal = _NormalState()
    _hover = _HoverState()
    _pressed = _PressedState()
    _disabled = _DisabledState()

    state_sprites = [] #TODO: add default state_sprites # normal, hover, pressed, disabled

    def __init__(self, state, position, text='', size=None, state_sprites=None):
        u"""
        
        :Parameters:
            size : tuple
                (w, h)
            state_sprites : list of sprites
                normal, hover, pressed, disabled
                has to be `Animation` sprites in which case the animation is played.
        
        """
        super(Button, self).__init__(position=position, spr=pyknic.entity.Spr())
        
        assert len(state_sprites) >= 4
        assert isinstance(state_sprites, list)
        self.state_sprites = state_sprites
        self.event_click = pyknic.events.Signal(u'button pressed')
        self._current_state = None
        self._change_state(self._normal)
        self.layer = 10000
        self.label = Label(text)
        self.label_offset = pyknic.geometry.Vec3(5, 5)
        state.screen_mouse.events.screenmouse_button_up += self.on_screenmouse_button_up_release

    def hit(self, world_coord):
        return self._current_state.hit(self, world_coord)

    def on_screenmouse_enter(self, world_coord, dragging):
        self._current_state.on_screenmouse_enter(self, world_coord, dragging)

    def on_screenmouse_leave(self, world_coord, dragging):
        self._current_state.on_screenmouse_leave(self, world_coord, dragging)

    def on_screenmouse_button_down(self, pos, buttons, mods):
        return self._current_state.on_mouse_down(self, pos, buttons, mods)

    def on_screenmouse_button_up_release(self, pos, buttons, mods):
        self._current_state.on_mouse_up_release(self, pos, buttons, mods)

    def render(self, screen_surface, offset=pyknic.geometry.Vec3(0, 0), screen_offset=None):
        super(Button, self).render(screen_surface, offset, screen_offset)
        r = pygame.Rect(self.rect)
        r.topleft = (self.position - offset).as_xy_tuple()
        print r, self.position, offset
        btn_surf = screen_surface.subsurface(r)
#        self.label.render(btn_surf, self.label_offset, None)
        self.label.render(btn_surf, -self.label_offset, None)

    def update(self, gdt, gt, dt, t):
        self._current_state.update(self, gdt, gt, dt, t)
        # update collision rect
        self.rect.center = self.position.as_xy_tuple()

    def _change_state(self, new_state):
        if self._current_state:
            self._current_state.exit_state(self)
        self._current_state = new_state
        self._current_state.enter_state(self)

    def _set_enable(self, value):
        if value:
            self._change_state(self._normal)
        else:
            self._change_state(self._disabled)
    enable = property(lambda self: self._current_state != self._disabled, _set_enable, doc=u'''enbale/disable control''')

#-------------------------------------------------------------------------------

if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))

