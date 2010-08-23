#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The world object. This hold the map data and provides some convinient methods
to get certain data.

The implementation of this class is very performance critical.

This module will have the IWorld interface and some default IWorld implementations.
Likey one for a topdown world, for a isometric world, side scrolling world and
for a topdown front world.

:TODO:
    add default worlds

"""

__version__ = '$Id: world.py 198 2009-07-12 16:37:11Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import pyknic
import pygame


import utilities
import renderer
from pyknic import gui

#-------------------------------------------------------------------------------

class IWorld(object):
    u"""
    The interface for the world implementations.
    
    Any world should implement this interface, because other 
    components rely on certain methods of the world. The query
    methods are performance critical.
    
    :Ivariables:
        layer : int
            The layer of this world. Normally not used, but if you have more
            than one world on screen at the same time, this is used to
            find the order in which the worlds are traversed by the mouse.
        _entities : `SortedList`
            A sorted list of all entities of thies world. Sort oder: layer, bottom up
        _renderers : `SortedList`
            A worted list of all renderers that render this world. Sort order: layer, top down

    """

    def __init__(self, *args,  **kwargs):
        self._entities = utilities.SortedList(key=lambda ent: ent.layer)
        self._renderers = utilities.SortedList(key=lambda ent: -ent.layer)
        self.layer = 0

    #-- entities --#
    def add_entity(self, entity):
        u"""
        Add entity to the worlds entities.
        
        :Note:
            This method has to be overriden and implemented.
        
        :Parameters:
            entity : `Entity`
                Entity to add.
        """
        raise NotImplementedError()

    def remove_entity(self, entity):
        u"""
        Remove entity from the worlds entities.
        
        :Note:
            This method has to be overriden and implemented.
        
        :Parameters:
            entity : `Entity`
                Entity to remove.
        """
        raise NotImplementedError()

    def get_entities_in_region(self, world_rect):
        u"""
        Returns a ordered list of entites to of this region of the world. 
        The list is ordered by entites layer attribute, bottom up. 
        
        :Note:
            This method has to be overriden and implemented.
        
        :Note: 
            This method is performance critical. 
        
        In a sophisticated implementation 
        there even might be caching and other accelerating structures. But
        this depends heavaly on the internal data structures.
        
        :Parameters:
            world_rect : Rect
                A rect in world coordinates.
        
        """
        raise NotImplementedError()

    #-- renderers --#
    def add_renderer(self, renderer):
        u"""
        Adds a renderer to the world.
        
        :Parameters:
            renderer : `IRenderer`
             The renderer to add to the world.
        """
        self._renderers.append(renderer)
        renderer._world = self

    def remove_renderer(self, renderer):
        u"""
        Removes a renderer from the world.
        
        :Parameters:
            renderer : `IRenderer`
                The renderer to be removed.
        
        """
        if renderer in self._renderers:
            self._renderers.remove(renderer)
            renderer._world = None

    def get_renderers(self):
        u"""
        Returns the `SortedList` of renderers.
        
        :Returns:
            list of renderers, sorted top down.
        """
        return self._renderers

    def render(self, screen_surf, offset=None):
        u"""
        Renders the world through the registered renderers.
        
        :Parameters:
            screen_surf : Surface
                The surface to draw on.
            offset : `Vec3`
                Ignored, but it is there to keep render method signature the the same.
        """
        for rend in reversed(self._renderers):
            rend.render(screen_surf, offset)

    #-- coordinate conversion --#
    def screen_to_world(self, screen_coord):
        u"""
        Converts screen coordinates to world coordinates.
        
        This is normally done in a renderer because only the 
        renderer know screen and world coordinates at the same time.
        
        :Parameters:
            screen_coord : `Vec3`
                The screen coordinates to convert.
        
        :Returns:
            `Vec3` or None (if no conversion could be found)
        
        :Note:
            This method has to be overriden and implemented.
        
        """
        raise NotImplementedError(u'Not implemented method of IWorld')

    def world_to_screen(self, world_coord):
        u"""
        Converts world coordinates to screen coordinates.
        
        This is normally done in a renderer because only the 
        renderer knows about screen and world coordinates.
        
        :Parameters:
            world_coord : `Vec3`
                The world coordinates to convert.
        
        :Returns:
            `Vec3` or None (if no conversion could be found)
        
        :Note:
            This method has to be overriden and implemented.
        
        
        """
        raise NotImplementedError(u'Not implemented method of IWorld')

    def get_entites_from_screen_coords(self, screen_coord):
        u"""
        Return a list of entities at the point in screen coordinates.
        
        :Parameters:
            screen_coord : `Vec3`
                The point on sreen.
        
        :Returns:
            list of `Entity` (might be empty)
        
        :Note:
            This method has to be overriden and implemented.
        
        """
        raise NotImplementedError(u'Not implemented method of IWorld')


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))


