#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Collision detection helpers.

Collision detection is normally divided in a broad phase and a narrow phase.
In the broad phase the main focus is in eliminating unnessecary collision 
checks. The best way
to do that, is to know which entities should collide with which others. Simplest
way to achieve that is to define groups of entities. Then pairs of groups can 
be defined to be checked against each other. But this helpers do really only 
detect the collision but the collision response is very game dependent. 
Therefore in the narrow phase a tailored collision response function can be 
registered depending 
on the types of the entities. To have those features in a flexible way, 
the strategy pattern is used to define the broad and narrow phase of 
collision detection.

For the very simple cases there are also some collision function that 
can be used directly without using the `CollisionDetector`.


"""

__version__ = '$Id: collision.py 247 2009-07-31 17:02:25Z dr0iddr0id $'

if __debug__:
    import sys
    sys.stdout.write(u'%s loading ... \n' % (__name__))
    import time
    _start_time = time.time()

import pygame

#-------------------------------------------------------------------------------

PREVENT_OTHER_COL_RESPONSE = True

#-------------------------------------------------------------------------------

class ICollisionStrategy(object):
    u"""
    The interface for all collision strategies. It defines two methods that 
    needs to be implemented.
    """

    def check_broad(self, group_name1, group_name2, coll_groups):
        u"""
        This method should check the broad phase collisions and try to 
        eliminate as many as possible as quick as possible and returning 
        only the potential hits. It can be inaccurate, but should be fast.
        
        :Parameters:
            group_name1 : string
                name of the first group
            group_name2 : string
                name of the second group
            coll_groups : dict
                a dictionary of {name:group}
        
        :Returns:
            a list of tuples, like [(o1, o2),...]
            
        """
        raise NotImplementedError(u'override this in inherited class')

    def check_narrow(self, pairs_list, coll_funcs):
        u"""
        This method checks the narrow phase collisions.
        
        :Parameters:
            pairs_list : list tuples
                a list of tuples, the potentially colliding entities
            coll_funcs : dict
                the dict of {type_tuple:func}
                
        Iterating over the collision pairs and getting the types of it 
        can be used to get the collision function. This function the should 
        be called using the collision pairs. 
        """
        raise NotImplementedError(u'override this in inherited class')


#-------------------------------------------------------------------------------
class AABBCollisionStrategy(ICollisionStrategy):
    u"""
    An implementation for entites with a rect attribute.
    """

    def check_broad(self, name1, name2, coll_groups): # -> [[(o1, o2),...],...]
        # TODO: also different collition functions, e.g. radius
        return brute_force_rect(coll_groups[name1], coll_groups[name2])
                    

    def check_narrow(self, pairs_list, coll_funcs):
        _get = coll_funcs.get
        [_get((first.__class__, second.__class__), self._dummy_func)(first, second)\
                for first, second in pairs_list]

    def _dummy_func(self, a, b):
        # TODO: probably raise an exception since this collision is not registered
        print '_dummy_func(a, b): \n\ta=%s of type %s \n\tb=%s of type %s' % (a, a.__class__, b, b.__class__)
        if not a.collision_response(b):
            b.collision_response(a)

#-------------------------------------------------------------------------------
class BoundingRadiusStrategy(ICollisionStrategy):
    u"""
    An implementation for entities with a bounding_radius attribute.
    """

    def check_broad(self, name1, name2, coll_groups): # -> [[(o1, o2),...],...]
        return brute_force_radius(coll_groups[name1], coll_groups[name2])

    def check_narrow(self, pairs_list, coll_funcs):
        _get = coll_funcs.get
        [_get((first.__class__, second.__class__), self._dummy_func)(first, second)\
                for first, second in pairs_list]

    def _dummy_func(self, a, b):
        # TODO: probably raise an exception since this collision is not registered
        print '_dummy_func(a, b): \n\ta=%s of type %s \n\tb=%s of type %s' % (a, a.__class__, b, b.__class__)
        a.collision_response(b)
        b.collision_response(a)

#-------------------------------------------------------------------------------
class CollisionDetector(object):
    u"""
    CollisionDetector for detecting collisions between groups of entities.
    
    It has various methods to register all needed data.
    """

    def __init__(self):
        self._check_pairs = [] # [(group_name1, group_name2, coll_strategy)]
        self._groups = {}      # {name: group}
        self._funcs = {}       # {(type1, type2): func}

    def register_once(self, group_name1, group_name2, group1, group2, coll_strategy, type_tuple, func):
        u"""
        Convenience method to register just two groups. It will only check the 
        first group against the second. To register any other group combinations 
        the other register methods can be used.
        It does exactly that::
        
            self.register_group(group_name1, group1)
            self.register_group(group_name2, group2)
            self.register_pair(group_name1, group_name2, coll_strategy)
            self.register_narrow_func(type_tuple, func)        
        
        :Parameters:
            group_name1 : string
                name of the first group
            group_name2 : string
                name of the second group
            group1 : iterable
                group1, can be just a list or any iterable
            group2 : iterable
                group2, can be just a list or any iterable
            coll_strategy : ICollisionStrategy
                the collision strategy to use between those groups
            type_tuple : tuple
                the types of identifiers which collision function to use, 
                e.g. (Entity, Bullet)
            func : function or method
                function to check real collision, signature: def func(entity, bullet)
        """
        self.register_group(group_name1, group1)
        self.register_group(group_name2, group2)
        self.register_pair(group_name1, group_name2, coll_strategy)
        self.register_narrow_func(type_tuple, func)

    def register_pair(self, group_name1, group_name2, coll_strategy=AABBCollisionStrategy()):
        u"""
        Registers pairs of group names. Each entity from first 
        group will be checked against the entities from the second one.
        
        :Parameters:
            group_name1 : string
                name of first group
            group_name2 : string
                name of second group
                
        """
        self._check_pairs.append((group_name1, group_name2, coll_strategy))

    def remove_pair(self, group_name1, group_name2, coll_strategy=None):
        u"""
        Removes this collision pair.
        
        :Parameters:
            group_name1 : string
                name of first group
            group_name2 : string
                name of second group
                
        """
        if coll_strategy:
            pair = (group_name1, group_name2, coll_strategy)
            if pair in self._check_pairs:
                self._check_pairs.remove(pair)
        else:
            for name1, name2, coll_strategy in self._check_pairs:
                if name1 == group_name1 and name2 == group_name2:
                    self._check_pairs.remove((name1, name2, coll_strategy))
                    break

    def register_group(self, name, group_iterable):
        u"""
        Register a group under a name. The name should be the same as 
        used for the collision pairs in `register_pair`.
        
        :Parameters:
            name : string
                name of the group
            group_iterable : iterable
                any iterable containing entities (list, tuple, group, ...)
                
        """
        self._groups[name] = group_iterable

    def remove_group(self, name):
        u"""
        Removes a previously registered group by its name.
        """
        if name in self._groups:
            del self._groups[name]

    def register_narrow_func(self, type_tuple, func):
        u"""
        Registers a tuple of types to look up the collision function.
        
        :Parameters:
            type_tuple : tuple
                a tuple of type, normally (entity.__class__, bullet.__class__)
            func : function
                the collision function like: def func(entity, bullet)
                the objects passed in should be of types defined in the type_tuple
        
        """
        self._funcs[type_tuple] = func

    def remove_narrow_func(self, type_tuple):
        u"""
        Removes the collision function defined by its type_tuple.
        """
        if type_tuple in self._funcs:
            del self._funcs[type_tuple]

    def check(self):
        u"""
        Runs all collision checks.
        """
        self.check_narrow(self.check_broad())

    def check_broad(self):
        u"""
        Checks the brad phase of the collision detection.
        
        This calls the `check_broad` of the current strategy.
        
        :Returns:
            a list of lits of collision pairs, example: 
            [(strategy, [(o1,o2), (o1, o5)]), (strategy2, [(o3, 04)]), ...]
            
        """
        #return self.coll_strategy.check_broad(self._check_pairs, self._groups)
        _groups = self._groups
        return [(coll_strategy, coll_strategy.check_broad(name1, name2, _groups)) for name1, name2, coll_strategy in self._check_pairs]

    def check_narrow(self, pairs_list):
        u"""
        Checks collisions of the narrow phase.
        
        This calls the `check_narrow` of the current strategy and should call 
        back the registered narrow functions, but this depends
        on the strategy used.
        
        :Parameters:
            pairs_list : list of lists of tuples
                this is what you get from `check_broad`
                
        """
        _funcs = self._funcs
        for coll_strategy, pairs in pairs_list:
            coll_strategy.check_narrow(pairs, _funcs)


#-------------------------------------------------------------------------------
def brute_force_rect(objects1, objects2): # -> [(obj, obj), ()] list of colliding pairs
    u"""
    Brute force method. It compares all obj form objects1 to all objects of
    objects2. This has n^2 checks and scales very badly. Use with care.
    
    :Parameters:
        objects1 : list
            list of objects to check against objects2
        objects2 : list
            list of other objects
    
    :Returns:
        list of collision pairs, like [(obj1, obj2), (obj, obj),...]
    
    """
    # TODO: does this check perform a list comparison?? better way?
    if objects1 == objects2:
        # a O((n^2 - n) / 2) algorithm, fast for small number of objects
        return [(entity, objects1[idx+1+col_idx]) \
                    for idx, entity in enumerate(objects1) \
                    for col_idx in entity.rect.collidelistall(objects1[idx+1:])]
    else:
        return [(entity, objects2[idx]) \
                    for entity in objects1 \
                    for idx in entity.rect.collidelistall(objects2)]

#-------------------------------------------------------------------------------

def brute_force(objects1, objects2, collide_func): # -> [(obj, obj), ()] list of colliding pairs
    u"""
    This checks collision for each obj in first group agains each object of 
    the second group using the provided collide_func.
    
    :Parameters:
        objects1 : list
            list of objects to check against objects2
        objects2 : list
            list of other objects
        collide_func : function
            collision function with signature: func(obj1, obj2) -> bool
    
    :Returns:
        list of collision pairs, like [(obj1, obj2), (obj, obj),...]
    
    """
    if objects1 == objects2:
        # a O((n^2 - n) / 2) algorithm, fast for small number of objects
        return [(entity, other) \
                    for idx, entity in enumerate(objects1) \
                    for other in objects1[idx+1:] if collide_func(entity, other)]
    else:
        return [(entity, objects2[idx]) \
                    for entity in objects1 \
                    for other in objects2 if collide_func(entity, other)]

#-------------------------------------------------------------------------------

def brute_force_radius(objects1, objects2):
    u"""
    Same as `brute_force_rect` but using a bounding_radius instead. Entities
    should have an attribute bounding_radius.
    """
    if objects1 == objects2:
        # a O((n^2 - n) / 2) algorithm, fast for small number of objects
        return [(entity, other) \
                    for idx, entity in enumerate(objects1) \
                    for other in objects1[idx+1:] if (entity.position - other.position).lengthSQ < (entity.bounding_radius + other.bounding_radius) * (entity.bounding_radius + other.bounding_radius)]
    else:
        return [(entity, objects2[idx]) \
                    for entity in objects1 \
                    for other in objects2 if (entity.position - other.position).lengthSQ < (entity.bounding_radius + other.bounding_radius) * (entity.bounding_radius + other.bounding_radius)]

#-------------------------------------------------------------------------------

# RDC = Recursive Dimensional Clustering

_BGN, _END = range(2)
XAXIS, YAXIS, INVALIDAXIS = range(3)

def rdc_rect(objects, axis=XAXIS, min_num=10):
    u"""
    A faster collision detection algorithm. It is based on the 
    Recursive Dimensional Clusterting, hence the rdc in the name.
    This is an n * log(n) in average, but worst case is still a n^2 algorithm.
    This one is implemented for a rect. The objects need an rect attribute.
    
    :Parameters:
        objects : list
            list of objects that should be checked against each other.
        axis : _*AXIS
            a axis constant, default starts with the x-axis (normally wider)
        min_num : int
            if a group contains less than the min_num objects then a brute force
            algorithme is applied
    
    :Returns:
        a list of collision paris.
    
    """
    pairs = []
    accum = [(objects, axis)]
    while accum:
        objects, axis = accum.pop(0)
        if len(objects) <= min_num or axis == INVALIDAXIS:
            pairs.extend(brute_force_rect(objects, objects))
        else:
            # find bounds
            assert axis < INVALIDAXIS and axis >= 0
            if axis == XAXIS:
                bounds = [(obj.rect.left, _BGN, obj) for obj in objects]
                bounds.extend([(obj.rect.right, _END, obj) for obj in objects])
            elif axis == YAXIS:
                bounds = [(obj.rect.top, _BGN, obj) for obj in objects]
                bounds.extend([(obj.rect.bottom, _END, obj) for obj in objects])
            bounds.sort()
            axis = INVALIDAXIS
            # find subgroups
            count = 0
            _group = []
            for bound in bounds:
                pos, closure, obj = bound
                if closure == _BGN:
                    count += 1
                    _group.append(obj)
                else:
                    count -= 1
                    if count == 0:
                        if bound != bounds[-1]:
                            if axis == XAXIS:
                                axis = YAXIS
                            else:
                                axis = XAXIS
                        accum.append((_group, axis))
                        _group = []
            assert count == 0
    return pairs

#-------------------------------------------------------------------------------
def rdc_radius(objects, axis=XAXIS, min_num=10):
    u"""
    Same as the `rdc_rect` but just for a bounding radius.
    The objects need a bounding_radius attribute.
    
    """
    pairs = []
    accum = [(objects, axis)]
    while accum:
        objects, axis = accum.pop(0)
        if len(objects) <= min_num or axis == INVALIDAXIS:
            pairs.extend(brute_force_radius(objects, objects))
        else:
            # find bounds
            assert axis < INVALIDAXIS and axis >= 0
            if axis == XAXIS:
                bounds = [(obj.position.x - obj.bounding_radius, _BGN, obj) for obj in objects]
                bounds.extend([(obj.position.x + obj.bounding_radius, _END, obj) for obj in objects])
            elif axis == YAXIS:
                bounds = [(obj.position.y - obj.bounding_radius, _BGN, obj) for obj in objects]
                bounds.extend([(obj.position.y + obj.bounding_radius, _END, obj) for obj in objects])
            bounds.sort()
            axis = INVALIDAXIS
            # find subgroups
            count = 0
            _group = []
            for bound in bounds:
                pos, closure, obj = bound
                if closure == _BGN:
                    count += 1
                    _group.append(obj)
                else:
                    count -= 1
                    if count == 0:
                        if bound != bounds[-1]:
                            if axis == XAXIS:
                                axis = YAXIS
                            else:
                                axis = XAXIS
                        accum.append((_group, axis))
                        _group = []
            assert count == 0
    return pairs
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    # some test classes
    R = pygame.Rect
    
    class A(object):
        def __init__(self, rect, vx, vy):
            self.rect = rect
            self.vx = vx
            self.vy = vy
        def __repr__(self):
            return '%s %s' %(self.rect, hex(id(self)))
        def collision_response(self, *args):
            print 'response', args
        def update(self):
            if self.rect.centerx > 1600 or self.rect.centerx < 0:
                self.vx = -self.vx
            if self.rect.centery > 800 or self.rect.centery < 0:
                self.vy = -self.vy
            self.rect.move_ip(self.vx, self.vy)
    
#    def f1(a, b):
#        print 'f1', a, b
#    
#    # some object to collide
#    a = A(R(0,0,30,30))
#    a3 = A(R(0,0,1,1))
#    a2 = A(R(100,100,1,1))
#    a4 = A(R(10,10,1,1))
#    r1 = (0,0,1,1)
#    r2 = (20,20,1,1)
#    
#    # collision detector
#    d = CollisionDetector()
#    
#    # define some groups
#    d.register_group('1', [a, a2, a4, a3])
#    d.register_group('2', [r1, r2])
#
#    # define which group should collide with other
#    d.register_pair('1', '2')
#    d.register_pair('1', '1')
#    
#    # define specialized callback
#    d.register_narrow_func((a.__class__,r1.__class__), f1)
#    
#    # check collisions
#    pairs = d.check_broad()
#    
#    print pairs
#    d.check_narrow(pairs)
    
    from random import randint
    g = []
    for i in range(500):
        g.append(A(R(randint(0, 1600), randint(0, 1000), randint(5, 25), randint(5,25)), randint(-10, 10), randint(-10, 10)))
    import time

    
    
    
    screen = pygame.display.set_mode((1600,1000))
    running = True
    draw_rect = pygame.draw.rect
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                running = False
        [obj.update() for obj in g]


        start = time.time()
        b = brute_force_rect(g, g)
        delta = time.time() - start
        print 'brute_force_rect', delta

        start = time.time()
        c = rdc_rect(g)
        delta = time.time() - start
        print 'rdc_rect        ', delta, '\n'

#        start = time.time()
#        d = rdc(g)
#        delta = time.time() - start
#        print delta, '\n==========='

#        pygame.event.wait()
        screen.fill((0,0,0))
        for r in g:
            draw_rect(screen, (128,128,128), r, 1)
        for t in b:
            for r in t:
                draw_rect(screen, (255,0,0), r.rect.inflate(-2, -2), 1)
        for t in c:
            for r in t:
                draw_rect(screen, (255,255,0), r.rect.inflate(-4, -4), 1)
#        for t in d:
#            for r in t:
#                draw_rect(screen, (0,0,255), r.rect.inflate(2, 2), 1)
        pygame.display.flip()


if __debug__:
    _dt = time.time() - _start_time
    sys.stdout.write(u'%s loaded: %fs \n' % (__name__, _dt))



