#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Event handling and helper classes.

:Variables:
    HANDLED : Constant
        Constant to return when a event handler wants to prevent further processing.
    UNHANDLED : Constant
        Optional return value when a event does not want to interrupt event processing.

"""

__version__ = '$Id: events.py 198 2009-07-12 16:37:11Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import warnings
from new import instancemethod as new_instancemethod
from weakref import ref

import pyknic.utilities


class SignalProvider(object):
    u"""
    Signal provider provides `Signal` on request.
    
    It automatically makes a `Signal` instance and save it 
    under the requested name. A name is requested in two ways::
    
        events = SignalProvider()
        # just as attribut access
        signal1 = events.name_to_be_requested
        # or as dict lookup
        signal2 = events['name_to_be_requested']
        signal1 == signal2 # True
    
    :Warning: 
        Watch out for typo's (misspelled name wont give an error just a new
        `Signal` instance.
    
    :Note:
        If this proves to be to error prone a registration interface
        will be added in future.
    
    """

    def __getattr__(self, name):
        # if it is already set then this isnt called
        if __debug__:
            pyknic.utilities.DLOG('creating Signal: %s' %(name))
        ## change this lines for weakreference signals
#        sig = WeakSignal(name)
        sig = Signal(name)
        setattr(self, name, sig)
        return sig

    def __getitem__(self, name):
        sig = self.__dict__.get(name, None)
        if sig:
            return sig
        return self.__getattr__(name)

    def __str__(self):
        return '<SignalProvider%s at %s >' %(str(self.__dict__.keys()), hex(id(self)))


#-------------------------------------------------------------------------------

HANDLED = True
UNHANDLED = False

class Signal(object):
    u"""
    A signal object. It is for event dispatching. It saves a list of
    observers and when fired, it calls the observers. The handler method
    has to accept the exact same number of arguments that are given to 
    the fire method. Or it should make use of the args and kwargs arguments.
    The return type of a handler is important. When returning True or any value 
    that evaluates to True in a if statement, the signal stops calling further 
    observers. Returning False or None (as default behavior of methods without a
    return), it will call further handler methods.
    
    The order in which the handler methods will be called can be defined when
    the signal is instanciated. The sort order can only have one of these values:
    
     * Signal.`NEW_FIRST`
     * Signal.`NEW_LAST`
    
    
    Default is NEW_FIRST. This means that handlers added later are called before 
    the older ones::
    
       s = Signal()
       s.add(handler1)
       s.add(handler2)
       s.fire() # call order: handler2, handler1
        
    This is important and useful, when imitating a push behavior. If handler2 
    returns a `UNHANDLED` then handler1 wont get be called.
    
    Using the `NEW_LAST` order for event handler leads to this::
     
       s = Signal()
       s.add(handler1)
       s.add(handler2)
       s.fire() # call order: handler1, handler2
     
    This is useful for a draw event. A convinient way to draw is in a back to 
    front manner. Adding first the background and then the other things on top 
    will draw the things in the correct order.
    
    This Signal implementation is iteration safe. It is possible to remove 
    the handler from within the handler without getting in trouble.
    
    :Warning:
        Any class that has a method added will be kept alive by this reference. 
        To allow the class to die it has to remove the handler. See `WeakSignal`
        for a implementation using weak references.
    
    :Ivariables:
        name : string
            Either the string that was given or None.
    
    :Cvariables:
        NEW_FIRST : int
            Used to define the call order. New handlers are added in front of 
            the others and therefore called before the others.
        NEW_LAST : int
            Used to define the call order. New handlers are appended and therefore
            called after the others.
        
    """

    _ADD, _RMV, _CLR = range(3)
    NEW_FIRST = 0
    NEW_LAST = -1


    def __init__(self, name=None, sort_order = None):
        u"""
        Constructor.
        
        :Parameters:
            name : string
                Optional. A name to identify the signal easier when debugging.
            sort_order : Constant
                Either Signal.NEW_FIRST or Signal.NEW_LAST. Defines the order in 
                which the handler are called.
        
        """
        if name:
            self.name = name
        else:
            self.name = hex(id(self))
        self._observers = []
        self._sort_oder = self.NEW_FIRST
        if sort_order:
            self._sort_oder = sort_order
        self._changed = False
        self._commands = []

    def add(self, obs):
        u"""
        Adds a handler to the signal.
       
        :Note:
            Shortcut::
            
                sig += obs
        
        :Parameters:
            obs : callable
                A handler to add, has to be callable.
        """
        self._changed = True
        self._commands.append((self._ADD, obs))
        return self

    def remove(self, obs):
        u"""
        Removes a handler.
        
        :Note:
            Shortcut::
            
                sig -= obs
        
        :Parameters:
            obs : callable
                The handler to be removed.
        """
        self._changed = True
        self._commands.append((self._RMV, obs))
        return self

    def fire(self, *args, **kwargs):
        u"""
        Fires the signal with any arguments.
        
        :Note:
            Shortcut::
            
                sig(*args, **kwargs)
        
        :Parameters:
            args : args
                Arguments list.
            kwargs : kwargs
                Named arguments, a dict.
        
        :rtype: True when a handler returns `HANDLED` , else False
        """
        if self._changed:
            self._sync()
        for obs in self._observers:
            if obs(*args, **kwargs):
                return True
        return False

    def clear(self):
        u"""
        Removes all handlers from the signal.
        """
        self._commands.append((self._CLR, []))

    def _sync(self):
        self._changed = False
        while self._commands:
            cmd, obs = self._commands.pop(0)
            if cmd == self._ADD and obs not in self._observers:
                self._observers.insert(self._sort_oder, obs)
            elif cmd == self._RMV:
                if obs in self._observers:
                    self._observers.remove(obs)
            elif cmd == self._CLR:
                self._observers = []
                self._commands = []
                

    def __str__(self):
        return '<%s(\'%s\') at %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    # convinients
    __iadd__ = add
    __isub__ = remove
    __call__ = fire

#-------------------------------------------------------------------------------

class WeakMethodRef(object):
    u"""
    It is a wrapper class to hold a weak reference to a bound method. 
    It acts exactly the same way as the weakref.ref class.
    """

    def __init__(self, method):
        u"""
        Save the method we want to hold a reference.
        
        :Parameters:
            method : callable
                A class method which should referenced weakly.
        """
        super(WeakMethodRef, self).__init__()
        self._inst = ref(method.im_self)
        self._func = method.im_func

    def __call__(self):
        u"""
        If you call the object return either the method/function object or
        None if it has died. Arguments are ignored.
        """
        inst = self._inst()
        if inst:
            return new_instancemethod(self._func, inst, inst.__class__)
        return None

    def __eq__(self, other):
        u"""
        equal operator, two instances are equal if for the bound method the 
        instances and the method objects are equal. Returns True or False.
        """
        return (self._inst() == other._inst() and self._func == other._func)

    def __ne__(self, other):
        u""" returns not self.__eq__(other)"""
        return not self.__eq__(other)

    def __str__(self):
        inst = self._inst()
        if inst:
            return '<%s->%s.%s(...) >'%(self.__class__.__name__, inst.__class__.__name__, self._func.__name__)
        else:
            return '<%s->\'dead\'>' %(self.__class__.__name__)
#-------------------------------------------------------------------------------

class WeakSignal(Signal):
    u"""
    A signal implementation that uses weak references. It has some overhead and 
    is therefor slower than `Signal`. It has the advantage that it does not 
    hold any object alive only because it is added. It uses the `WeakMethodRef` 
    to store references to methods of a class (because the class methods are 
    actually thin wrapper that dies using normal ref). Funtions are saved using 
    the normal ref.
    
    Behavior is the same as in `Signal`.
    
    :Warning:
        Might have some preformance impact.
    """
    def fire(self, *args, **kwargs):
        if self._changed:
            self._sync()
        for obs in self._observers:
            func = obs()
            if func:
               if func(*args, **kwargs):
                    return True
            else:
                self._commands.append((self._RMV, obs))
                self._changed = True

    def _sync(self):
        self._changed = False
        while self._commands:
            cmd, obs = self._commands.pop(0)
            if cmd == self._ADD:
                if hasattr(obs, 'im_self') and obs.im_self:
                    # bound method
                    obs = WeakMethodRef(obs)
                else:
                    # unbound function
                    obs = ref(obs)
                if obs not in self._observers:
                    self._observers.insert(self._sort_oder, obs)
            elif cmd == self._RMV:
                if not isinstance(obs, WeakMethodRef):
                    obs = WeakMethodRef(obs)
                for idx, obs2 in enumerate(self._observers):
                    if obs == obs2:
                        self._observers.remove(obs2)
                        break
            elif cmd == self._CLR:
                self._observers = []
                self._commands = []

    # convinients
    __call__ = fire

#-------------------------------------------------------------------------------


if __name__ == '__main__':
    
    def f1(*args, **kwargs):
        print 'f1', args, kwargs
    
    def f2(*args, **kwargs):
        print 'f2', args, kwargs
    
    e = Signal()
    e += f1
    e += f2
    
    e('first call')

    e -= f1
    e('second call')

    sp = SignalProvider()
    
    sig = sp.new_sig
    
    sig2 = sp['new_sig2']
    
    print 'sig', sig == sp['new_sig']
    print 'sig2', sig2 == sp.new_sig2
    
    print sp
    print e
    print sp.new_sig

if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))

