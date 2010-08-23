#!/usr/bin/python
# -*- coding: utf-8 -*-

u"""
Pyknic
======

Pyknic is boilerplate code for writing simple games.

It has following features so far:

    * time based *animation* of sprites
    * abstract *world* modeling
    * *renderer* (like camera)
    * *scrolling*
    * *collision* detection
    * *vector* class
    * *scene management* (trhough states)
    * *maploader* for tmx files produced by tiled (see [http://mapeditor.org/])
    * (minimalistic) *gui* (actually only a button so far, should be easy to extend)
    * *event system* using Signal s and handlers
    * *time* related functions like: *scheduler, slow motion*
    * *custom mouse sprite* (with additional enter/leave and drag events)

:Variables:
    version : string
        version string of this pyknic package
    vernum : list
        list of integers representing the version, generate from the `version`, 
        easier to campare

:Undocumented:
    QUIT
    ACTIVEEVENT
    KEYDOWN
    KEYUP
    MOUSEMOTION
    MOUSEBUTTONUP
    MOUSEBUTTONDOWN
    JOYAXISMOTION
    JOYBALLMOTION
    JOYHATMOTION
    JOYBUTTONUP
    JOYBUTTONDOWN
    VIDEORESIZE
    VIDEOEXPOSE
"""

__version__ = '$Id: __init__.py 315 2009-08-30 05:24:49Z dr0iddr0id $'

import os.path
import sys



if __debug__:
    import sys
    try:
        # setting up pyknic directory
        import pyknic
        _p = os.path.split(str(pyknic).split()[3].split('\'')[1])[0]
    except:
        _p = u'UNKNOWN DIRECTORY'
    sys.stdout.write(u'%s loading from %s \n' % (__name__, _p))
    import time
    _start_time = time.time()




import pygame

# optimizations
from pygame.locals import QUIT
from pygame.locals import ACTIVEEVENT
from pygame.locals import KEYDOWN
from pygame.locals import KEYUP
from pygame.locals import MOUSEMOTION
from pygame.locals import MOUSEBUTTONUP
from pygame.locals import MOUSEBUTTONDOWN
from pygame.locals import JOYAXISMOTION
from pygame.locals import JOYBALLMOTION
from pygame.locals import JOYHATMOTION
from pygame.locals import JOYBUTTONUP
from pygame.locals import JOYBUTTONDOWN
from pygame.locals import VIDEORESIZE
from pygame.locals import VIDEOEXPOSE

# import subpackages
import pyknic.geometry
import pyknic.gui
import pyknic.resources
import pyknic.thirdparty
import pyknic.utilities
# import submodules
import pyknic.animation
import pyknic.collision
import pyknic.default
import pyknic.entity
import pyknic.events
import pyknic.renderer
import pyknic.timing
import pyknic.world


#------------------------------------------------------------------------------


class VersionMismatchException(Exception):
    u"""
    Exception that should be raised when expected version differes from the 
    version request.
    """
    pass

class VersionFormatException(Exception):
    u"""
    Exception that should be raised when the version formatting is wrong.
    """
    pass

class Version(object):
    u"""
    Version class. Allows comparision between Version instances.
    
    :IVariables:
        VERSION_DESCRIPTION_ORDER : dict
            This dict translates the descr into a number, so a natural 
            ordering is created. Used internally for vernum property.
    
    """

    VERSION_DESCRIPTION_ORDER = {
                    'dev':-3,
                    'snapshot':-3,
                    'alpha':-2,
                    'beta':-1,
                    'release':0,
                    'patch':1,
                    'pyweek9':-999
                    }

    def __init__(self, version_string):
        u"""
        Constructor.
        
        :Parameters:
            version_string : string
                String representation of the Version. It should be::
                    
                    major.minor.micro.descr
                                              major: incompatible api changes
                                              minor: compatible api changes
                                              micro: bug fixes and small changes
                                              descr: description
        
        The description can be one of the following 
        (ordered from lower to higher version):
        
            * dev
            * snapshot
            * alpha
            * beta
            * release
            * patch
        
        A `VersionFormatException` is raised if the version formating is wrong. 
        Versions can be compared using the normal comparing operators.
        """
        self._version = version_string
        vernum = [0, 0, 0, 0]
        for idx, s in enumerate(version_string.split('.')):
            if idx==3:
                vernum[idx] = self.VERSION_DESCRIPTION_ORDER.get(s.lower(), 0)
            else:
                try:
                    vernum[idx] = int(s)
                except ValueError:
                    raise VersionFormatException(u'Only digits are allowed for major.minor.micro')
        self._vernum = vernum

    version = property(lambda self: self._version, doc=u'''read-only, version as string''')
    vernum = property(lambda self: self._vernum, doc=u'''read-only, list of version numbers''')

    def __str__(self):
        return u"<%s %s>" % (self.__class__.__name__, self.version)

    def __cmp__(self, other):
        return cmp(self.vernum, other.vernum)

class VersionRangeFormatException(Exception):
    u"""
    Should be raised, if the version range string has wrong format.
    """
    pass

class VersionRange(object):
    u"""
    The version range class. Allows to define a version range and lets check 
    if a `Version` is contained in the range using the *in* operator.
    """
# [1.0.0, 2)  <=>  1.0.0<= version < 2
# [1] == 1 == 1.0 == 1.0.0  <==> 1 <= version <= 1.0.0.5

    def __init__(self, version_range_string):
        u"""
        Constructor.
        
        :Parameters:
            version_range_string : string
                A string of the form::
                
                    [0.0.0.dev, 1.0) same as 0.0.0.dev <= version < 1.0
                    [0.0.0.dev, 1.0] same as 0.0.0.dev <= version <= 1.0
                    (0.0.0.dev, 1.0] same as 0.0.0.dev < version <= 1.0
                    (0.0.0.dev, 1.0) same as 0.0.0.dev < version < 1.0
                    
                    or
                    
                    [1.0] same as version == 1.0 or 1.0 <= version <= 1.0
        
        To check if a version is in the range, just it liek this::
            
            if ver in ver_range: pass
        
        """
        from operator import lt, le
        if version_range_string[0] == '[':
            self._left_op = le
        elif version_range_string[0] == '(':
            self._left_op = lt
        else:
            raise VersionRangeFormatException(u'Versionrange has to start with [ or (')
        if version_range_string[-1] == ']':
            self._right_op = le
        elif version_range_string[-1] == ')':
            self._right_op = lt
        else:
            raise VersionRangeFormatException(u'Versionrange has to end with ] or )')
        if ',' in version_range_string:
            self._left_version, self._right_version = version_range_string[1:-1].split(',')
        else:
            self._left_version = self._right_version = version_range_string[1:-1]
        self._left_version = Version(self._left_version)
        self._right_version = Version(self._right_version)

    def __contains__(self, version):
        return self._left_op(self._left_version, version) and self._right_op(version, self._right_version)

version = u'2.0.1.pyweek9'  # major.minor.micro.descr
                            #                           major: incompatible api changes
                            #                           minor: compatible api changes
                            #                           micro: bug fixes and small changes
                            #                           descr: description

vernum = Version(version).vernum

#-- verions checks --#
# pygame
if list(pygame.vernum) < [1, 8, 1]:
    raise Exception(u'pygame 1.8.1 or higher is needed pyknic v%s, your version is \'%s\'' % (pygame.ver, version))

# python
if list(sys.version_info[:3]) < [2, 5, 1]:
    raise Exception(u'python 2.5.1 or higher is needed for pyknic v%s, your python version is \'%s\'' % (os.path.sys.version, version))

#------------------------------------------------------------------------------

class Configuration(object):
    u"""
    The class that holds the configuration data from the configuration file.
    The values can be get/set through keys, like a dictionary.
    
    See `utilities.load_config` for how to load a configuration manually.
    :TODO: save_config
    """

    def __init__(self, yaml_data = {}):
        self._data = yaml_data

    def _get_element(self, branch, context):
        if len(context) == 0:
            return Configuration(branch)
        key = context.pop(0)
        if not branch.has_key(key):
            return Configuration()
        item = branch[key]
        if isinstance(item, dict):
            return self._get_element(item, context)
        return item

    def __getitem__(self, key):
        return self._get_element(self._data, key.split('.'))

    def __setitem__(self, key, val):
        pass

    def __delitem__(self, key):
        pass

    def __repr__(self):
        return str(self._data)
        
    def __nonzero__(self):
        if self._data != {}:
            return True
        return False

#------------------------------------------------------------------------------

class Application(object):
    u"""
    Represents the current state of a Pygame application maintains the flow of
    the pipeline.

    An application can have different states (see State). It provides methods to 
    manage and change from one state to another state. For example one could 
    have a menu state, a play state, a credits state, etc. The states are 
    like screens. The state changes are deferred until they are applied. This 
    is done because if the state changes in the middle of processing and need
    data from the current state this could go wrong. This means also that after
    calling a state changing method one iteration of the main loop has to 
    complete before the change takes place.
    
    
    """

    # internal commands
    _POP, _PUSH, _REPLACE = range(3)

    def __init__(self, first_state, version_range=u"[1.0.0.pyweek9, 1.0.999.pyweek9]", config=None):
        u"""
        Sets up the only App class, should only be instanciated once
        
        :Parameters:
            first_state : `State`
                the first state, instance of State
            version_range : string
                description of a version range, see `VersionRange`, for pyweek9 this 
                defaults to [1.0.0.pyweek9, 1.0.999.pyweek9]
            config : string
                filename of custom config, if None is provided or for missing entries the default values from the deafult config are applied.
        
        """
        # check version
        if __debug__: print "App __init__"
        if Version(version) not in VersionRange(version_range):
            msg = u'This version %s is not in version range %s, a version in the range is needed to run this program (module used: %s)' %(version, version_range, sys.argv[0])
            raise VersionMismatchException(msg)
        if __debug__: print "App __init__ version check done"
        # attr
        self._config = self._load_settings(config)
        if __debug__: print "App __init__ loaded config done"
        self._time = 0.0
        self._framerate = self._config['display.fps']
        self._cur_state = first_state
#        global AppState
#        AppState = first_state
        self._states = [first_state]
        self._commands = []
        self._running = True
        self._start_drag = False
        self._dragging = False
        if __debug__: print "App __init__ done"

    #-- properties --#
    config = property(lambda self: self._config, doc=u"Read-Only, returns the current `Configuration`")
    state = property(lambda self: self._cur_state, doc=u"Read-Only, returns the current `State` of the app")

    screen = property(lambda self: pygame.display.get_surface(), doc="uRead-Only, returns pygame.Surface, same as pygame.display.get_surface()")

    framerate = property(lambda self: self._framerate, doc=u"Read-Only, the framerate the game runs (from the config)")
    time = property(lambda self: self._time, doc=u"Read-Only, current time of `Application` in [s] (has some error because spikes are filtered)")
    clock = property(lambda self: self._clock, doc=u"Read-Only, returns the clock, pygame.Clock()")

    #-- private --#
    def _load_settings(self, filename):
        u"""protected method for loading the configuration files"""
#        p = os.path.dirname(__file__)
#        default = os.path.abspath(os.path.join(p, 'default.yaml'))
#        default = open(default).read()
#        config = yaml.load(default)
#        _d, config = load_config(os.path.join(pyknic_directory, 'default.yaml'))
        config = {}
        for name in [var for var in dir(pyknic.default) if not var.startswith('__')]:
            config[name] = getattr(pyknic.default, name)
        if filename:
            path = os.path.abspath(filename)
#            yaml_text = open(path).read()
#            yaml_data = yaml.load(yaml_text)
            if __debug__: print "loading config from %s" % path
            _d, yaml_data = pyknic.utilities.load_config(path)
            config = pyknic.utilities.merge_configs(config, yaml_data)
        return Configuration(config)

    def _update_states(self):
        u"""protected method, realizes the state change by processing the
        commands in the command queue"""
        # deferred state updating
        while self._commands:
            cmd, new_state = self._commands.pop(0)
            if cmd == self._POP:
                self._cur_state.on_exit()
                self._states.pop(0)
                if self._states:
                    self._cur_state = self._states[0]
                    self._cur_state.on_resume()
                else:
                    self._running = False
            elif cmd == self._PUSH:
                self._running = True
                self._cur_state.on_pause()
                self._cur_state = new_state
                self._cur_state.the_app = self
                self._cur_state.on_init(self)
                self._states.insert(0, new_state)
            elif cmd == self._REPLACE:
                self._cur_state.on_exit()
                self._states.pop(0)
                self._cur_state = new_state
                self._cur_state.the_app = self
                self._cur_state.on_init(self)
                self._states.insert(0, new_state)
#        global AppState
#        AppState = self._cur_state

    #-- state handling --#
    def push_state(self, new_state):
        u"""Push a state over the current one. The change occures deferred."""
        self._commands.append((self._PUSH, new_state))

    def pop_state(self):
        u"""Pop a state. The change occures deferred. If no state is left,
        the application will quit."""
        self._commands.append((self._POP, None))

    def replace_state(self, new_state):
        u"""Replace the current state with the new one. The change occures deferred."""
        self._commands.append((self._REPLACE, new_state))

#TODO: switch means exchange two states
#    def switch_state(self, ):

    def clear_states(self):
        u"""Removes all states. Make sure to push a new state or otherwise the 
        app will exit because no state is left. The occure deferred."""
        while self._states:
            self.pop()

    #-- app functions --#
    def init(self):
        u"""
        Called after pygame init and before the actual main loop.
        """
        pass

    def exit(self):
        u"""
        Called when the main loop exits.
        """
        pass

    def quit(self):
        u"""
        Quit the main loop.
        """
        self._running = False

    #-- pygame specific --#
    def _init_pygame(self):
        cfg = self.config['display']
        w, h = cfg['width'], cfg['height']
        caption = cfg['caption']
        if __debug__:
            caption += ' [__debug__]'
        if __debug__: print 'pygame init done'
        pygame.init()
        if __debug__: print 'pygame init done'
        pygame.display.set_caption(caption)
        if __debug__: print 'pygame set display done'
        # TODO: icon loading
        try:
            icon = pygame.image.load(cfg['icon'])
            if __debug__: print u"custom icon loaded"
        except:
            import base64
            import gzip
            import StringIO
            import pyknic.resources
            gzipper = gzip.GzipFile(fileobj=StringIO.StringIO(base64.b64decode(pyknic.resources.pyknic_logo_32x32)), mode='rb')
            s_dec = gzipper.read()
            gzipper.close()
            icon = pygame.image.fromstring(s_dec, (32, 32), 'RGBA')
            if __debug__: print u"loading default icon done!"
        pygame.display.set_icon(icon)
        args = [(w, h)] #, pygame.DOUBLEBUF|pygame.HWSURFACE]
        if cfg['flags']:
            pass # args.append(flags)
        self._screen = pygame.display.set_mode(*args)
        if __debug__: print 'pygame set mode done'
        self._clock = pygame.time.Clock()
        if __debug__: print u"pygame init done"

    def run(self):
        u"""
        Run the App. Start the main loop.
        """
        # init 
        if __debug__: print 'App run start'
        self._init_pygame()
        self.init()
        if __debug__: print 'App run state on_init'
        self._cur_state.the_app = self
        self._cur_state.on_init(self)
        if __debug__: print 'App run state on_init done'
        # optimizations
        clock_tick = self.clock.tick
        state = self._cur_state
        state_game_time_update = state.game_time.update
#        state_render = state.render
        dispatch_events = self._dispatch_events
        framerate = self._framerate
        # main loop
        while self._running:
            dt = min(200, clock_tick(framerate)) / 1000.0
            self._time += dt
            dispatch_events()
            state_game_time_update(dt, self._time)
#            state_render()
            # update the state
            if self._commands:
                self._update_states()
                state = self._cur_state
                state_game_time_update =  state.game_time.update
#                state_render = state.render
        # finished
        if __debug__: print 'App run done'
        self.exit()

    def _dispatch_events(self, get_events=pygame.event.get):
        u"""
        Internal use. pygame specific implementation for translating events.
        """
        cur_state_events = self._cur_state.events # optimization
        screen_mouse = self._cur_state.screen_mouse
        for event in get_events():
            # TODO: use event any?
            #cur_state.any(event)
            event_type = event.type # optimization
            #-- events should be arranged most frequent first --#
##            if event_type == EVENT_SCHEDULE_ID:
##                self._schedule_cb()
##            elif event_type == EVENT_UPDDATE_ID:
##                dt = args[1] - self._time
##                if dt > 0:
##                    if __debug__:
##                        self._num_updates += 1
##                        sys.stdout.write(u"dt: %i  t: %i  _t:  %i  fps: %f" %(dt, args[1], self._time, 1000./dt if dt>0 else 0))
##                    # TODO: filter to big dt values?
##                    # self._time = get_ticks() instead of t ? no you loose time
##                    self._update(dt, args[1])
##                    self._time = args[1]
            #-- event --#
            cur_state_events.raw_event(event)
            #-- mouse --#
            #    pygame.MOUSEMOTION,    #  pos, rel, buttons
            if event_type == MOUSEMOTION:
                if event.buttons == (0, 0, 0): # unpressed generate a motion event
#                    screen_mouse.on_mouse_motion(event.pos, event.rel)
                    cur_state_events.mouse_motion(event.pos, event.rel)
                else: # pressed generate a drag event
                    if self._start_drag:
                        data = self._start_drag
#                        screen_mouse.on_drag_start(*data)
                        cur_state_events.mouse_drag_start(*data)
                        self._start_drag = False
                        self._dragging = True
#                    screen_mouse.on_mouse_drag(event.pos, event.rel, event.buttons, pygame.key.get_mods())
                    cur_state_events.mouse_drag(event.pos, event.rel, event.buttons, pygame.key.get_mods())
            #    pygame.MOUSEBUTTONUP,  #  pos, button
            elif event_type == MOUSEBUTTONUP:
                if self._dragging:
                    self._dragging = False
#                    screen_mouse.on_drag_drop(event.pos, event.button, pygame.key.get_mods())
                    cur_state_events.mouse_drag_drop(event.pos, event.button, pygame.key.get_mods())
                cur_state_events.mouse_button_up(event.pos, event.button, pygame.key.get_mods())
            #    pygame.MOUSEBUTTONDOWN,#  pos, button
            elif event_type == MOUSEBUTTONDOWN:
                pos, btns, mod = event.pos, event.button, pygame.key.get_mods()
                self._start_drag = (pos, btns, mod)
                cur_state_events.mouse_button_down(pos, btns, mod)
            
            #-- keyboard --#
            #    pygame.KEYDOWN,        #  unicode, key, mod
            elif event_type == KEYDOWN:
                cur_state_events.key_down(event.key, event.mod, event.unicode)
            #    pygame.KEYUP,          #  key, mod
            elif event_type == KEYUP:
                cur_state_events.key_up(event.key, event.mod)
            #-- joystick --#
            #    pygame.JOYAXISMOTION,  #  joy, axis, value
            elif event_type == JOYAXISMOTION:
                cur_state_events.joy_axis_motion(event.joy, event.axis, event.value)
            #    pygame.JOYBALLMOTION,  #  joy, ball, rel
            elif event_type == JOYBALLMOTION:
                cur_state_events.joy_ball_motion(event.joy, event.ball, event.rel)
            #    pygame.JOYHATMOTION,   #  joy, hat, value
            elif event_type == JOYHATMOTION:
                cur_state_events.joy_hat_motion(event.joy, event.hat, event.value)
            #    pygame.JOYBUTTONUP,    #  joy, button
            elif event_type == JOYBUTTONUP:
                cur_state_events.joy_button_up(event.joy, event.button)
            #    pygame.JOYBUTTONDOWN,  #  joy, button
            elif event_type == JOYBUTTONDOWN:
                cur_state_events.joy_button_down(event.joy, event.button)
            
            #    pygame.QUIT,           #  none
            elif event_type == QUIT:
                cur_state_events.quit(self)
            #    pygame.ACTIVEEVENT,    #  gain, state
            elif event_type == ACTIVEEVENT:
                cur_state_events.active_event(event.state, event.gain)
                if (event.state & 0x1): # mouse bit
                    if event.gain: # mouse enter
                        cur_state_events.mouse_enter(pygame.mouse.get_pos())
                    else: # mouse leave
                        cur_state_events.mouse_leave(pygame.mouse.get_pos())
                # Note: this works unreliable!!
#                            if (event.state & 0x4): # app bit (iconify/restore)
#                                if event.gain: # restored
#                                    pass 
#                                else: # iconified
#                                    pass 
                if (event.state & 0x2): # key bit
                    if event.gain: # get keyboard focus
                        cur_state_events.activate()
                    else: # lost keyboard focus
                        cur_state_events.deactivate()
            
            #-- video --#
            #    pygame.VIDEORESIZE,    #  size, w, h
            elif event_type == VIDEORESIZE:
                cur_state_events.video_resize(event.size, event.w, event.h)
            #    pygame.VIDEOEXPOSE,    #  none
            elif event_type == VIDEOEXPOSE:
                cur_state_events.video_expose()
            else:
                cur_state_events.unknown(event)


#-------------------------------------------------------------------------------

class State(object):
    u"""
    A state of the App. Should be inherited.
    
    :Ivariables:
    
        events : `SignalProvider`
            Provides Signals to hook up, per default a state has:
            
                * **raw_event( pygame.event.Event event)** - just the raw event, fired before any other event
                * **mouse_motion((int, int) pos, (int, int) rel)** - tuple of integers in screen coordinates
                * **mouse_drag_start(data)** - data is a tuple containing (pos, btns, mod) as given by pygame event, fired after a mouse_button_down
                * **mouse_drag((int int) pos, (int, int) rel, (int, int, int) buttons, int mods)** - as long at least one button is pressed this event is fired instead of mouse_motion
                * **mouse_drag_drop((int, int) pos, (int, int, int) button, int mods)** - after dragging this will be fired, before mouse_button_up
                * **mouse_button_up((int, int) pos, int button, int mods)** - mouse button up as in pygame
                * **mouse_button_down((int, int) pos, int btns, int mod)** - mouse button down
                * **key_down(event.key, event.mod, event.unicode)** - same as in pygame key down event
                * **key_up(event.key, event.mod)** - same as in pygame key up event
                * **joy_axis_motion(event.joy, event.axis, event.value)** - same arguments as for the pygame event
                * **joy_ball_motion(event.joy, event.ball, event.rel)** - same arguments as for the pygame event
                * **joy_hat_motion(event.joy, event.hat, event.value)** - same arguments as for the pygame event
                * **joy_button_up(event.joy, event.button)** - same arguments as for the pygame event
                * **joy_button_down(event.joy, event.button)** - same arguments as for the pygame event
                * **quit(`Application` self)** - quit event has the app as parameter
                * **active_event(event.state, event.gain)** - same arguments as for the pygame event
                * **mouse_enter((int, int) pos)** - the mouse enter event (extracted from active_event), position is not that precise
                * **mouse_leave((int, int) pos)** - the mouse leave event (extracted from active_event), position is not that precise
                * **activate()** - got focus
                * **deactivate()** - lost focus
                * **video_resize((int, int) size, int w, int h)** - new size of window
                * **video_expose()** - event signaling to redraw
                * **unknown(event)** - any other event, also userevents
        
        screen_mouse : `ScreenMouse`
            The mouse of this state
        game_time : `GameTime`
            Time and scheduler for this state
        the_app : `Application`
            the_app is a reference to the application and is set just before 
            the call to on_init of this state.
    """
    def __init__(self, *args, **kwargs):
        u"""
        Initialize the state. It registers two event handler:
         - on_quit: reacts on a quit signal, pops a state
         - on_key_down: reacts on key presses: escape to quit and F3 to take a screenshot
         
        Those event handlers can be overwriten.
        Initialize the data in on_init().

         """
        # TODO: convert to read only property? hmmm performance...
        if __debug__: print 'State __init__'
        self.events = pyknic.events.SignalProvider()
        if __debug__: print 'State __init__ SignalProvider done'
        self.screen_mouse = pyknic.gui.mouse.ScreenMouse(self)
        if __debug__: print 'State __init__ ScreenMouse done'
        self.game_time = pyknic.timing.GameTime()
        if __debug__: print 'State __init__ GameTime done'
        self.events.quit += self.on_quit
        self.events.key_down += self.on_key_down
        self.the_app = None
        if __debug__: print 'State __init__ done'

    #--- state handling ---#
    def on_init(self, *args, **kwargs):
        u"""
        Called once before the state is actually used.
        Normally the data should be initialized in here.
        self.the_app.state points already to this state when this method
        is called (so you can use it). 
        """
        pass

    def on_exit(self, *args, **kwargs):
        u"""Last call before state is dropped from the app."""
        pass

    def on_pause(self, *args, **kwargs):
        u"""If another state is pushed on top this is called to allert it 
        should pause."""
        pass

    def on_resume(self, *args, **kwargs):
        u"""If the the upper state is pop, this state is reactivated and this
        is called."""
        pass

    #--- per frame updates ---#
#    def update(self, gdt, gt, dt, t, *args, **kwargs):
#        u"""This will be called automatically every frame by the app.
#        :arguments:
#        
#            dt: time used in last frame in [s]
#            t: current time of the app in [s] (has some error because spikes are filtered out).
#        """
#        # TODO: if a simulation is needed ten the simulation should run at a
#        # constant framerate higher than the actual screen refresh... 
#        # maybe better to do it in the state!!
#        pass
#
#    def render(self, get_surface=pygame.display.get_surface, flip=pygame.display.flip):
#        u"""This will be called automatically every frame by the app.
#        Render your data to screen in here."""
#        pass

    #-- default event handlers --#
    def on_key_down(self, key, mod, unicode):
        u"""Default event handler for key presses.
         - escape: pops this state
         - F3: take a screenshot
        
        """
        if pygame.K_ESCAPE == key:
            self.on_quit()
        elif pygame.K_F3 == key:
            pyknic.utilities.take_screenshot(self.the_app.config['paths']['screenshots'])

    def on_quit(self, *args, **kwargs):
        u"""Default event handler for the quit event.
        Pops the current state."""
        self.the_app.pop_state()

#-------------------------------------------------------------------------------

if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))



