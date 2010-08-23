#!/usr/bin/python
# -*- coding: utf-8 -*-

u"""
Animation support.

Still a bit experimental.

An animation is just a sequence of `AnimationFrame`.

The current animation uses two files written in yaml to define an animation. 
Since the resources can be ordered in many different ways like 
an image strip or spritesheet it has to be that flexible.

First file is the rects file.
The rects file does nothing else as enumerate the rects of the single 
images in an image file. It has basically three parts:

  * The version, just to make sure the loader can load it.
  * 1..n rect enumerations (the number are actually names, you could name each 
    frame differently. A rect is defined by [x, y, w, h].
  * Mapping of image to rects, which images has which rects assoiated with it.

Here an example::

    version: [rects, 0.0.1, pyknic]    # [type, version, vendor]
    rects: {
        #nr: [xpos, ypos, width, height, info]
         1: [ 0  , 0   , 24   , 32    ,],
         2: [24  , 0   , 24   , 32    ,],
         3: [48  , 0   , 24   , 32    ,],
         4: [ 0  , 32  , 24   , 32    ,],
         5: [24  , 32  , 24   , 32    ,],
         6: [48  , 32  , 24   , 32    ,],
         7: [ 0  , 64  , 24   , 32    ,],
         8: [24  , 64  , 24   , 32    ,],
         9: [48  , 64  , 24   , 32    ,],
        10: [ 0  , 96  , 24   , 32    ,],
        11: [24  , 96  , 24   , 32    ,],
        12: [48  , 96  , 24   , 32    ,],
        }
    imagefiles: {hero.png: rects}

The second file actually defines the animation using the rects. It has also
3 parts:

  * the version, also to make sure that the loader understands it
  * default values for different parameters like dt, offset, ...
    and defining the image file and the rects file to use
  * animations defined by which rects enumeration to use and which rect from it
    every frame also can overwrite any default entry by adding that key 
    value-pair to the dict, also the name can be freely chosen

Lets take a look at a real file::

    version   : [animation, 0.0.1, pyknic]    # [type, version, vendor]
    # defaults
    dt        : 0.2           # 1/fps [s]
    offset    : [12, 32]      # (opt) anchor point
    pixelspeed: 10            # (opt) how namy pixels/s it should be moved to match animation speed
    colorkey  : [0, 0, 0]     # might be None
    blendmode : 0             # same as in pygame: BLEND_ADD, ..., see pygame documentation
    # image and rects file
    imagefile : hero.png      # rectsfile has to refere also to this imagefile
    rectsfile : myrects.yaml

    # animations
    up   : [{rects: 2},
            {rects: 3},
            {rects: 2},
            {rects: 1}]

    right: [{rects: 5},
            {rects: 6},
            {rects: 5},
            {rects: 4}]


When you load the animation file with the loader function, it will return a 
dict with the names of the animations as keys and instances of `Animation` as
values in it.

"""

__version__ = '$Id: animation.py 275 2009-08-02 09:16:08Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import pygame

import pyknic
import pyknic.geometry
import pyknic.events


#-------------------------------------------------------------------------------

class AnimationFrame(object):
    u"""
    A single frame of an animation. I basically saves all values a frame could 
    have. They are set to the default values if not overriden.
    """

    def __init__(self, image, time_intervall=0.050, offset=None, blendmode=0):
        u"""
        :Parameters:
            image : Surface
                the image of that frame
            time_intervall : float
                the delay to the next frame of animation
            offset : `Vec3`
                the offset of that frame from the render center
            blendmode : int
                one of the pygame's blend modes of blit
        
        """
        self.image = image
        self.offset = offset
        self.blendmode = blendmode
        if offset is None:
            self.offset = pyknic.geometry.Vec3(0, 0)
        assert(time_intervall > 0)
        self.time_intervall = time_intervall  # [ms] to next frame -> 20 fps
#        self.scale = 1.0
#        self.rotation = 0.0

#-------------------------------------------------------------------------------

def anim_callback(anim):
    u"""
    Example of a end of animation callback function.
    """
    pass

def loop(anim):
    u"""
    For a looping animation, default callback.
    """
    anim.play()

def pingpong(anim):
    u"""
    For a ping pong animation. Could also be done differently.
    """
    if anim.frame == anim._frames[-1]:
        anim._next = itertools.cycle(reversed(self._frames)).next
    else:
        anim._next = itertools.cycle(iter(self._frames)).next

#-------------------------------------------------------------------------------
# TODO: should probably inherit from Spr
class IAnimation(object):
    u"""
    Animation interface. Defines functions of an Animation.
    
    :IVariables:
        event_anim_end : `Signal`
            The signal used for the callback event at the end of the animation.
        scheduler : `GameTime`
            The scheduler used for this animation.
        _frames : list
            list of frames like [IAnimationFrame]
    
    """
    def __init__(self, scheduler, frames, anim_end_callback=loop):
        u"""
        Animation init.
        
        :Parameters:
            scheduler : `GameTime`
                the scheduler to use, should be the scheduler of the state 
                where this animation is created
            frames : list
                list of `AnimationFrame`
            anim_end_callback : function
                function that should be called when animation ends, example: loop(anim)
            scheduler : `GameTime`
                scheduler to be used, if None the `GameTime` from current state is used
        
        """
        #-- needed by entity render --#
        self.source_rect = None
        self.blendmode = 0
        self.offset = pyknic.geometry.Vec3(0, 0)
        #-- event --#
        self.event_anim_end = pyknic.events.Signal('Animation end')
        self.event_anim_end += anim_end_callback
        #-- impl --#
        if not isinstance(frames, list):
            frames = [frames]
        self._frames = frames  # [IAnimationFrame]
        self.scheduler = scheduler

    def play(self):
        u"""
        Start the animation.
        """
        raise NotImplementedError()

    def pause(self):
        u"""
        Pause the animation. Calling play afterwards will continuer from where it was.
        """
        raise NotImplementedError()

    def stop(self):
        u"""
        Stop the animation. Calling play afterwards will start from beginning.
        """
        raise NotImplementedError()

# TODO: always render in Entity?
#    def render(self, screen_surf, offset):
#        raise NotImplementedError()

    def update(self, gdt, gt, dt, t):
        u"""
        Time based updated.
        
        :Parameters:
            gdt : float
                game delta time in seconds
            gt : float
                game time in seconds
            dt : float
                real delta t in seconds
            t : float
                real time
        """
        raise NotImplementedError()

    # could maybe be a property
    def is_running(self):
        u"""
        Returns if animation is currently running.
        
        :Returns:
            bool
            
        """
        raise NotImplementedError()

    # could be a property
    def set_fps(self, fps):
        u"""
        Set the fps the animation should run.
        
        :Parameters:
            fps : frames/second
                fps for the animation
        """
        raise NotImplementedError()

    #TODO: some ways to add/remove/change callback

#-------------------------------------------------------------------------------
import pyknic.timing
import itertools

class Animation(IAnimation):

#TODO: move part of init into interface
    def __init__(self, scheduler, frames, anim_end_callback=loop):
        super(Animation, self).__init__(scheduler, frames, anim_end_callback)
        #-- needed --#
        #-- impl --#
#        self.scale = 1.0
#        self.rotation = 0.0
        # TODO: maybe save tuples with data [(img, offset, blendmode), ...]
        #       for itertools 
        self._next = itertools.cycle(iter(self._frames)).next
        # set to first frame
        self.frame = self._next()
        self.image = self.frame.image
        self.blendmode = self.frame.blendmode
        self.offset = self.frame.offset
        self._running = False

    def play(self):
        if not self._running and len(self._frames) > 1:
            self.scheduler.unschedule(self._update_animation) # just to make sure not to schedule twice
            self.scheduler.schedule(self.frame.time_intervall, self._update_animation)
            self._running = True

    def pause(self):
        if self._running:
            self.scheduler.unschedule(self._update_animation)
            self._running = False

    def stop(self):
        if self._running:
            self.pause()
            # move to last frame
            while self.frame != self._frames[-1]:
                self.frame = self._next()

# TODO: always render in Entity?
#    def render(self, screen_surf, offset):
#        screen_surf.blit(self.image, )

    def _update_animation(self, gdt, gt, dt, t):
        self.frame = self._next()
        self.image = self.frame.image
        self.offset = self.frame.offset
        self.blendmode = self.frame.blendmode
        if self.frame == self._frames[-1]:
            self.pause()
            self.event_anim_end(self)
        else:
            self.scheduler.schedule(self.frame.time_intervall, self._update_animation)

    # could maybe be a property
    def is_running(self):
        return self._running

    # could be a property
    def set_fps(self, fps):
        raise NotImplementedError()

#-------------------------------------------------------------------------------
#import yaml
import thirdparty
import os
import os.path
import pygame
import warnings
import sys

from pyknic.utilities import load_config


def load_animation(scheduler, anim_file_name, version=['animation', '0.0.1', 'pyknic']): # -> {name:animation}
    u"""
    Loads an animation.
    
    :Parameters:
        anim_file_name : string
            name of the animation file
        version : list
            the version of the animation file this loader can load, dont touch!
    
    :Returns:
        dictionary of animations: {name: `Animation`}
    
    :Note:
        can have bugs lurking!
    """
    anim_dir, anim_data = load_config(anim_file_name)
    # test version of animation file
    if version != anim_data['version']:
        raise Exception(u'wrong version, expected %s, got %s' % (str(version), anim_data['version']))
    rects_filename = anim_data['rectsfile']
    rects_data = None

    # for the relative case the directory needs to be inserted to import the module
    sys.path.insert(0, anim_dir)
    rects_dir, rects_data = load_config(rects_filename)
    del sys.path[0]

    # test version of rects file
    rversion = ['rects', '0.0.1', 'pyknic']
    if rversion != rects_data['version']:
        raise Exception(u'wrong version, expected %s, got %s' % (str(rversion), rects_data['version']))

    img_path = os.path.join(anim_dir, anim_data['imagefile'])
    source_image = pygame.image.load(img_path)
    anims = {}

    non_anim_entries = ['version', 'dt', 'offset', 'pixelspeed', 'imagefile', 'rectsfile', 'colorkey', 'alpha', 'blendmode']
    for key in anim_data.keys():
        if key not in non_anim_entries: # filter non animations
            frames = []
            for frame_dict in anim_data[key]: #[{rects:., },{}]:
                dt = frame_dict.get('dt', anim_data['dt'])
                offset = frame_dict.get('offset', anim_data['offset'])
                offset = pyknic.geometry.Vec3(offset[0], offset[1])
                colorkey = frame_dict.get('colorkey', anim_data.get('colorkey', None))
                blendmode = frame_dict.get('blendmode', anim_data.get('blendmode', None))
                if blendmode:
                    try:
                        blendmode = getattr(pygame, blendmode)
                    except:
                        if __debug__:
                            warnings.warn(u'blendmode %s not found' % (blendmode))
                        blendmode = 0
                else:
                    blendmode = 0 # no blend mode
                # filter out which rects list to use
                count = 0
                for fkey in frame_dict.keys():
                    if fkey not in non_anim_entries: #['dt', 'offset', 'pixelspeed', 'imagefile']:
                        if fkey != rects_data['imagefiles'][anim_data['imagefile']]:
                            raise Exception(u'rects file does not cover source image \'%s\'' % (fkey))
                        # fkey is the name of the rects group in the rects file
                        rect_name = frame_dict[fkey]
                        rdata = rects_data[fkey][rect_name]
                        r = pygame.Rect(rdata[:4])
                        img = pygame.Surface(r.size)
                        img.blit(source_image, (0, 0), r)
                        if colorkey:
                            img.set_colorkey(tuple(colorkey))
                        count += 1 # TODO: probably not needed
                        if count > 1:
                            raise Exception(u'only one rect can be defined per frame: %s' % (rect_name))
                        frames.append(AnimationFrame(img, dt, offset, blendmode))
            anims[key] = Animation(scheduler, frames)
    return anims

#-------------------------------------------------------------------------------


if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))


