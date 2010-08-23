#!/usr/bin/python
# -*- coding: utf-8 -*-

u"""
Here are time related classes.
"""

__version__ = '$Id: timing.py 198 2009-07-12 16:37:11Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import warnings
from bisect import insort
from time import time


from events import Signal

#-------------------------------------------------------------------------------

class GameTime(object):
    u"""
    GameTime allows you to manipulate the virtual time in the game. You can
    slow down or speed up the time in your game. Also you can pause any time
    dependent code by setting the dilatation factor to 0. Tying to set a
    negative factor value will raise a NegativeFactorException.
    Each call to update will fire the (public) 'event_update' with the
    arguments: gdt, gt, dt, t
    (game delta time, game time, real delta time, real time)
   
    Through the attribute time the starttime can be set and the current
    gametime can be read (both in [s]).
   
    GameTime provides also a scheduler part, in which functions can
    be scheduled to be called later. The scheduler takes time dilatation
    into account. The scheduler part does not work if blocking mode is used
    in gamebase (and the clock part isnt that usefull then). Use the Scheduler
    class if a working scheduler even in blocking mode.
    
    :Ivariables:
        time : int
            game time in [s] since start, can be read and written
        event_update : Signal
            update event that is fired every time update is called,
            it passes gdt, gt, dt and t as parameters e.g.: on_update(gdt, gt, dt, t)
    
    """
   
    SCHEDULE_STOP = True
    SCHEDULE_AGAIN = False
   
    def __init__(self, *args, **kwargs):
        u"""
        Init the GameTime with tick_speed=1.0.
        """
        super(GameTime, self).__init__(*args, **kwargs)
        # clock attributes
        self._factor = 1.0
        self.time = 0
        self.event_update = Signal(u"gametime event_update") # update(gdt, gt, dt, t)
        # scheduling attributes
        self._tasks = [] # [(gt, (f, arg, kwargs)), ]
        self._unschedule_func = None

    def _set_factor(self, factor):
        u"""
        For use in the factor property only. You get a warning when setting a
        negative value, but it is permitted.
       
        :Parameters:
            factor : float
              time dilatation factor, 0.0 pauses, negative values run the time
              backwards (scheduling does not work when running backwards).
        """
        if __debug__:
              if 0 > factor:
                warnings.warn(u'Using negative time factor!!')
        if 0 == factor:
            # TODO: raise exception
            self._factor = 0
        else:
            self._factor = factor

    tick_speed = property(lambda self: self._factor, _set_factor, doc=u'Set the \
dilatation factor, 0.0 pauses, negative raise a warning and let the time run \
backwards (scheduling does not work with negative values). Default value is 1.0 (realtime)')

    #-- scheduler methods --#

    def schedule(self, dt, func, *args, **kwargs):
        u"""
        Schedule a function with its arguments. It will be called once after
        the time specified by dt [s] and removed from scheduling.
       
        :Parameters:
            dt : float
                delta game time after which the func should be called in [s]
            func : function ref
                function to when its time has come and it should have 
                following signature: func(gdt, gt, dt, t)
            args : tuple
                arguments for the function call
            kwargs : dict
                keyword arguments of the function call
        """
        # schedule for later call
        t = self.time + dt
        # add task to the sorted list
        task = (t, (func, args, kwargs))
        if __debug__:
            if func != self._reschedule:
                for _task in [tsk for tsk in self._tasks if tsk[1][0] == func]:
                    warnings.warn(u'Already in scheduler: \n%s(%s, %s) interval: %d time: %d \n %s' %(func, args, kwargs, t, self.time, str(_task)))
        insort(self._tasks, task)

    def _reschedule(self, gdt, gt, dt, t, *args, **kwargs):
        u"""
        Internal use only. Used for re-scheduling functions to implement
        schedule_repeated.
        """
        interval, old_t, skip, func, eargs = args
        # call callback
        self._unschedule_func = None
        stop = func(self.gdt, self.time, dt, t, *eargs, **kwargs) or func == self._unschedule_func
        if not stop:
            nt = old_t + interval - self.time
            if skip:
                while nt <= 0:
                    nt += interval
            self.schedule(nt, self._reschedule, interval, self.time+interval, skip, func, eargs, **kwargs)

    def schedule_repeated(self, interval, func, skip=False, *args, **kwargs):
        u"""
        The given function will be called repeatedly with the given time
        interval [s]. To stop the scheduling either call unschedule(func) or
        just return SCHEDULE_STOP from the function func.
       
        :Parameters:
            interval : float
                game time between each call in [s]
            func : func ref
                function that is called
            skip : bool
                if frames should be skipped
            args : tuple
                functions arguments
            kwargs : dict
                keyword arguments for func
        """
        self.schedule(interval, self._reschedule, interval, self.time + interval, skip, func, args, **kwargs)

    def unschedule(self, func):
        u"""
        Remove the function from any scheduling.
       
        :Parameters:
            func : function ref
                function to remove
        """
        self._unschedule_func = func
        # find and remove func from tasks (all occurences)
        self._tasks = [task for task in self._tasks if task[1][0] != func]
        # remove repeated tasks too
        remaining = []
        for task in self._tasks:
            if task[1][0] == self._reschedule:
                if task[1][1][2] != func:
                    remaining.append(task)
            else:
                remaining.append(task)
        self._tasks = remaining

    def clear(self):
        u"""
        Removes all tasks from the scheduler.
        """
        self._tasks = []

    def update(self, dt, real_t):
        u"""
        Should be called each frame to update the gametime.
        dt is the time passes in
        the last 'frame' and t should be the real time. It fires the
        event_update with the arguments: gdt, gt, dt, t
       
            gdt : float
                game delta time in [s]
            gt : float
                game time in [s] since start
            dt : int
                real delta time (same as input) in [s]
            real_t : int
                real time (same as input) in [s]
       
        :Parameters:
            dt : int
                real delta time (same as input) in [s]
            real_t : int
                real time (same as input) in [s]
       
        The gametime is only advanced if update is called.
       
        It also calls all scheduled functions if their time has come. The
        scheduled functions will be called in the correct order, but only
        with a time resolution equal to call to this update method (probably
        ~30 fps).
        """
        self.gdt = self._factor * dt
        self.time += self.gdt
        # fire event
        self.event_update(self.gdt, self.time, dt, real_t)
        # TODO: FIXME: not sure if this is good enough
        if self._factor:
            # call scheduled func if their time has come
            while self._tasks and self._tasks[0][0] <= self.time:
                t, fargs = self._tasks.pop(0)
                func, args, kwargs = fargs
                func(self.gdt, self.time, dt, real_t, *args, **kwargs)

    def create_timer(self):
        u"""
        returns an instance of Timer bound to this time scheduler.
        """
        return Timer(self)


#-------------------------------------------------------------------------------

# TODO: write a scheduler with higer precision (maybe using pygame timer)

class Timer(object):

    def __init__(self, scheduler):
        u"""
        scheduler is  GameTime scheduler to hook in.
        Timer is a nicer interface to the GameTime scheduler. Its
        precision is the same as for the GameTime, roughly the same
        time resolution as the fps.
        """
        self._scheduler = scheduler
        self.event_elapsed = Signal(u'Timer event_elapsed')
        self._interval = None
        self._auto_repeat = False
        self._enabled = True

    def _set_interval(self, value):
        if value <= 0:
            self.enabled = False
            raise Exception(u'intervall hast to be a positive integer')
        self._interval = value
    interval = property(lambda self: self._interval, _set_interval, doc=u'get/set a interval in [s], must be > 0 otherwise raises an Exception')

    def _set_auto_repeat(self, val):
        self._auto_repeat = val
    auto_repeat = property(lambda self: self._auto_repeat, _set_auto_repeat, doc=u'if True then it repeats')

    def _set_enabled(self, val):
        if val == True:
            if self._interval is None:
                raise Exception(u'interval not set!')
            self._scheduler.schedule(self._interval, self._on_callback)
        else:
            self._scheduler.unschedule(self._on_callback)
            self._enabled = val
    enabled = property(lambda self: self._enabled, _set_enabled, doc=u'start/stop raising elapsed events')

    def _on_callback(self):
        if self._enabled:
            self.event_elapsed()
            if self._auto_repeat:
                self._scheduler.schedule(self._interval, self._on_callback)

    def start(self):
        u"""same as setting enabled = True"""
        self.enabled = True

    def stop(self):
        u"""same as setting enabled = False"""
        self.enabled = False

if __debug__:
    _dt = time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))



