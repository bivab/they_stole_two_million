#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module contains some convinient functions and classes. They should help 
make certain tasks easier.
"""

__version__ = '$Id: utilities.py 275 2009-08-02 09:16:08Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import os
import glob
import inspect

import pygame
import pyknic
import pyknic.events

#-------------------------------------------------------------------------------

class Direction(object):
    u"""
    Direction constants:
    
     * E  = 0.0
     * SE = 0.5
     * S  = 1.0
     * SW = 1.5
     * W  = 2.0
     * NW = 2.5
     * N  = 3.0
     * NE = 3.5
    
    They should be used to compare with the `get_8dir()`, get_4dir() and get_dir() 
    functions.
    
    """
    E, SE, S, SW, W, NW, N, NE = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]

def get_8dir(degrees):
    u"""
    Calculates the direction from the angle in degrees.
    :rtype: `Direction`: E, SE, S, SW, W, NW, N, NE
    """
    # upate look direction
    return int(degrees / 45.0 + 0.5) % 8 / 2.

def get_4dir(degrees):
    u"""
    Calculates the direction from the angle in degrees.
    :rtype: `Direction` E, S, W, N
    """
    # upate look direction
    return int(degrees / 90.0 + 0.5) % 4

def get_dir(degrees, num_dirs=4):
    u"""
    Calculates the direction from the angle in degrees.
    :rtype: the direction coded into a floating point number depending 
    on how many directions you use. For 4 directions it would be:
    
         * E = 0.0
         * S = 1.0
         * W = 2.0
         * N = 3.0

    Using 8 directions adds the SE, SW, NW and NE which would result in 
    the additional directions:
     
         * SE = 0.5
         * SW = 1.5
         * NW = 2.5
         * NE = 3.5

    If you use 16 direction you get 0.25, 1.5, 1.75 and so on.
    """
    return int(degrees / (360.0 / num_dirs) + 0.5) % num_dirs / (num_dirs / 4.0)

#-------------------------------------------------------------------------------

class FrameCounter(object):
    u"""
    The FrameCounter emits an event after the specified number of frames have 
    been count.
    
    :Ivariables:
        event_frames_elapsed : `Signal`
            It is fired after 'num' calls to update.
    
    """

    def __init__(self, num):
        u"""
        :Parameters:
            num : int
                number of frames to wait untile firing the event_frames_elapsed again.
        """
        self._num = int(num)
        self._count = 0
        self.event_frames_elapsed = pyknic.events.Signal(u'num(%i)_frames_elapsed id(%h)' %(self._num, id(self)))

    def update(self, gdt, gt, dt, t):
        u"""
        This method needs to be called every frame to internal count can be updated.
        """
        self._count += 1
        if self._count >= self._num:
            self.event_frames_elapsed()
            self._count = 0

#-------------------------------------------------------------------------------

# TODO: for *.pyw versions it should be routed to stdout
def DLOG(message):
    u"""
    instead using print all the time, this prints the message adding
    information where in the code it was printed.
    """
    if __debug__:
        frame = None
        try:
            frame = inspect.stack()[1]
            print "DEBUG : %s [%s, %s]" % (message, frame[1], frame[2])
        except:
            print "DEBUG : %s" % message
        finally:
            del frame

#-------------------------------------------------------------------------------
def merge_configs(default, user):
    u"""
    Merges the defautl config file with a custom file. The default 
    values are overwritten by the custom values
    :rtype: dict
    """
    if isinstance(user,dict) and isinstance(default,dict):
        for k,v in default.iteritems():
            if k not in user:
                user[k] = v
            else:
                user[k] = merge_configs(user[k],v)
    return user



# TODO: put those function into utils? because same as in animation.py!!!
def _my_import(file_name):
    u"""
    Helper function to load module from any directory extracted from the filename.
    
    :Parameters:
        file_name : string
            The filenmae of the module, has to end with .py
    
    """
    mod_dir = os.path.dirname(file_name)
    os.sys.path.insert(0, mod_dir)
    file_name = file_name.rsplit('.', 1)[0]
    file_name = os.path.split(file_name)[1]
    if __debug__: print u"importing config '%s' in directory '%s'" % (file_name, mod_dir)
    mod = __import__(file_name)
    del os.sys.path[0]
    return mod_dir, mod

def load_config(file_name):
    u"""
    TODO: docs
    """
    mod_dir, mod = _my_import(file_name)
    data = {}
    for key in [var for var in dir(mod) if not var.startswith('__')]:
        data[key] = getattr(mod, key)
    return mod_dir, data

#-------------------------------------------------------------------------------
def take_screenshot(save_path, filename='screenshot'):
    u"""
    Saves a screenshot to disk. The saved images are automatically
    numbered. If there are already files named the same way in the 
    directory, it weill continue the numbering (it does not overwrite files).
    The directory where the files are saved can be specified in the 
    configuration as::
    
        paths:
            screenshots: your_screenshots_save_path
    
    The path is relative to the current working directory.
    A pygame screen needs to be initialized to save screenshots sucessfully.
    
    :Parameters:
        save_path : string
            directory where to save the screenshots, usually taken from 
            the config
        filename : string
            the filename prefix for the saved file
    
    """
    extenstion = 'png'
    save_path = os.path.abspath(save_path)
    print save_path
    if not os.path.exists(save_path):
        try:
            os.makedirs(save_path)
        except Exception, e:
            DLOG(e)
            return
    query = os.path.join(save_path, '%s_*.%s' % (filename, extenstion))
    image_names = glob.iglob(query)
    num = 0
    for image_name_full in image_names:
        image_name = os.path.split(image_name_full)[1]
        name, imgext = image_name.split('.')
        prefix, img_num = name.split('_')
        if int(img_num)>num:
            num = int(img_num)
    new_name = os.path.join(save_path,'%s_%05d.%s' % (filename, num + 1, extenstion))
    if pygame.display.get_init():
        pygame.image.save(pygame.display.get_surface(), new_name)
        DLOG('saved screenshot at %s' % new_name)

#-------------------------------------------------------------------------------


class SortedList(list):
    u"""
    A fast sorted list implementation. It stores the items in a sorted way, sorted by the specified key.
    Trick: to reverse the sorting you can just negate the key:
    
    Instead of using::
    
        key = lambda x : x.layer
    
    you would use::
    
        key = lambda x : -x.layer
    
    to sort in reverse order.
    """

    def __init__(self, other_iterable=[], key = None):
        u"""
        Constructor.
        
        :Parameters:
            other_iterable : iterable
                A iterable containing elements to sort. Does the same as::
                
                    s = SortedList()
                    s.merge(other_iterable)
                
            key : function
                A function that return the attribute to compare e.g. lambda x: x.layer
                if key is None then the elements itselfs are used (using lambda x: x)
        """
        self._key = key
        if key is None:
            self._key = lambda x: x
        self.extend(other_iterable)

    def insort(self, item):
        u"""
        Sorts in the item.
        
        :Parameters:
            item : object
                Inserts a item into the list, same as append. The item should
                have same attributes as needed by the key function.
        """
        self.extend([item])

    append = insort

    def index(self, item, low=None, high=None):
        u"""
        Returns index of the item or raises ValueError if the item is not found.
        
        :Parameters:
            low : int
                low is the lower bound, low >= 0, default: 0
            high : int
                high is the upper bound, high <= len(self), default: len(self)
                
        :rtype: int
        """
        if low is None:
            low = 0
        if high is None:
            high = len(self)
        key = self._key
        item_key = key(item)
        assert low >= 0
        assert high <= len(self)
        # bisect to find lowest item
        while low < high:
            mid = (low + high) // 2
            if key(self[mid]) < item_key:
                low = mid + 1
            else:
                high = mid
        # if not found raise ValueError
        if low == len(self):
            raise ValueError(u'item not found')
        # return index
        # worst case it searches the entire list, but might never happen
        return super(SortedList, self).index(item, low)

    def extend(self, iterable):
        u"""
        Insorts the items into this SortedList::
        
            a.extend(b) inserts the items of b into a using the sort key of a.
        
        :Parameters:
            iterable : iterable
                items to insort
        
        """
        # optimizations
        key = self._key 
        super_insert = super(SortedList, self).insert
        for item in iterable:
            item_key = key(item)
            # bisect algorithmus to insert at right position
            low = 0
            high = len(self)
            while(low < high):
                mid = (low + high) // 2
                if item_key < key(self[mid]):
                    high = mid
                else:
                    low = mid+1
            # finally insert it (use insert of list)
            super_insert(low, item)

    def update(self):
        u"""
        If for any reason the sort order has changed, this method
        re-sorts it again.
        
        :note: use with care because of overhead!
        """
        itemslist = list(self)
        del self[:]
        self.extend(itemslist)

    def clear(self):
        u"""
        Removes all items from the SortedList. Same as::
        
            del sorted_list[:]
        
        """
        del self[:]

    def __add__(self, other):
        u"""
        allows for c = a + b
        returns the mixed list (sorted by a's key)
        
        :rtype: `SortedList`

        """
        return self.__class__(self, self._key).extend(other)

    def __iadd__(self, other):
        u"""allows to write a += b
        This is basically the same as using a.extend(b)"""
        self.extend(other)
        return self

    def __contains__(self, item):
        u"""test if a item is in the list"""
        try:
            self.index(item)
            return True
        except ValueError:
            return False

    # these methods are not allowed because they would cause the list to be unsorted

    def __mul__(self, scalar):
        u"""not allowed because would change order"""
        raise Exception(u'not allowed to multiply a SortedList, use extend() instead')
    __rmul__ = __mul__
    __imul__ = __mul__

    def insert(self, idx, value):
        u"""not allowed because would change order"""
        raise Exception(u'insert not allowed for SortedList, use insort() or append()')

    def __setslice__(self, idx, jdx, slice):
        u"""not allowed because would change order"""
        raise Exception(u'assignment to slice not allowed for SortedList, use insort() or append()')

    def __setitem__(self, key, value):
        u"""not allowed because would change order"""
        raise Exception(u'item assignemt not allowed for SortedList, use insort() or append()')

    def sort(self, cmp=None, key=None, reverse=False):
        u"""not allowed because would change order"""
        raise Exception(u'SortedList is already sorted, use new_list = SortedList(old_list, new_key) to sort differently')

    def reverse(self):
        u"""not allowed because would change order, see SortedList how to reverse it."""
        raise Exception(u'reverse not allowed, see doc of SortedList how to reverse it.')


if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))

